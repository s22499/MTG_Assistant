import os
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from src.prompts.prompt_templates import QUERY_REWRITE_PROMPT, ANSWER_PROMPT_TEMPLATE


class LLMService:
    def __init__(self):
        self.api_key = os.environ["OPENAI_API_KEY_TEG"]
        self.model = ChatOpenAI(api_key=self.api_key)

    def refine_query(self, question):
        prompt_template = ChatPromptTemplate.from_template(QUERY_REWRITE_PROMPT)
        prompt = prompt_template.format(question=question)
        return self.model.predict(prompt)

    def generate_answer(self, context, question):
        prompt_template = ChatPromptTemplate.from_template(ANSWER_PROMPT_TEMPLATE)
        prompt = prompt_template.format(context=context, question=question)
        return self.model.predict(prompt)
