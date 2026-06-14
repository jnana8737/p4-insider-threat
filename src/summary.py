import pandas as pd

df = pd.read_csv('outputs/scored_events.csv')

print("=== OVERALL ===")
print(f"Total events: {len(df)}")
print(f"Anomalies flagged (IF): {df['if_anomaly_flag'].sum()}")
print(f"Anomaly rate: {df['if_anomaly_flag'].mean():.1%}")

print("\n=== SEVERITY BREAKDOWN ===")
print(df['severity'].value_counts())

print("\n=== TOP RISKY USERS ===")
top_users = df.groupby('user_id')['risk_score'].max().sort_values(ascending=False).head(10)
print(top_users)

print("\n=== ACTIONS IN CRITICAL/HIGH ALERTS ===")
high_risk = df[df['severity'].isin(['CRITICAL','HIGH'])]
print(high_risk['action'].value_counts())

print("\n=== TIME PATTERNS IN HIGH RISK ===")
print(high_risk['time_classification'].value_counts())