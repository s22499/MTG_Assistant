import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from services.llm_service import LLMService

load_dotenv()


def test_refine_query():
    llm = LLMService()
    
    user_question = "How can I make black deck cards with discard?"
    
    print("\nOriginal question:")
    print(user_question)
    
    print("\nGenerating 4 candidate rewrites...")
    candidates = [llm.refine_query(user_question, temperature=0.9) for _ in range(4)]
    
    for i, c in enumerate(candidates, 1):
        print(f"\nCandidate {i}:\n{c}")
    
    print("\nChoosing best candidate using LLM...")
    best = llm.choose_best_query(user_question, candidates)
    
    print("\nFinal chosen query:")
    print(best)


if __name__ == "__main__":
    test_refine_query()
