import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from app import run_app

st.set_page_config(page_title="Chat to MySQL", page_icon=':speech_balloon:')
st.title(body="Chat to MySQL")

with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

authenticator.login()

if st.session_state["authentication_status"]:
    with st.sidebar:
        st.image("../FRRcirculo.png", width=75)
        st.write(f'Welcome *{st.session_state["name"]}*')
        authenticator.logout()

    # Application
    run_app()

elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')
