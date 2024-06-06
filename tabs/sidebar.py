import streamlit as st

def sidebar():
    st.image("https://mediafiles.urlaubsguru.de/wp-content/uploads/2023/06/Logo_UG_mit-claim.png")
    st.title("SEO Tool")
    st.markdown("<p>Welcome to the Urlaubsguru SEO-Tool.</p>", unsafe_allow_html=True)
    st.markdown("<h3>Currently features the following features:</h3>", unsafe_allow_html=True)
    st.markdown("<ul><li>Performance Change Visualization for given URLs</li></ul>", unsafe_allow_html=True)
    st.divider()
    st.markdown("<h4>Domain Settings</h4><p>Please select the desired Urlaubsguru Domain for your Analysis.</p>", unsafe_allow_html=True)
    domain_wanted = st.selectbox("Domain", ["Germany", "Austria", "Switzerland", "Netherlands", "Spain"])
    st.divider()

    st.markdown("<h3>Contact</h3><p>If you have any questions, requests or comments, please contact the Inbound Marketing Team:</p><ul><li><a href='https://teams.microsoft.com/l/channel/19%3a72197b1f3177425aba225726ec4f2f5f%40thread.skype/Inbound%2520Automation?groupId=1da7e5cc-703e-4d39-8dac-4b5a723173a4&tenantId=5f4d3a64-cc9f-49a2-be2d-41ac01dba2dd'>Inbound Marketing Automation Teams Channel</a></li><li><a href='mailto:paul.herzog@urlaubsguru.de'>E-Mail</a></li>", unsafe_allow_html=True)
    st.divider()

    return domain_wanted