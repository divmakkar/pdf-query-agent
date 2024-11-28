# app/models/question_answering.py

import openai
from app.utils.config import Config
from app.utils.logger import get_logger

# Rest of the code remains the same


logger = get_logger(__name__)


class QuestionAnswering:
    def __init__(self):
        openai.api_key = Config.OPENAI_API_KEY

    def get_answer(self, context, question):
        prompt = f"""
You are an AI assistant that answers questions based solely on the provided context.
If the answer is not in the context, reply "Data Not Available".

Context:
\"\"\"
{context}
\"\"\"

Question:
{question}

Answer:"""

        try:
            response = openai.chat.completions.create(
                model=Config.CHAT_MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
            )
            answer = response.choices[0].message.content.strip()
            return answer
        except Exception as e:
            logger.error(f"Error getting answer from OpenAI: {e}")
            raise e
