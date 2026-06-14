import pandas as pd
import json

EXCEPTION_RULES = [
    {
        "condition": lambda row: row.get('privilege_level') == 'admin' and row.get('days_inactive', 0) < 7,
        "note": "Active admin account — elevated access is expected. Verify intent before blocking."
    },
    {
        "condition": lambda row: row.get('job_title', '').lower() in ['cto', 'ciso', 'vp', 'director', 'chief'],
        "note": "Executive role — broad access is normal. Escalate to HR for verification, do not auto-block."
    },
    {
        "condition": lambda row: row.get('days_inactive', 999) < 30 and row.get('action') == 'export_data',
        "note": "Recently active user performing export — could be legitimate business activity. Flag for manager review."
    },
    {
        "condition": lambda row: row.get('privilege_level') == 'service-account',
        "note": "Service account — automated process may explain unusual hours. Verify scheduled job exists."
    }
]

def apply_exceptions(row):
    notes = []
    for rule in EXCEPTION_RULES:
        try:
            if rule['condition'](row):
                notes.append(rule['note'])
        except:
            pass
    return notes if notes else ["No mitigating context found — treat alert as high priority."]

if __name__ == "__main__":
    with open('outputs/alerts.json') as f:
        alerts_data = json.load(f)

    for alert in alerts_data['alerts']:
        exceptions = apply_exceptions(alert)
        alert['exception_notes'] = exceptions

    with open('outputs/alerts.json', 'w') as f:
        json.dump(alerts_data, f, indent=2, default=str)

    print("Exception notes added to all alerts.")
    print("\nSample — first alert exception notes:")
    print(alerts_data['alerts'][0]['exception_notes'])