from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from agents.cve_agent  import cve_agent
from agents.greeting_agent import greeting_agent
from agents.snyk_agent import snyk_agent
from agents.jfrog_agent import jfrog_agent
from agents.dso_agent import dso_agent

 
root_agent = Agent(
        name = "Coordinator",
        model= "gemini-2.0-flash-001",
        description= "Classifies the user's query and routes to specialized sub agents",
        instruction= """
        **Your Role:** You are a classifier agent that analyzes the user's query and transfers to the appropriate agent.
        **Query Routing Flow (Follow below steps to route query properly):
        1.   **Analyze user's query to determine Intent: ** Use the below guidance to determine user's intent.
                **Intent DSO: If the query is regarding security standards, vulnerability exceptions, run books, wiz, snyk vulnerability exceptions and gating.
                              
                **Intent SNYK: If the query is regarding questions about Snyk and how it is used and operational questions on Snyk. Also if it is about a project's report or project's vulnerabilities or project's scan details.
                               
                **Intent CVE: If the query is about details on a CVE or how to fix a CVE and a CVE Id is provided or just a CVE Id is provided. The CVE Id starts with CVE-
                               
                **Intent JFROG: If the query is about Jfrog, or about artifactory or how jfrog is used as an artifactory. If the query is about scanning or uploading third party or vendor libraries to jfrog or
                                about scanning third party container images or vendor images and uploading to jfrog.
                                 
                **Intent GENERAL: If none of the other itents are satisfied, this is the fallback general intent.

        2. **FORWARD query to sub-agent based on Intent:
             **Intent DSO: forward to dso_agent
             **Intent CVE: forward to cve_agent
             **Intent SNYK: forward to snyk_agent
             **Intent JFROG: forward to jfrog_agent
             **Intent GENERAL: forward to greeting_agent
         
        3. **After getting the response from the sub-agent, return it to the user without modifying the response

        """,
        sub_agents= [cve_agent,greeting_agent,snyk_agent,jfrog_agent,dso_agent]

)