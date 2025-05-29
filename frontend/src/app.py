import streamlit as st
from services.promptService import PromptService

class ChatbotApp:
    def __init__(self):
        st.set_page_config(
            page_title="MTG Assistant",
            layout="wide"
        )

        self.initialize_session_state();

        self.prompt_service = PromptService(api_url="http://data:8000")

    def initialize_session_state(self):
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

    def display_chat_messages(self):
        """Display all chat messages"""
        for message in st.session_state.messages:
            if message["role"] != "system":
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

    def handle_user_input(self):
        """Process user input and update chat messages."""
        # prompt = st.text_input("Enter your question here:")

        if prompt:= st.chat_input("Enter your question here:"):

            st.session_state.messages.append({
                "role": "user",
                "content": prompt
            })

            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                try:
                    stream = self.prompt_service.mock_get_answer("Prompt answer")

                    ## TODO: CHANGE TO STREAM
                    response = st.write(stream)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })
                except Exception as e:
                    st.error(f"Error: {e}")

    def run(self):
        self.display_sidebar()

        self.display_chat_messages()

        self.handle_user_input()

if __name__ == "__main__":
    app = ChatbotApp()
    app.run()