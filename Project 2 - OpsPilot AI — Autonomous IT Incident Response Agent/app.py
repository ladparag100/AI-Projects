import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

st.set_page_config(page_title='OpsPilot AI', page_icon='🛡️', layout='wide')
st.title('OpsPilot AI — Autonomous IT Incident Response Agent')
st.write('Simulated incident dashboard with AI triage suggestions. Connect to your monitoring and automation systems in a real deployment.')

# Sample incidents (in-memory). In real use, these would come from monitoring APIs.
sample_incidents = [
    {'id': 'INC-001', 'time': '2026-05-07 09:12:00', 'severity': 'high', 'summary': 'Database connectivity errors', 'details': 'Connection timeouts to primary DB.'},
    {'id': 'INC-002', 'time': '2026-05-07 10:05:00', 'severity': 'medium', 'summary': 'High CPU on web-01', 'details': 'CPU > 90% for 10min.'},
    {'id': 'INC-003', 'time': '2026-05-07 11:22:00', 'severity': 'low', 'summary': 'Disk nearly full on backup', 'details': 'Disk usage 85%.'}
]

st.subheader('Active Incidents')
for inc in sample_incidents:
    with st.expander(f"{inc['id']} — {inc['summary']} ({inc['severity']})"):
        st.write(f"**Time:** {inc['time']}")
        st.write(f"**Details:** {inc['details']}")
        st.write('---')
        # Simple triage suggestions
        if inc['severity'] == 'high':
            st.warning('Suggested actions: 1) Failover DB; 2) Restart DB service; 3) Open SEV ticket')
            if st.button(f"Run remediation for {inc['id']}"):
                st.success('Simulated remediation executed: Restart DB service (dry-run)')
        elif inc['severity'] == 'medium':
            st.info('Suggested actions: 1) Scale web service; 2) Investigate recent deploys')
        else:
            st.write('Suggested actions: Monitor and schedule maintenance')

st.divider()

st.subheader('AI Triage (Example)')
user_question = st.text_area('Ask OpsPilot about an incident (example: "What should I do for INC-001?")')
if st.button('Get Triage Suggestion') and user_question.strip():
    # This is a placeholder: in a real app we'd call an LLM with context
    st.write('**AI Suggestion:**')
    st.write('Investigate DB connectivity: check network connectivity, failover status, and recent configuration changes. Consider failing over to replica if primary unresponsive.')

st.markdown('\n---\n**Note:** This is a demo app. Integrate with your monitoring/automation systems for production use.')
