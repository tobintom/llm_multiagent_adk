import streamlit as st
import asyncio
import vertexai
from adk._adkapp import app, call_agent_async,runner
import nest_asyncio


st.set_page_config(page_title=" Chat Agent", layout="centered") # Configures the browser tab title and page layout.
st.title(" - Security Chat Bot") # Main title of the app.
st.caption(" is an AESTM chatbot to help answer security questions") # Descriptive text.
# st.divider()
# st.divider()
# st.subheader("Chat with ")

with st.sidebar:
    st.title("")
    st.write(" can ask questions")
    st.info("Ask questions to ")

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt:= st.chat_input("Ask .."):
    st.session_state.chat_history.append({"role":"user","content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        

    with st.chat_message("assistant"):
        with st.spinner("Thinking.."):
            try:
                response_text = asyncio.run(call_agent_async(prompt,runner))
            except Exception as e:
                response_text = f"Error {e}"
        
        st.markdown(response_text)
    st.session_state.chat_history.append({"role":"assistant","content":response_text})

    



# query = st.text_input("Question" , value="Ask ..")

# if st.button("Ask "):
#     if not query.strip():
#         st.warning("Please enter a question")
#     else:
#         with st.spinner("Talking to the agent.."):
#             try:
#                 response_text = asyncio.run(call_agent_async(query,runner))
#             except Exception as e:
#                 response_text = f"Error : {e}"
#         st.subheader("Agent Response")
#         st.write(response_text)










# nest_asyncio.apply()
# print("JIIII")
# vertexai.init(project="digital-poc-security-eng",location="us-east4")

# """
# Sets up and runs the Streamlit web application for the ADK chat assistant.
# """
# st.set_page_config(page_title=" Chat Agent", layout="wide") # Configures the browser tab title and page layout.
# st.title(" - Security Chat Bot") # Main title of the app.
# st.markdown(" is an AESTM chatbot to help answer security questions") # Descriptive text.
# st.divider() # A visual separator.
#     # api_key = get_api_key() # Retrieve the API key from settings.
#     # if not api_key:
#     #     st.error("⚠️ Action Required: Google API Key Not Found or Invalid! Please set GOOGLE_API_KEY in your .env file. ⚠️")
#     #     st.stop() # Stop the application if the API key is missing, prompting the user for action.
#     # Initialize ADK runner and session ID (cached to run only once).
# #adk_runner, current_session_id = initialize_adk()
    
# st.divider()
# st.subheader("Chat with ") # Subheading for the chat section.

# with st.sidebar:
#     st.title("")
#     st.write(" can ask questions related to AESTM")
#     st.info("Ask questions to ")

# if "messages" not in st.session_state:
#     st.session_state.messages = []
# if "adk_session_id" not in st.session_state:
#     st.session_state.adk_session_id = None
# if "user_id" not in st.session_state:
#     st.session_state.user_id = "streamlit_user"

# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# async def init_session():
#     if st.session_state.adk_session_id is None:
#         session = await app.async_create_session(user_id=st.session_state.user_id)
#         st.session_state.adk_session_id = session.id
#         st.rerun()

# def response_generator(user_id, session_id, message):
#     loop = asyncio.get_event_loop()
#     async_iter = app.async_stream_query(
#         user_id = user_id,
#         session_id = session_id,
#         message = message
#     ).__aiter__()
#     while True:
#         try:
#             event = loop.run_until_complete(anext(async_iter))
#             if hasattr(event, 'content') and event.content:
#                 print(f"CCCCOOOOO {event.content}")
#                 yield event.content
#         except StopAsyncIteration:
#             break

# if prompt := st.chat_input("Ask .."):
#     st.session_state.messages.append({"role" : "user", "content" : prompt})
#     with st.chat_message("user"):
#         st.markdown(prompt)

#     asyncio.run(init_session())

#     with st.chat_message("assistant"):
#         message_placeholder = st.empty()
#         full_response = ""
#         for chunk in response_generator(st.session_state.user_id,st.session_state.adk_session_id, prompt):
#             full_response += chunk
#             message_placeholder.markdown(full_response + " ")
#         message_placeholder.markdown(full_response)
    
#     st.session_state.messages.append({"role":"assistant","content":full_response})


# if st.sidebar.button("Clear Chat"):
#     st.session_state.messages = []
#     st.session_state.adk_session_id = None
#     st.rerun()

#     # Initialize chat message history in Streamlit's session state if it doesn't exist.
#     # if MESSAGE_HISTORY_KEY not in st.session_state:
#     #     st.session_state[MESSAGE_HISTORY_KEY] = []
#     # # Display existing chat messages from the session state.
#     # for message in st.session_state[MESSAGE_HISTORY_KEY]:
#     #     with st.chat_message(message["role"]): # Use Streamlit's chat message container for styling.
#     #         st.markdown(message["content"])
#     # # Handle new user input.
#     # if prompt := st.chat_input("Ask .."):
#     #     # Append user's message to history and display it.
#     #     st.session_state[MESSAGE_HISTORY_KEY].append({"role": "user", "content": prompt})
#     #     with st.chat_message("user"):
#     #         st.markdown(prompt)
#     #     # Process the user's message with the ADK agent and display the response.
#     #     with st.chat_message("assistant"):
#     #         message_placeholder = st.empty() # Create an empty placeholder to update with the assistant's response.
#     #         with st.spinner("Assistant is thinking..."): # Show a spinner while the agent processes the request.
#     #             print("PROCESSING CHAT MESSAGE")
#     #             agent_response = run_adk_sync(adk_runner, current_session_id, prompt) # Call the synchronous ADK runner.
#     #             message_placeholder.markdown(agent_response) # Update the placeholder with the final response.
        
#     #     # Append assistant's response to history.

#     #     st.session_state[MESSAGE_HISTORY_KEY].append({"role": "assistant", "content": agent_response})
