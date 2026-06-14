import pandas as pd
from src.ingest import load_data

def engineer_event_features(df):
    # sensitivity score
    sensitivity_map = {'low': 1, 'medium': 2, 'high': 3, 'restricted': 4}
    df['sensitivity_score'] = df['resource_sensitivity'].map(sensitivity_map).fillna(1)

    # action risk
    action_risk = {
        'login': 1,
        'sql_query': 2,
        'file_access': 2,
        'api_call': 2,
        'admin_operation': 3,
        'export_data': 4
    }
    df['action_risk'] = df['action'].map(action_risk).fillna(1)

    # time risk
    time_risk = {
        'business_hours': 0,
        'unusual_hours': 1,
        'weekend': 2,
        'night': 3
    }
    df['time_risk'] = df['time_classification'].map(time_risk).fillna(0)

    # privilege score
    priv_map = {'user': 1, 'power-user': 2, 'service-account': 3, 'admin': 4}
    df['privilege_score'] = df['privilege_level'].map(priv_map).fillna(1)

    # NEW: failed access attempts
    if 'status' in df.columns:
        df['is_failed'] = (df['status'] == 'failure').astype(int)
    else:
        df['is_failed'] = 0

    # NEW: days inactive risk (higher inactivity = more suspicious when active)
    if 'days_inactive' in df.columns:
        df['inactivity_risk'] = pd.cut(
            df['days_inactive'],
            bins=[-1, 7, 20, 40, 999],
            labels=[0, 1, 2, 3]
        ).astype(float).fillna(0)
    else:
        df['inactivity_risk'] = 0

    # NEW: new hire risk (hired within 90 days + accessing sensitive data)
    if 'hire_date' in df.columns:
        df['hire_date'] = pd.to_datetime(df['hire_date'], errors='coerce')
        df['tenure_days'] = (pd.Timestamp.now() - df['hire_date']).dt.days
        df['is_new_hire'] = (df['tenure_days'] < 90).astype(int)
    else:
        df['is_new_hire'] = 0

    # NEW: unauthorized system access
    # check if resource is in user's approved systems_access
    if 'systems_access' in df.columns and 'resource' in df.columns:
        def check_unauthorized(row):
            approved = str(row.get('systems_access', '')).split('|')
            resource = str(row.get('resource', ''))
            # check if any approved system matches the resource
            return 0 if any(a.lower() in resource.lower() or resource.lower() in a.lower() 
                          for a in approved) else 1
        df['unauthorized_access'] = df.apply(check_unauthorized, axis=1)
    else:
        df['unauthorized_access'] = 0

    return df

def build_user_baselines(df):
    baseline = df.groupby('user_id').agg(
        avg_sensitivity=('sensitivity_score', 'mean'),
        avg_action_risk=('action_risk', 'mean'),
        typical_hour_mean=('hour', 'mean'),
        typical_hour_std=('hour', 'std'),
        night_access_rate=('is_night', 'mean'),
        export_rate=('action', lambda x: (x == 'export_data').mean()),
        total_events=('action', 'count'),
        unique_resources=('resource', 'nunique'),
        failure_rate=('is_failed', 'mean'),
        unauthorized_rate=('unauthorized_access', 'mean')
    ).reset_index()
    return baseline

if __name__ == "__main__":
    df = load_data()
    df = engineer_event_features(df)
    baseline = build_user_baselines(df)

    print("Feature sample:")
    print(df[['action','action_risk','sensitivity_score','time_risk',
              'privilege_score','is_failed','inactivity_risk',
              'is_new_hire','unauthorized_access']].head(10))
    print(f"\nFailed events: {df['is_failed'].sum()}")
    print(f"New hire events: {df['is_new_hire'].sum()}")
    print(f"Unauthorized access events: {df['unauthorized_access'].sum()}")

    df.to_csv('outputs/features.csv', index=False)
    baseline.to_csv('outputs/user_baselines.csv', index=False)
    print("\nSaved features.csv and user_baselines.csv")