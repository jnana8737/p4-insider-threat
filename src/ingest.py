import pandas as pd

def load_data():
    logs = pd.read_csv('data/data_access_logs.csv', parse_dates=['timestamp'])
    users = pd.read_csv('data/user_profiles.csv')

    # parse hire_date and last_login if they exist
    for col in ['hire_date', 'last_login']:
        if col in users.columns:
            users[col] = pd.to_datetime(users[col], errors='coerce')

    # time-based features
    logs['hour'] = logs['timestamp'].dt.hour
    logs['day_of_week'] = logs['timestamp'].dt.dayofweek
    logs['is_weekend'] = logs['day_of_week'] >= 5
    logs['is_night'] = logs['hour'].between(0, 6)

    # merge logs with user profiles
    df = logs.merge(users, on='user_id', how='left', suffixes=('', '_profile'))

    return df

if __name__ == "__main__":
    df = load_data()
    print(df.shape)
    print(df.columns.tolist())
    print(df.head())
    df.to_csv('outputs/merged.csv', index=False)
    print("\nSaved to outputs/merged.csv")