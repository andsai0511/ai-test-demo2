import os
from openai import OpenAI
from ai.ai_bot import AiBot

class ChatGPT(AiBot):

    def __init__(self, token, model):
        self.__chat_gpt_model = model
        self.__client = OpenAI(api_key = token)

    def ai_generate_test_coverage(self, code, unit_test, all_source_files, unit_test_file_path):
        stream = self.__client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": AiBot.build_test_generation_prompt(code=code, unit_test=unit_test, all_source_files=all_source_files, unit_test_file_path=unit_test_file_path),
                }
            ],
            model=self.__chat_gpt_model,
            stream=True,
        )
        content = []
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content.append(chunk.choices[0].delta.content)
        return "".join(content)
