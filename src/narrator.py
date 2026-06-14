import os
import json
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_API_KEY")
)

def generate_narrative(row):
    prompt = f"""
You are a security analyst at a bank. Analyze this data access event and generate a concise investigation narrative.

USER ID: {row.get('user_id')} | Dept: {row.get('department','N/A')} | Role: {row.get('job_title','N/A')} | Privilege: {row.get('privilege_level','N/A')}
EVENT: {row.get('action')} on {row.get('resource')} ({row.get('resource_sensitivity')} sensitivity)
TIME: {row.get('timestamp')} ({row.get('time_classification')})
RISK SCORE: {row.get('risk_score'):.1f}/100
DAYS INACTIVE: {row.get('days_inactive','N/A')}

Return ONLY a JSON object, no markdown formatting, no extra text:
{{
  "summary": "one sentence explaining why this is suspicious",
  "anomalies": ["anomaly 1", "anomaly 2", "anomaly 3"],
  "business_context": "any legitimate explanation that should be considered",
  "recommendation": "BLOCK or INVESTIGATE or MONITOR",
  "confidence": 0.0
}}
"""
    response = client.chat.completions.create(
        model="nvidia/llama-3.1-nemotron-nano-8b-v1",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,
        temperature=0.1
    )

    text = response.choices[0].message.content.strip()
    # remove markdown code fences if present
    text = text.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(text)
    except:
        return {"summary": text, "anomalies": [], "business_context": "", "recommendation": "INVESTIGATE", "confidence": 0.5}

if __name__ == "__main__":
    df = pd.read_csv('outputs/scored_events.csv')

    # only generate narratives for top 25 riskiest events (save API credits)
    top_alerts = df.sort_values('risk_score', ascending=False).head(25).copy()

    alerts = []
    for idx, row in top_alerts.iterrows():
        print(f"Generating narrative for event {idx}...")
        narrative = generate_narrative(row)
        alert_dict = row.to_dict()
        alert_dict['narrative'] = narrative
        alerts.append(alert_dict)

    output = {
        "metadata": {
            "total_events": len(df),
            "critical_count": int((df['severity']=='CRITICAL').sum()),
            "high_count": int((df['severity']=='HIGH').sum()),
            "users_at_risk": int(df[df['severity']=='CRITICAL']['user_id'].nunique())
        },
        "alerts": alerts
    }

    with open('outputs/alerts.json', 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\nSaved {len(alerts)} narratives to outputs/alerts.json")