import pandas as pd
import numpy as np
from src.ingest import load_data
from src.features import engineer_event_features
from src.detector import run_isolation_forest, apply_rules

def compute_risk_score(df):
    # normalize IF score to 0-1 (lower if_score = more anomalous = higher risk)
    min_s, max_s = df['if_score'].min(), df['if_score'].max()
    if_normalized = 1 - (df['if_score'] - min_s) / (max_s - min_s)

    # normalize rule flags
    max_flag = df['rule_flags'].max()
    max_flag = max_flag if max_flag > 0 else 1
    rule_normalized = df['rule_flags'] / max_flag

    # new signals
    unauthorized = df['unauthorized_access'] if 'unauthorized_access' in df.columns else 0
    failed = df['is_failed'] if 'is_failed' in df.columns else 0
    inactivity = (df['inactivity_risk'] / 3) if 'inactivity_risk' in df.columns else 0
    new_hire = df['is_new_hire'] if 'is_new_hire' in df.columns else 0

    df['risk_score'] = (
        if_normalized * 0.35 +
        rule_normalized * 0.25 +
        (df['time_risk'] / 3) * 0.10 +
        (df['sensitivity_score'] / 3) * 0.10 +
        unauthorized * 0.10 +
        failed * 0.05 +
        inactivity * 0.05 +
        new_hire * 0.05 * (df['sensitivity_score'] / 3)
    ) * 100

    df['severity'] = pd.cut(
        df['risk_score'],
        bins=[-1, 35, 60, 80, 101],
        labels=['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
    )

    return df

if __name__ == "__main__":
    df = load_data()
    df = engineer_event_features(df)
    df, model = run_isolation_forest(df)
    df = apply_rules(df)
    df = compute_risk_score(df)

    print("Severity distribution:")
    print(df['severity'].value_counts())

    print("\nTop 10 riskiest events:")
    cols_to_show = ['user_id','action','resource','time_classification',
                    'risk_score','severity','is_failed','unauthorized_access']
    cols_to_show = [c for c in cols_to_show if c in df.columns]
    print(df.sort_values('risk_score', ascending=False)[cols_to_show].head(10))

    df.to_csv('outputs/scored_events.csv', index=False)
    print("\nSaved outputs/scored_events.csv")