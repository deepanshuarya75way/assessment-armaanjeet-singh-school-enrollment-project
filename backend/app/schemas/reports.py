from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, computed_field
from app.models.school import CategoryEnum
from app.schemas.school import SchoolResponse as SchoolOut
from typing import Optional

class GenerateReportRequest(BaseModel):
    report_month: date
class AIReportQueryRequest(BaseModel):
    session_id : str
    question: str
    target_date : date
class AIReportQueryResponse(BaseModel):
    answer: str
class ReportDataResponse(BaseModel):
    id: int
    school_id: int
    class_: int | str
    category: CategoryEnum | None

    boys: int
    girls: int
    below_6: int
    between_6_and_11: int
    above_11: int
    school: Optional[SchoolOut] = None

    # 2. Automatically compute 'school_name' from 'school.name'
    @computed_field
    def school_name(self) -> str:
        if self.school and self.school.name:
            return self.school.name
        return f"School #{self.school_id}"


    model_config = ConfigDict(from_attributes=True)


class ReportResponse(BaseModel):
    id: int
    report_month: date
    generated_at: datetime
    status: str = "END"

    model_config = ConfigDict(from_attributes=True)


class ReportDetailResponse(ReportResponse):
    data: list[ReportDataResponse] = []