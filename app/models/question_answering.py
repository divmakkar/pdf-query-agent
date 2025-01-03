# app/models/question_answering.py

from app.utils.config import Config
from app.utils.logger import get_logger
from anthropic import Anthropic


logger = get_logger(__name__)


class QuestionAnswering:
    def __init__(self):
        self.api_key = Config.ANTHROPIC_API_KEY
        self.answer_model = Config.ANSWER_MODEL
        self.summary_model = Config.SUMMARY_MODEL
        self.client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)

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
        # logger.info(f"Prompt to the system is {prompt}")

        try:
            response = self.client.messages.create(
                max_tokens=512,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.answer_model,
            )
            answer = response.content[0].text
            return answer
        except Exception as e:
            logger.error(f"Error getting answer from LLM : {e}")
            raise e

    def get_summary(self, text):
        prompt = f"Summarize the following text:\n\n{text}\n\nSummary:"

        try:
            response = self.client.messages.create(
                max_tokens=512,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.summary_model,
            )
            answer = response.content[0].text
            return answer
        except Exception as e:
            logger.error(f"Error getting answer from LLM : {e}")
            raise e
