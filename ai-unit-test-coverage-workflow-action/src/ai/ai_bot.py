from abc import ABC, abstractmethod

class AiBot(ABC):

    __test_generation_prompt = """
You are an expert software engineer specializing in testing.
Your task is to generate a comprehensive unit test suite for the given code.
If an existing unit test file is provided, you should add or improve the tests in it.
If no unit test file is provided, you should create a new one from scratch.

- Analyze the provided code to understand its functionality, inputs, and outputs.
- Create test cases that cover all execution paths, including edge cases and error conditions.
- Ensure the generated tests are well-structured, readable, and follow best practices for the language.
- Only return the complete code for the unit test file. Do not include any explanations, introductory text, or markdown formatting.

Relevant Source Files:
{all_source_files}

Unit Test File Path (use this to generate the correct package name):
{unit_test_file_path}

Existing Unit Test File (if any):
{unit_test}

Source Code:
{code}
"""

    @abstractmethod
    def ai_generate_test_coverage(self, code, unit_test, all_source_files, unit_test_file_path) -> str:
        pass

    @staticmethod
    def build_test_generation_prompt(code, unit_test, all_source_files, unit_test_file_path) -> str:
        return AiBot.__test_generation_prompt.format(
            unit_test=unit_test,
            code=code,
            all_source_files=all_source_files,
            unit_test_file_path=unit_test_file_path
        )
