from dotenv import load_dotenv
import os
import streamlit as st
import asyncio
from agents import Runner, Agent

# run this script with `streamlit run simple_chat.py`

load_dotenv()

api_key = os.environ.get("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables")

if "messages" not in st.session_state:
    st.session_state.messages = []

agent = Agent(
    name="Chat Assistant",
    instructions="You are a helpful and friendly assistant. Respond concisely to user queries.",
)

st.title("Chat with GPT-4o")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("You:", key="user_input")
    submit_button = st.form_submit_button(label="Send")

if submit_button and user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    async def get_response():
        result = await Runner.run(agent, input=st.session_state.messages)
        return result

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(get_response())

    assistant_response = result.final_output
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})

    st.rerun()
if st.button("New Chat"):
    st.write("Starting a new chat...")
    st.session_state.messages = []
    st.rerun()