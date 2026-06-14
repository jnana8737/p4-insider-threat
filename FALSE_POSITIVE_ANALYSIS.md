\# False Positive Analysis



\## Edge Cases Handled



\### 1. Executive/Senior Admin Accounts

Risk: Admin accounts flagged for legitimate elevated access

Mitigation: Exception handler adds context note to escalate to HR rather than auto-block

Result: Reduces auto-block false positives for privileged users



\### 2. Service Accounts

Risk: Service accounts have no normal pattern and get flagged constantly

Mitigation: Exception handler flags service account exports for job scheduler verification

Result: Analysts check scheduled jobs before escalating



\### 3. Recently Active Users

Risk: Users active within 30 days flagged for exports that may be legitimate

Mitigation: Exception handler adds manager review note instead of immediate block

Result: Reduces false positives for normal business activity



\### 4. Night Access by On-Call Engineers

Risk: On-call engineers legitimately access systems at night

Mitigation: time\_risk is only 10% of the weighted score — single night access cannot alone reach CRITICAL

Result: Pattern of night access required to escalate



\### 5. New Hire Risk

Risk: New hires accessing sensitive data may be legitimate onboarding

Mitigation: New hire flag combined with sensitivity score, not standalone trigger

Result: New hire + high sensitivity + night access required for escalation



\### 6. Adjustable Threshold

Risk: Fixed threshold creates too many or too few alerts

Mitigation: Dashboard includes adjustable risk score threshold slider (0-100)

Recommended: 30 for comprehensive monitoring, 65 for high-priority-only view



\## Threshold Trade-offs

\- Threshold 30: Precision 73%, Recall 91% — catch almost everything, some false positives

\- Threshold 35: Precision 87%, Recall 69% — balanced for daily operations

\- Threshold 50+: Precision 90%+, Recall drops below 25% — only for critical-only view



\## Known Limitations

\- No HR termination data integration (would significantly reduce false positives)

\- No calendar/on-call schedule data (month-end Finance activity may be over-flagged)

\- Service account baselines not separately modeled from human accounts

