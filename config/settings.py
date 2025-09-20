import os
import logging
from dotenv import load_dotenv
load_dotenv() # Load environment variables from a .env file. This is crucial for keeping sensitive data like API keys out of your main codebase.
# Suppress most ADK internal logs to keep the console clean during Streamlit runs.
# You can change this to logging.INFO or logging.DEBUG for more verbose output during debugging.
logging.basicConfig(level=logging.ERROR) 
MODEL_GEMINI = "gemini-2.0-flash" 
APP_NAME_FOR_ADK = "Sora"  
USER_ID = "u008240"  
INITIAL_STATE = ""
MESSAGE_HISTORY_KEY = "messages_final_mem_v2"  
ADK_SESSION_KEY = "adk_session_id"  
 