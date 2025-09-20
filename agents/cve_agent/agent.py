from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
import requests
import json


def fetch_cve_details(cve_id: str)-> str:
    """
    Retrieves the details of a CVE using the CVE ID

    Parameters:
    - cve_id (str): The CVE ID used to get CVE vulnerability details from NVD using REST API

    Returns:
    - JSON service payload with vulnerability details

    Use this tool when the user asks about a particular cve and provides a cve id
    """

    url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={cve_id}"
    try:
        r = requests.get(url,timeout=20)
        r.raise_for_status()
        data = r.json()
        items = data.get("vulnerabilities",[])
        if not items:
            return json.dumps({"error":f"No details found for cve {cve_id}"})
        out = []
        for entry in items:
            cve = entry.get("cve",{})
            descs = entry.get("descriptions",[])
            desc = None
            if descs:
                en = [d['value'] for d in descs if d.get('lang' ,'en')=='en']
                desc = en[0] if en else descs[0]['value']
            metrics = cve.get('metrics' , {})
            severity = None
            if 'cvssMetricV31' in metrics:
                severity = metrics['cvssMetricV31'][0]['cvssData'].get('baseSeverity')
            out.append({
                "id": cve.get('id'),
                "description" : desc,
                "severity": severity
            })
        return json.dumps({"cve_details":items}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error":str(e)})


cve_agent = Agent(
    name = "cve_agent",
    model = LiteLlm("gemini-2.0-flash-lite"),
    description="Finds CVE related information",
    instruction= """
    If the query is not about CVE or security vulnerability or a cve fix, route back to the coordinator to find the appropriate agent.
    You are a security expert and will return valid information about a CVE security vulnerability or a query about how to fix a cve, based on a given CVE
    using the fetch_cve_details CVE tool. The cve id usually starts with cve, so look for a cve id by looking for a cve id that thats with cve.
    Give full details on the CVE, vulnerability details, severity and complete remediation steps in a well structured manner with a section for each which is easy to read.
    """,
    tools=[fetch_cve_details]
    
)
