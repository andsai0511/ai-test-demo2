import requests
from ai.ai_bot import AiBot
import json

class OllamaBot(AiBot):
    def __init__(self, base_url, model):
        self.base_url = base_url.rstrip('/')
        self.model = model

    def ai_generate_test_coverage(self, code, unit_test, all_source_files, unit_test_file_path):
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "you are a code testing expert"
                },
                {
                    "role": "user",
                    "content": AiBot.build_test_generation_prompt(code=code, unit_test=unit_test, all_source_files=all_source_files, unit_test_file_path=unit_test_file_path),
                }
            ],
            "stream": False
        }
        response = requests.post(url, json=payload, stream=False)
        response.raise_for_status()
        content = []
        for line in response.iter_lines():
            if line:
                json_object = json.loads(line.decode('utf-8'))
                content.append(json_object["message"]["content"])
        return "".join(content)
