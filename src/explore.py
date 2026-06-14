import pandas as pd

logs = pd.read_csv('data/data_access_logs.csv')
users = pd.read_csv('data/user_profiles.csv')

print("=== LOGS ===")
print(logs.shape)
print(logs.columns.tolist())
print(logs.head())

print("\n=== USERS ===")
print(users.shape)
print(users.columns.tolist())
print(users.head())

print("\n=== LOGS VALUE COUNTS ===")
print(logs['action'].value_counts())
print(logs['time_classification'].value_counts())
print(logs['resource_sensitivity'].value_counts())