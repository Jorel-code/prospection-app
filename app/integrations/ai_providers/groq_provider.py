from groq import Groq
import os
from app.interfaces.ai_provider_interface import IAIMessageGenerator
from app.integrations.ai_providers.dto import GeneratedMessage

class GroqProvider(IAIMessageGenerator):
    def __init__(self):
        self.client = Groq(api_key=os.environ["GROQ_API_KEY"])

    def generate(self, system_prompt, user_prompt, channel) -> GeneratedMessage:
        response = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        return GeneratedMessage(
            content=response.choices[0].message.content,
            provider_used="groq",
            channel=channel
        )