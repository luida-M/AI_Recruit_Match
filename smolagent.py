#smolagent.py
import openai

class SmolAgent:
    def __init__(self, api_key):
        openai.api_key = api_key

    def run(self, prompt):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # o el modelo que tengas habilitado
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response['choices'][0]['message']['content']
