import streamlit as st
import pandas as pd
import json
import plotly.express as px
import os
import time
import streamlit.components.v1 as components

st.set_page_config(page_title="Insider Threat Detection", layout="wide")
st.title("🔴 Insider Threat Detection System")
st.caption("Société Générale Hackathon | P4 Data Access Audit")

SCORED_PATH = 'outputs/scored_events.csv'
ALERTS_PATH = 'outputs/alerts.json'
USER_RISK_PATH = 'outputs/user_risk.csv'

if not os.path.exists(SCORED_PATH) or not os.path.exists(ALERTS_PATH):
    st.warning("Run the ML pipeline first.")
    st.stop()

mod_time = time.ctime(os.path.getmtime(SCORED_PATH))
st.caption(f"Data last updated: {mod_time}")

df = pd.read_csv(SCORED_PATH)
with open(ALERTS_PATH) as f:
    alerts_data = json.load(f)

user_risk_exists = os.path.exists(USER_RISK_PATH)
if user_risk_exists:
    user_df = pd.read_csv(USER_RISK_PATH)

tab1, tab2, tab3 = st.tabs(["📊 Overview", "👤 User Profiles", "🗄️ Data Assets"])

with tab1:
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Events", alerts_data['metadata']['total_events'])
    col2.metric("Critical Alerts", alerts_data['metadata']['critical_count'])
    col3.metric("High Alerts", alerts_data['metadata']['high_count'])
    col4.metric("Users at Risk", alerts_data['metadata']['users_at_risk'])

    # Severity donut + timeline side by side
    c1, c2 = st.columns([1, 2])
    with c1:
        st.subheader("Severity Breakdown")
        sev = df['severity'].value_counts().reset_index()
        sev.columns = ['severity', 'count']
        fig_donut = px.pie(
            sev, names='severity', values='count', hole=0.5,
            color='severity',
            color_discrete_map={'CRITICAL':'red','HIGH':'orange','MEDIUM':'gold','LOW':'green'}
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with c2:
        st.subheader("Risk Score Timeline")
        fig = px.scatter(
            df, x='timestamp', y='risk_score', color='severity',
            hover_data=['user_id','action','resource'],
            color_discrete_map={'CRITICAL':'red','HIGH':'orange','MEDIUM':'gold','LOW':'green'}
        )
        st.plotly_chart(fig, use_container_width=True)

    # Privilege Graph
    st.subheader("🕸️ Privilege Access Graph (High/Critical Events Only)")
    graph_path = 'outputs/privilege_graph.html'
    if os.path.exists(graph_path):
        with open(graph_path, 'r', encoding='utf-8') as f:
            graph_html = f.read()
        components.html(graph_html, height=600, scrolling=True)
    else:
        st.info("Run python -m src.graph_viz to generate the graph")

    # Top Alerts Table with threshold slider
    st.subheader("🚨 Top Alerts")
    threshold = st.slider("Risk Score Threshold", min_value=0, max_value=100, value=30)
    top_alerts = df[df['risk_score'] > threshold].sort_values('risk_score', ascending=False).head(20)
    st.caption(f"Showing {len(top_alerts)} alerts above threshold {threshold}")
    display_cols = [c for c in ['user_id','action','resource','time_classification','risk_score','severity'] if c in df.columns]
    st.dataframe(top_alerts[display_cols], use_container_width=True)

    # Alert Deep Dive
    st.subheader("🔍 Alert Investigation")
    alert_options = {f"{a['user_id']} - {a['action']} ({a['risk_score']:.1f})": a for a in alerts_data['alerts']}
    selected_label = st.selectbox("Select Alert", list(alert_options.keys()))
    selected_alert = alert_options[selected_label]
    narrative = selected_alert['narrative']

    st.markdown(f"**Summary:** {narrative.get('summary','')}")
    st.markdown(f"**Recommendation:** `{narrative.get('recommendation','')}`")
    st.markdown(f"**Confidence:** {narrative.get('confidence','')}")

    st.markdown("**Anomalies detected:**")
    for a in narrative.get('anomalies', []):
        st.markdown(f"- {a}")

    st.markdown(f"**Business context:** {narrative.get('business_context','')}")

    st.markdown("**⚠️ Exception Notes:**")
    for note in selected_alert.get('exception_notes', []):
        st.info(note)

    # PDF Download
    report_path = 'outputs/incident_report.pdf'
    if os.path.exists(report_path):
        with open(report_path, 'rb') as f:
            st.download_button(
                label="📄 Download Incident Report (PDF)",
                data=f,
                file_name="insider_threat_report.pdf",
                mime="application/pdf"
            )

    if st.button("🔄 Refresh Data"):
        st.rerun()

with tab2:
    st.subheader("👤 User Risk Profiles")
    if not user_risk_exists:
        st.warning("Run python -m src.user_scorer first to generate user_risk.csv")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Users", len(user_df))
            st.metric("High/Critical Risk Users",
                int(user_df['user_severity'].isin(['HIGH','CRITICAL']).sum()))
        with col2:
            user_sev = user_df['user_severity'].value_counts().reset_index()
            user_sev.columns = ['severity','count']
            fig_u = px.pie(user_sev, names='severity', values='count', hole=0.5,
                color='severity',
                color_discrete_map={'CRITICAL':'red','HIGH':'orange','MEDIUM':'gold','LOW':'green'})
            st.plotly_chart(fig_u, use_container_width=True)

        st.subheader("Top Risky Users")
        show_cols = [c for c in ['user_id','user_risk_score','user_severity',
            'export_count','night_access_count','privilege_level',
            'department','job_title'] if c in user_df.columns]
        st.dataframe(
            user_df.sort_values('user_risk_score', ascending=False)[show_cols].head(20),
            use_container_width=True
        )

with tab3:
    st.subheader("🗄️ Data Assets at Risk")
    if 'resource' in df.columns:
        resource_risk = df.groupby('resource').agg(
            total_accesses=('action','count'),
            avg_risk=('risk_score','mean'),
            export_count=('action', lambda x: (x=='export_data').sum()),
            high_risk_count=('severity', lambda x: x.isin(['HIGH','CRITICAL']).sum())
        ).reset_index().sort_values('avg_risk', ascending=False)

        fig_res = px.bar(
            resource_risk.head(15), x='resource', y='avg_risk',
            color='avg_risk', color_continuous_scale='RdYlGn_r',
            title='Average Risk Score by Resource'
        )
        st.plotly_chart(fig_res, use_container_width=True)

        st.subheader("Resource Access Summary")
        st.dataframe(resource_risk, use_container_width=True)

        if 'resource_sensitivity' in df.columns:
            st.subheader("Sensitivity Breakdown")
            sens = df['resource_sensitivity'].value_counts().reset_index()
            sens.columns = ['sensitivity','count']
            fig_s = px.pie(sens, names='sensitivity', values='count', hole=0.4)
            st.plotly_chart(fig_s, use_container_width=True)