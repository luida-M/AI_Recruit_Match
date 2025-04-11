import streamlit as st
import openai

class SmolAgent:
    def __init__(self, api_key):
        openai.api_key = api_key

    def run(self, prompt):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response['choices'][0]['message']['content']

def agent_demo():
    api_key = st.secrets["API_KEY"]
    st.write("API key cargada:", api_key)  # DEBUG
    agent = SmolAgent(api_key=api_key)

    st.title("Mi Agente Inteligente 🤖")
    user_input = st.text_input("Decile algo:")

    if user_input:
        response = agent.run(user_input)
        st.write("Respuesta del agente:", response)

agent_demo()
