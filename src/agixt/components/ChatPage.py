import os
from AGiXT import AGiXT
from Config import Config
from Config.Agent import Agent

CFG = Config()


class ChatPage:
    def __init__(self, st):
        st.header("Chat with Agent")

        agent_name = st.selectbox(
            "Select Agent",
            options=[""] + [agent["name"] for agent in CFG.get_agents()],
            index=0,
        )

        smart_chat_toggle = st.checkbox("Enable Smart Chat")

        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = {}

        chat_container = st.container()

        if agent_name:
            learn_file_upload = st.file_uploader("Upload a file to learn from")
            learn_file_path = ""
            if learn_file_upload is not None:
                if not os.path.exists(os.path.join("data", "uploaded_files")):
                    os.makedirs(os.path.join("data", "uploaded_files"))
                learn_file_path = os.path.join(
                    "data", "uploaded_files", learn_file_upload.name
                )
                with open(learn_file_path, "wb") as f:
                    f.write(learn_file_upload.getbuffer())

            try:
                chat_history = Agent(agent_name).get_chat_history(agent_name)
            except:
                chat_history = []
            st.session_state.chat_history[agent_name] = chat_history

            self.render_chat_history(
                chat_container, st.session_state.chat_history[agent_name], st
            )

            chat_prompt = st.text_input("Enter your message", key="chat_prompt")
            send_button = st.button("Send Message")

            if send_button:
                if agent_name and chat_prompt:
                    with st.spinner("Thinking, please wait..."):
                        agent = AGiXT(agent_name)
                        if smart_chat_toggle:
                            response = agent.smart_chat(
                                chat_prompt,
                                shots=3,
                                async_exec=True,
                                learn_file=learn_file_path,
                            )
                        else:
                            response = agent.run(
                                chat_prompt,
                                prompt="Chat",
                                context_results=6,
                                learn_file=learn_file_path,
                            )
                    chat_entry = [
                        {"sender": "User", "message": chat_prompt},
                        {"sender": "Agent", "message": response},
                    ]
                    st.session_state.chat_history[agent_name].extend(chat_entry)
                    self.render_chat_history(
                        chat_container, st.session_state.chat_history[agent_name], st
                    )
                else:
                    st.error("Agent name and message are required.")
        else:
            st.warning("Please select an agent to start chatting.")

    def render_chat_history(self, chat_container, chat_history, st):
        chat_container.empty()
        with chat_container:
            for chat in chat_history:
                if "sender" in chat and "message" in chat:
                    if chat["sender"] == "User":
                        st.markdown(
                            f'<div style="text-align: left; margin-bottom: 5px;"><strong>User:</strong> {chat["message"]}</div>',
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            f'<div style="text-align: left; margin-bottom: 5px;"><strong>Agent:</strong> {chat["message"]}</div>',
                            unsafe_allow_html=True,
                        )