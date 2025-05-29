ANSWER_PROMPT_TEMPLATE = """
You are a Magic: The Gathering expert. Use only the following context (from decklists, rulebooks, and card descriptions) to answer the user's question.

{context}

---

Answer this question clearly and helpfully:
{question}
"""

QUERY_REWRITE_PROMPT = """
Rewrite the following Magic: The Gathering question to include specific keywords such as deck archetypes, card names, formats, and colors. 
Make it more suitable for vector search in a rulebook and article database.

Original question:
{question}

Optimized query:
"""
