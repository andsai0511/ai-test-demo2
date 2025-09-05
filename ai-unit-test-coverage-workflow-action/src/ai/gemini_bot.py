import os
import requests
from ai.ai_bot import AiBot

class GeminiBot(AiBot):
    def __init__(self, url, api_key, model="gemini-pro"):
        self.url = url
        self.api_key = api_key
        self.model = model
        self.base_url = f"{self.url}/{self.model}:generateContent"
        self.headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key
        }

    def ai_generate_test_coverage(self, code, unit_test, all_source_files, unit_test_file_path):
        prompt = AiBot.build_test_generation_prompt(code=code, unit_test=unit_test, all_source_files=all_source_files, unit_test_file_path=unit_test_file_path)
        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": prompt}]}
            ]
        }
        response = requests.post(self.base_url, headers=self.headers, json=payload)
        response.raise_for_status()
        data = response.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            return "[Gemini API: No valid response]"
