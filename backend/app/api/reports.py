# app/routers/reports.py
from datetime import date, datetime, timedelta 
from typing import Annotated
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from app.database import SessionDep
from sqlalchemy import select, delete
from app.dependencies.user import get_current_user
from app.models.users import User
from app.schemas.reports import ReportResponse, ReportDetailResponse, GenerateReportRequest, AIReportQueryRequest, AIReportQueryResponse
from app.services.report_service import ReportService
from app.services.analytics_service import AnalyticsService
from app.services.ai_service import AIService
from app.models.chats import ChatMessage 

router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)

@router.post("/generate", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def generate_report(
    payload: GenerateReportRequest,
    db: SessionDep,
    user: Annotated[User, Depends(get_current_user)]
):
    service = ReportService(db)
    return await service.generate_report(
        user_id=user.id,
        report_month=payload.report_month
    )

@router.get("", response_model=list[ReportResponse])
async def get_my_reports(
    db: SessionDep,
    user: Annotated[User, Depends(get_current_user)]
):
    service = ReportService(db)
    return await service.get_my_reports(user_id=user.id)

@router.get("/{report_id}", response_model=ReportDetailResponse)
async def get_report(
    report_id: int,
    db: SessionDep,
    user: Annotated[User, Depends(get_current_user)]
):
    service = ReportService(db)
    report = await service.get_report(user_id=user.id, report_id=report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

@router.put("/{report_id}/refresh", response_model=ReportDetailResponse)
async def refresh_report(
    report_id: int,
    db: SessionDep,
    user: Annotated[User, Depends(get_current_user)]
):
    service = ReportService(db)
    return await service.refresh_report(user_id=user.id, report_id=report_id)

@router.post("/{report_id}/finalize", response_model=ReportResponse)
async def finalize_report(
    report_id: int,
    db: SessionDep,
    user: Annotated[User, Depends(get_current_user)]
):
    service = ReportService(db)
    return await service.finalize_report(user_id=user.id, report_id=report_id)



@router.post("/ai-query", response_model=AIReportQueryResponse)
async def query_reports_with_ai(
    payload: AIReportQueryRequest,
    db: SessionDep,
    user: Annotated[User, Depends(get_current_user)]
):
    now = datetime.utcnow()
    analytics = AnalyticsService(db)
    comparison_metrics = await analytics.get_schools_monthly_comparison(user.id, payload.target_date)
    
    # Delete any old expired messages for this session
    clean_stmt = delete(ChatMessage).where(
        ChatMessage.session_id == payload.session_id,
        ChatMessage.expires_at < now
    )
    await db.execute(clean_stmt)

    # Fetch active, unexpired history logs ordered by creation time
    stmt = (
        select(ChatMessage)
        .where(ChatMessage.session_id == payload.session_id, ChatMessage.user_id == user.id)
        .order_by(ChatMessage.created_at.asc())
    )
    result = await db.execute(stmt)
    db_messages = result.scalars().all()
    
    # Convert DB instances to standard payload dictionaries required by Groq
    session_history = [{"role": msg.role, "content": msg.content} for msg in db_messages]

    # all Groq via your updated AIService
    ai = AIService()
    answer, updated_history = await ai.answer_report_question(
        question=payload.question, 
        metrics=comparison_metrics,
        session_history=session_history
    )
    
    # Set expiration to 30 minutes from right now
    new_expiration_time = now + timedelta(minutes=30)
    
    # 5. Extract the newest user query and AI answer from the returned window
    new_turns = updated_history[-2:]
    for turn in new_turns:
        db.add(
            ChatMessage(
                session_id=payload.session_id,
                user_id=user.id,
                role=turn["role"],
                content=turn["content"],
                expires_at=new_expiration_time
            )
        )
    
    # Commit changes cleanly to the database
    await db.commit()

    return {"answer": answer}
