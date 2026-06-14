import pandas as pd
import json

def compute_user_risk(df):
    user_risk = df.groupby('user_id').agg(
        avg_risk_score=('risk_score', 'mean'),
        max_risk_score=('risk_score', 'max'),
        total_events=('action', 'count'),
        night_access_count=('is_night', 'sum'),
        export_count=('action', lambda x: (x == 'export_data').sum()),
        critical_count=('severity', lambda x: (x == 'CRITICAL').sum()),
        high_count=('severity', lambda x: (x == 'HIGH').sum()),
    ).reset_index()

    # pull in user profile info
    users = pd.read_csv('data/user_profiles.csv')
    user_risk = user_risk.merge(users, on='user_id', how='left')

    # privilege score
    priv_map = {'user': 1, 'power-user': 2, 'service-account': 3, 'admin': 4}
    user_risk['privilege_score'] = user_risk['privilege_level'].map(priv_map).fillna(1)

    # compute user-level risk score 0-100
    max_avg = user_risk['avg_risk_score'].max()
    max_exports = user_risk['export_count'].max() if user_risk['export_count'].max() > 0 else 1
    max_nights = user_risk['night_access_count'].max() if user_risk['night_access_count'].max() > 0 else 1

    user_risk['user_risk_score'] = (
        (user_risk['avg_risk_score'] / max_avg) * 0.4 +
        (user_risk['export_count'] / max_exports) * 0.3 +
        (user_risk['night_access_count'] / max_nights) * 0.2 +
        (user_risk['privilege_score'] / 4) * 0.1
    ) * 100

    user_risk['user_severity'] = pd.cut(
        user_risk['user_risk_score'],
        bins=[-1, 40, 65, 85, 101],
        labels=['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
    )

    return user_risk

if __name__ == "__main__":
    df = pd.read_csv('outputs/scored_events.csv')
    user_risk = compute_user_risk(df)

    print("User risk distribution:")
    print(user_risk['user_severity'].value_counts())
    print("\nTop 10 riskiest users:")
    print(user_risk.sort_values('user_risk_score', ascending=False)[
        ['user_id','user_risk_score','user_severity','export_count','night_access_count','privilege_level']
    ].head(10))

    user_risk.to_csv('outputs/user_risk.csv', index=False)
    print("\nSaved outputs/user_risk.csv")