from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

greeting_agent = Agent(
    name = "greeting_agent",
    model = LiteLlm("gemini-2.0-flash-lite"),
    description="A greeting agent",
    instruction= """
    You are a greeting agent. Respond with a polite greeting.
    """
)