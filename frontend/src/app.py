import streamlit as st
from services.promptService import PromptService
import time
from uuid import uuid4


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
        
        if "chats" not in st.session_state:
            st.session_state.chats = {}
            self.create_new_chat()

        if not st.session_state.chats:
            self.create_new_chat()

        if "active_chat" not in st.session_state:
            st.session_state.active_chat = next(iter(st.session_state.chats))

    def create_new_chat(self):
        chat_id = str(uuid4())[:8]
        st.session_state.chats[chat_id] = {
            "name": f"Chat {len(st.session_state.chats) + 1}",
            "has_user_message": False,
            "last_updated": time.time(),
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that answers questions about Magic: The Gathering."
                }
            ]
        }

        st.session_state.active_chat = chat_id
        st.session_state.has_user_message = False

    def has_empty_chat(self):
        return any(not chat.get("has_user_message", False) for chat in st.session_state.chats.values())

    
    def display_sidebar(self):
        """Display the sidebar with the chat history and other options."""
        with st.sidebar:
            st.markdown("## MTG Assistant")
            st.markdown("### Chats")

            st.markdown(
                """
                <style>

                .stSidebar .stVerticalBlock>div:nth-child(4) button {
                    width: 100%;
                }

                .stSidebar .stHorizontalBlock {
                    position: relative;
                    height: 40px;
                }

                .stSidebar .stHorizontalBlock p {
                    text-align: left;
                }

                .stSidebar .stHorizontalBlock>.stColumn:first-child,
                .stSidebar .stHorizontalBlock>.stColumn:first-child button[kind="secondary"],
                .stSidebar .stHorizontalBlock>.stColumn:first-child div{
                    width: 100% !important; 
                }

                .stSidebar .stHorizontalBlock>.stColumn:not(:first-child) button[kind="secondary"] {
                    background-color: transparent;
                    border: 1px solid transparent;
                }

                .stSidebar .stHorizontalBlock>.stColumn:last-child {
                    position: absolute;
                    right: 12px;
                }

                </style>
                """,
                unsafe_allow_html=True
            )

            if st.button("New Chat"):
                if not self.has_empty_chat():
                    self.create_new_chat()
                    st.rerun()

            active_chat = st.session_state.active_chat

            sorted_chats = sorted(
                st.session_state.chats.items(),
                key=lambda item: item[1]["last_updated"],
                reverse=True
            )

            for chat_id, chat in sorted_chats:
                cols = st.columns([0.8, 0.2])

                with cols[0]:
                    if chat_id == active_chat:
                        st.markdown(
                            f"""
                            <div style="
                                background-color: #E0825C50;
                                color: 000000;
                                padding: 7px 12px;
                                border-radius: 0.75rem;
                                cursor: pointer;
                                width: fit-content;
                                border: 1px solid #E0825C;
                            ">
                            {chat["name"]}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    else:
                        if st.button(chat["name"], key=f"chat_{chat_id}"):

                            active_chat = st.session_state.active_chat

                            if active_chat in st.session_state.chats:
                                if not st.session_state.chats[active_chat].get("has_user_message", False):
                                    st.session_state.chats.pop(active_chat)

                            st.session_state.active_chat = chat_id
                            st.session_state.has_user_message = bool(chat.get("has_user_message", False))
                            st.rerun()

                with cols[1]:
                    if st.button("X", key=f"delete_{chat_id}"):
                        st.session_state.chats.pop(chat_id)
                        if active_chat == chat_id:
                            remaining_chats = list(st.session_state.chats.keys())
                            if remaining_chats:
                                st.session_state.active_chat = remaining_chats[0]
                            else:
                                self.create_new_chat()
                        st.rerun()

                

    
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
        chat_id = st.session_state.active_chat
        chat = st.session_state.chats[chat_id]

        st.markdown("""
            <style>
            .stMain .stChatMessage:nth-child(odd) {
                background-color: #2D2724 !important;
            }
            .stMain .stChatMessage:nth-child(even) {
                background-color: transparent !important;
            }
            </style>
        """, unsafe_allow_html=True)

        if not chat["has_user_message"]:
            self.display_empty_chat()
            
        for message in chat["messages"]:
            if message["role"] != "system":
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
    
    def handle_user_input(self):
        """Process user input and update chat messages."""
        
        if prompt := st.chat_input("Enter your question here:"):
            chat_id = st.session_state.active_chat
            chat = st.session_state.chats[chat_id]
            
            chat["messages"].append({
                "role": "user",
                "content": prompt
            })
            chat["has_user_message"] = True
            
            response = ""
            try:
                response = self.prompt_service.ask(prompt)
                
                chat["messages"].append({
                    "role": "assistant",
                    "content": response.strip()
                })
                chat["last_updated"] = time.time()

                st.rerun()
            
            except Exception as e:
                chat["messages"].append({
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
