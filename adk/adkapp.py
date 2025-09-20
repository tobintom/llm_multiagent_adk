import streamlit as st
import asyncio
import time
import os
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types as genai_types
from vertexai.agent_engines import AdkApp
from classifier_agent.agent import root_agent
from config.settings import APP_NAME_FOR_ADK, USER_ID, INITIAL_STATE, ADK_SESSION_KEY

def session_service_builder():
    return InMemorySessionService()

app = AdkApp(
    agent=root_agent,
    session_service_builder=session_service_builder
)

session_service = InMemorySessionService()
runner = Runner(agent=root_agent, app_name=APP_NAME_FOR_ADK, session_service=session_service)

async def call_agent_async(query: str, runner: Runner, user_id: str = USER_ID, session_id: str = "session-1") -> str:
    content = genai_types.Content(role="user", parts=[genai_types.Part(text=query)])

    await session_service.create_session(app_name= APP_NAME_FOR_ADK, user_id=user_id, session_id=session_id)

    events = runner.run_async(user_id=user_id, session_id=session_id, new_message=content)

    final_text = ""

    async for event in events:
        try:
            if event.is_final_response():
                final_text = event.content.parts[0].text
        except Exception:
            print("exception")
            pass
    return final_text