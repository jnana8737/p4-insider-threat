import pandas as pd
import json

df = pd.read_csv('outputs/scored_events.csv')
with open('outputs/alerts.json') as f:
    alerts_data = json.load(f)

# top 20 by risk score
top20 = df.sort_values('risk_score', ascending=False).head(20)

with open('outputs/flagged_accesses.md', 'w') as f:
    f.write("# Flagged Access Events — Top 20 Threats\n\n")
    for i, (_, row) in enumerate(top20.iterrows(), 1):
        f.write(f"## Alert {i}: {row['user_id']} — {row['action']}\n")
        f.write(f"- **Resource:** {row.get('resource','N/A')}\n")
        f.write(f"- **Sensitivity:** {row.get('resource_sensitivity','N/A')}\n")
        f.write(f"- **Time:** {row.get('timestamp','N/A')} ({row.get('time_classification','N/A')})\n")
        f.write(f"- **Risk Score:** {row['risk_score']:.1f}/100\n")
        f.write(f"- **Severity:** {row['severity']}\n\n")

print("Saved outputs/flagged_accesses.md")