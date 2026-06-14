import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from src.ingest import load_data
from src.features import engineer_event_features

def run_isolation_forest(df):
    features = ['sensitivity_score', 'action_risk', 'time_risk', 'privilege_score', 
            'hour', 'is_failed', 'inactivity_risk', 'is_new_hire', 'unauthorized_access']

    X = df[features].fillna(0)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = IsolationForest(
        contamination=0.46,
        random_state=42,
        n_estimators=200
    )

    df['if_anomaly'] = model.fit_predict(X_scaled)
    df['if_score'] = model.score_samples(X_scaled)
    df['if_anomaly_flag'] = df['if_anomaly'] == -1

    return df, model

def apply_rules(df):
    df['rule_flags'] = 0

    df.loc[(df['is_night']) &
           (df['action'] == 'export_data') &
           (df['sensitivity_score'] == 3), 'rule_flags'] += 3

    df.loc[(df['is_night']) &
           (df['action'] == 'admin_operation'), 'rule_flags'] += 2

    df.loc[(df['sensitivity_score'] == 3) &
           (df['time_risk'] >= 2), 'rule_flags'] += 2

    df.loc[(df['privilege_level'] == 'service-account') &
           (df['action'] == 'export_data'), 'rule_flags'] += 2

    return df

if __name__ == "__main__":
    df = load_data()
    df = engineer_event_features(df)
    df, model = run_isolation_forest(df)
    df = apply_rules(df)

    print("Anomaly counts (IF):")
    print(df['if_anomaly_flag'].value_counts())

    print("\nRule flag distribution:")
    print(df['rule_flags'].value_counts())

    df.to_csv('outputs/detected.csv', index=False)
    print("\nSaved outputs/detected.csv")