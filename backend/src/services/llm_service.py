import os
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from src.prompts.prompt_templates import QUERY_REWRITE_PROMPT, ANSWER_PROMPT_TEMPLATE
from src.services.chromadb_service import ChromaDBService


class LLMService:
    def __init__(self):
        self.api_key = os.environ["OPENAI_API_KEY_TEG"]
        self.model = ChatOpenAI(api_key=self.api_key)
    
    def refine_query(self, question, temperature=0.7):
        prompt_template = ChatPromptTemplate.from_template(QUERY_REWRITE_PROMPT)
        prompt = prompt_template.format(question=question)
        model = ChatOpenAI(api_key=self.api_key, temperature=temperature)
        return model.predict(prompt)
    
    def generate_answer(self, context, question):
        prompt_template = ChatPromptTemplate.from_template(ANSWER_PROMPT_TEMPLATE)
        prompt = prompt_template.format(context=context, question=question)
        return self.model.predict(prompt)
    
    def choose_best_query(self, question, candidates):
        prompt = f"""
            You are a Magic: The Gathering expert helping optimize search queries.
            
            The original user question was:
            "{question}"
            
            Here are 4 optimized query candidates:
            
            1. {candidates[0]}
            2. {candidates[1]}
            3. {candidates[2]}
            4. {candidates[3]}
            
            Pick the **single best** query that is most useful for searching a database of MTG articles and rulebooks.
            Only output the best version, no explanation. """
        return self.model.predict(prompt).strip()
    
    def run_rag_pipeline(self, user_query: str) -> dict:
        chroma = ChromaDBService()
        
        candidates = [self.refine_query(user_query, temperature=0.9) for _ in range(4)]
        best_query = self.choose_best_query(user_query, candidates)

        collections_to_query = ["Articles", "Cards"]
        all_results = []

        for name in collections_to_query:
            collection = chroma.get_collection(name)
            results = collection.similarity_search(best_query, k=5)
            all_results.extend(results)

        context = "\n".join([doc.page_content for doc in all_results])
        answer = self.generate_answer(context, user_query)
        
        return {
            "original_question": user_query,
            "refined_candidates": candidates,
            "best_query": best_query,
            "response": answer,
        }
    
