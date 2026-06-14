import time
import subprocess

start = time.time()

import pandas as pd
from src.ingest import load_data
from src.features import engineer_event_features
from src.detector import run_isolation_forest, apply_rules
from src.scorer import compute_risk_score

df = load_data()
df = engineer_event_features(df)
df, model = run_isolation_forest(df)
df = apply_rules(df)
df = compute_risk_score(df)

end = time.time()
print(f"Pipeline completed in {end - start:.2f} seconds")
print(f"Events processed: {len(df)}")
print(f"Rate: {len(df)/(end-start):.0f} events/second")