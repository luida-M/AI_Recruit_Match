import streamlit as st
from smolagent import SmolAgent

# TEMPORALMENTE así para confirmar que el problema es `st.secrets`
api_key = "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"
st.write("Usando clave directamente:", api_key)  # Solo debug

agent = SmolAgent(api_key=api_key)

st.title("Mi Agente Inteligente 🤖")
user_input = st.text_input("Decile algo:")

if user_input:
    response = agent.run(user_input)
    st.write("Respuesta del agente:", response)
