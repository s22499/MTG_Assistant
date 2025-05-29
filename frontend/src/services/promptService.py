import requests

class PromptService:
    def __init__(self, api_url: str=""):
        self.api_url = api_url

    def get_answer(self, prompt: str) -> str:
        """
        Sends a prompt to the API and returns the response.
        """
        
        try:
            response = requests.post(
                f"{self.api_url}/",
                json={"prompt": prompt}
            )
            response.raise_for_status()
            return response.json().get("answer", "")
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to get answer from API: {e}")
        
    
    def mock_get_answer(self, prompt: str) -> str:
        """
        Mocks the API response by returning a fixed text.
        """
        return f"Mocked answer for prompt: {prompt}"
