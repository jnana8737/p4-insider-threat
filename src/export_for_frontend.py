import pandas as pd
import json

df = pd.read_csv('outputs/scored_events.csv')

with open('outputs/alerts.json') as f:
    alerts_data = json.load(f)

# severity counts
severity_counts = df['severity'].value_counts().to_dict()

# all events (lightweight, for the timeline chart)
events_cols = [c for c in ['timestamp','user_id','action','resource','severity','risk_score','time_classification'] if c in df.columns]
all_events = df[events_cols].to_dict(orient='records')

export = {
    "metadata": alerts_data['metadata'],
    "severity_counts": severity_counts,
    "all_events": all_events,
    "alerts": alerts_data['alerts']
}

with open('outputs/dashboard_data.json', 'w') as f:
    json.dump(export, f, indent=2, default=str)

print("Saved outputs/dashboard_data.json")
print(f"Total events: {len(all_events)}, Alerts with narratives: {len(alerts_data['alerts'])}")