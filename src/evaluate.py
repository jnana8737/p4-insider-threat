import pandas as pd
from sklearn.metrics import classification_report, precision_score, recall_score, f1_score

df = pd.read_csv('outputs/scored_events.csv')

y_true = df['if_anomaly_flag'].astype(int)

THRESHOLD = 30
y_pred = (df['risk_score'] > THRESHOLD).astype(int)

print("=== Final Evaluation Report (Threshold=30) ===")
print(classification_report(y_true, y_pred, target_names=['Normal','Anomaly']))
print(f"Precision: {precision_score(y_true, y_pred):.2%}")
print(f"Recall:    {recall_score(y_true, y_pred):.2%}")
print(f"F1 Score:  {f1_score(y_true, y_pred):.2f}")
print(f"\nAlerts flagged: {y_pred.sum()} out of {len(y_pred)} events")