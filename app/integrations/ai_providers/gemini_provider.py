import google.generativeai as genai
import os
from app.interfaces.ai_provider_interface import IAIMessageGenerator
from app.integrations.ai_providers.dto import GeneratedMessage

class GeminiProvider(IAIMessageGenerator):
    def __init__(self):
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        self.model = genai.GenerativeModel("gemini-3.6-flash")

    def generate(self, system_prompt, user_prompt, channel) -> GeneratedMessage:
        prompt_complet = f"{system_prompt}\n\n{user_prompt}"
        response = self.model.generate_content(prompt_complet)
        return GeneratedMessage(content=response.text, provider_used="gemini", channel=channel)