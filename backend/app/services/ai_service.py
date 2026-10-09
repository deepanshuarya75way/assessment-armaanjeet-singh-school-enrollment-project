# app/services/ai_service.py
import json
from groq import AsyncGroq
from app.config import settings

class AIService:
    def __init__(self):
        self.client = AsyncGroq(api_key=settings.AI_API_KEY)

    # Update the method signature to accept an optional session_history list
    async def answer_report_question(
        self, question: str, metrics: list[dict], session_history: list[dict] = None
    ) -> tuple[str, list[dict]]:
        """
        Processes a report query using conversation context and returns a tuple:
        (ai_response_string, updated_history_list)
        """
        # Initialize history as an empty list if this is the very first turn
        if session_history is None:
            session_history = []

        system_prompt = (
            "You are an education intelligence system evaluating school enrollment performance.\n"
            "Analyze the provided JSON dataset of schools to answer the question directly.\n\n"
            "Answering Guidelines:\n"
            "1. Highest / Lowest Count: Explicitly name the schools with the highest and lowest `total_strength`.\n"
            "2. Growth & Decline: Reference `mom_trend` to show which schools increased or decreased.\n"
            "3. Dropout Analysis: Reference `critical_dropouts` to identify class transitions losing the most students.\n"
            "4. Keep the response concise, formatted in markdown bullets, and cite exact numbers.\n\n"
            f"Schools Dataset:\n{json.dumps(metrics, indent=2, default=str)}"
        )

        # 2. Build the messages array structure required by Groq:
        # System Prompt (Dataset) -> Prior Back-and-Forth History -> Current User Question
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(session_history)  # Injects previous [{'role': 'user', 'content': '...'}, ...]
        messages.append({"role": "user", "content": question})

        # Enforce supported model identifier
        model_name = getattr(settings, "AI_MODEL", None)
        if not model_name or "llama-3.3" in model_name:
            model_name = "llama-3.1-8b-instant"

        # 3. Request completion from Groq with the full conversational window
        response = await self.client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.1
        )

        ai_response = response.choices[0].message.content

        # 4. Append the current turn into our memory list before returning
        session_history.append({"role": "user", "content": question})
        session_history.append({"role": "assistant", "content": ai_response})

        # 5. Sliding optimization: Keep only the last 10 messages
        # This keeps the Groq API calls fast and prevents token usage from exploding
        if len(session_history) > 10:
            session_history = session_history[-10:]

        # 6. Return BOTH the raw string answer and the updated history list
        return ai_response, session_history
