import streamlit as st
from smolagent import SmolAgent

# TEMPORALMENTE así para confirmar que el problema es `st.secrets`
api_key = "sk-tu-clave-copiada-directamente"
st.write("Usando clave directamente:", api_key)  # Solo debug

agent = SmolAgent(api_key=api_key)

st.title("Mi Agente Inteligente 🤖")
user_input = st.text_input("Decile algo:")

if user_input:
    response = agent.run(user_input)
    st.write("Respuesta del agente:", response)
