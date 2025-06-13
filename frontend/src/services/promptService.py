import requests


class PromptService:
    def __init__(self, api_url: str = ""):
        self.api_url = api_url
    
    def refine_prompt(self, prompt: str) -> str:
        """
        Refines user front to better match vector store
        """
        
        try:
            response = requests.post(
                f"{self.api_url}/refine",
                json={"question": prompt}
            )
            response.raise_for_status()
            return response.json().get("refined_query", "")
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to get answer from API: {e}")
    
    def get_answer(self, question: str, context: str) -> str:
        try:
            response = requests.post(
                f"{self.api_url}/generate",
                json={"question": question, "context": context}
            )
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to get answer: {e}")

    def ask(self, prompt: str) -> str:
        try:
            response = requests.post(
                f"{self.api_url}/ask",
                json={"question": prompt}
            )
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to get full answer: {e}")
