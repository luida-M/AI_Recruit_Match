import streamlit as st
from smolagent import SmolAgent

def agent_demo():
    # Obtener clave secreta
    api_key = st.secrets["API_KEY"]

    # Inicializar agente
    agent = SmolAgent(api_key=api_key)

    # UI
    st.title("Mi Agente Inteligente 🤖")
    user_input = st.text_input("Decile algo:")

    if user_input:
        response = agent.run(user_input)
        st.write("Respuesta del agente:", response)

# Llamás a la función
agent_demo()
