import streamlit as st
from services.promptService import PromptService
import time


class ChatbotApp:
    def __init__(self):
        st.set_page_config(
            page_title="MTG Assistant",
            layout="wide"
        )
        
        self.initialize_session_state()
        
        self.prompt_service = PromptService(api_url="http://backend:4000")
    
    def initialize_session_state(self):
        if "is_streaming" not in st.session_state:
            st.session_state.is_streaming = False
        
        if "has_user_message" not in st.session_state:
            st.session_state.has_user_message = False
        
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that answers questions about Magic: The Gathering."
                }
            ]
    
    def display_sidebar(self):
        """Display the sidebar with the chat history and other options."""
        with st.sidebar:
            st.markdown("## MTG Assistant")
            st.markdown("### Chats")
            st.info("First chat")
    
    def display_empty_chat(self):
        st.title("MTG Assistant")
        st.write("Ask me anything about **Magic: The Gathering**!")
        
        st.markdown("### Example Prompts")
        
        example_prompts = [
            "What does the card *Lightning Bolt* do?",
        ]
        
        for prompt in example_prompts:
            st.markdown(f"- {prompt}")
    
    def display_chat_messages(self):
        """Display all chat messages"""
        if not st.session_state.has_user_message:
            self.display_empty_chat()
        
        for message in st.session_state.messages:
            if message["role"] != "system":
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
    
    def handle_user_input(self):
        """Process user input and update chat messages."""
        # prompt = st.text_input("Enter your question here:")
        
        if prompt := st.chat_input("Enter your question here:"):
            
            st.session_state.messages.append({
                "role": "user",
                "content": prompt
            })
            
            st.session_state.has_user_message = True
            
            response = ""
            try:
                response = self.prompt_service.ask(prompt)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response.strip()
                })
            
            except Exception as e:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Error: {e}"
                })
    
    def run(self):
        self.display_sidebar()
        
        self.handle_user_input()
        self.display_chat_messages()


if __name__ == "__main__":
    app = ChatbotApp()
    app.run()
