import os
from dotenv import load_dotenv
import google.generativeai as genai
import json
import re

load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_KEY:
    raise RuntimeError("GEMINI_API_KEY not set in environment")

# Configure the genai client
genai.configure(api_key=GEMINI_KEY)

# Choose a suitable Gemini model
MODEL = "gemini-2.0-flash"  # you can change this to another text generation model

def _call_gemini(prompt: str, max_output_tokens: int = 2048):
    model = genai.GenerativeModel(MODEL)

    response = model.generate_content(
        prompt,
        generation_config={
            "max_output_tokens": max_output_tokens
        }
    )

    # Always return text only
    try:
        if hasattr(response, "text") and response.text:
            return response.text.strip()

        if hasattr(response, "candidates"):
            return response.candidates[0].content.parts[0].text.strip()

    except Exception as e:
        print("ERROR extracting text:", e)

    return ""


def synthesize_research(company, web_results, news, wiki):
    parts = []
    parts.append(f"Company: {company}")

    if wiki:
        parts.append("Wikipedia summary:\n" + wiki)
    if news:
        parts.append("News:\n" + "\n".join([f"- {n['title']}: {n['description']}" for n in news]))
    if web_results:
        parts.append("Web snippets:\n" + "\n".join([f"- {r['title']}: {r['body']}" for r in web_results]))

    composite = "\n\n".join(parts)

    prompt = f"""
Extract the following from this company research dataset:

### Summary:
(Short company summary)

### Conflicts:
(List contradictions or mismatched information. If none, return "None")
    
Data:
{composite}
"""

    output = _call_gemini(prompt)
    if isinstance(output, dict):
        output = json.dumps(output, indent=2)

    summary = re.search(r"### Summary:\s*(.*?)(?=###|$)", output, re.DOTALL)
    conflicts = re.search(r"### Conflicts:\s*(.*?)(?=###|$)", output, re.DOTALL)

    summary_text = summary.group(1).strip() if summary else ""
    conflicts_text = conflicts.group(1).strip() if conflicts else ""

    # --- FIX: Convert conflicts to a list ---
    if conflicts_text.lower() == "none" or conflicts_text.strip() == "":
        conflicts_list = []
    else:
        conflicts_list = [
            line.lstrip("-• ").strip() 
            for line in conflicts_text.split("\n") 
            if line.strip()
        ]

    return summary_text, conflicts_list


def generate_account_plan(company, summary_text):
    prompt = f"""
Using the summary below, create a COMPLETE ACCOUNT PLAN for the company "{company}".

Return the output STRICTLY in the following JSON format (valid JSON only):

{{
  "Company Overview": "",
  "Key Stakeholders": "",
  "SWOT": "",
  "Market Position": "",
  "Opportunities": "",
  "Risks": "",
  "Recommended Next Steps": ""
}}

Summary:
{summary_text}

Make each field 3–6 sentences long. DO NOT include markdown, do not include headings outside JSON.
"""

    response = _call_gemini(prompt, max_output_tokens=3000)

    # Try to parse JSON
    try:
        plan_dict = json.loads(response)
        return plan_dict
    except json.JSONDecodeError:
        # If Gemini adds extra text, extract JSON using fallback
        import re
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            return json.loads(match.group())
        else:
            raise ValueError("Gemini did not return valid JSON")