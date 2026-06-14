from fpdf import FPDF
import json
from datetime import datetime

def clean(text):
    if not text:
        return ''
    return str(text).replace('\u2014', '-').replace('\u2013', '-').replace('\u2018', "'").replace('\u2019', "'").replace('\u201c', '"').replace('\u201d', '"')

def generate_report():
    with open('outputs/alerts.json') as f:
        alerts_data = json.load(f)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 16)
    pdf.cell(0, 10, 'Insider Threat Detection Report', align='C')
    pdf.ln(10)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 8, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", align='C')
    pdf.ln(8)
    pdf.cell(0, 8, 'Societe Generale Hackathon | P4 Data Access Audit', align='C')
    pdf.ln(12)

    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, 'Executive Summary')
    pdf.ln(8)
    pdf.set_font('Helvetica', '', 10)
    m = alerts_data['metadata']
    pdf.cell(0, 6, f"Total Events Analyzed: {m['total_events']}")
    pdf.ln(6)
    pdf.cell(0, 6, f"Critical Alerts: {m['critical_count']}")
    pdf.ln(6)
    pdf.cell(0, 6, f"High Alerts: {m['high_count']}")
    pdf.ln(6)
    pdf.cell(0, 6, f"Users at Risk: {m['users_at_risk']}")
    pdf.ln(10)

    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, 'Top Alert Investigations')
    pdf.ln(8)

    for i, alert in enumerate(alerts_data['alerts'][:10]):
        pdf.set_font('Helvetica', 'B', 10)
        title = clean(f"Alert {i+1}: {alert.get('user_id')} - {alert.get('action')} on {alert.get('resource')}")
        pdf.cell(0, 7, title)
        pdf.ln(7)

        pdf.set_font('Helvetica', '', 9)
        score = alert.get('risk_score', 0)
        severity = clean(alert.get('severity', ''))
        time_class = clean(alert.get('time_classification', ''))
        pdf.cell(0, 6, f"Risk Score: {score:.1f}/100 | Severity: {severity} | Time: {time_class}")
        pdf.ln(6)

        narrative = alert.get('narrative', {})
        summary = clean(narrative.get('summary', ''))
        if summary:
            pdf.multi_cell(0, 6, f"Summary: {summary}")

        rec = clean(narrative.get('recommendation', ''))
        conf = clean(str(narrative.get('confidence', '')))
        pdf.cell(0, 6, f"Recommendation: {rec} | Confidence: {conf}")
        pdf.ln(6)

        exception_notes = alert.get('exception_notes', [])
        if exception_notes:
            pdf.set_font('Helvetica', 'I', 9)
            pdf.multi_cell(0, 6, clean(f"Context: {exception_notes[0]}"))

        pdf.ln(4)

    pdf.output('outputs/incident_report.pdf')
    print("Saved outputs/incident_report.pdf")

if __name__ == "__main__":
    generate_report()