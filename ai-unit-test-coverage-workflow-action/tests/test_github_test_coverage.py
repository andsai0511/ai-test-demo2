import os
import sys
from unittest.mock import patch, MagicMock

SRC_CODE = """
def add(x, y):
    return x + y

def subtract(x, y):
    return x - y

def multiply(x, y):
    return x * y

def divide(x, y):
    if y == 0:
        raise ValueError("Cannot divide by zero!")
    return x / y
"""

UNIT_TEST_CODE = """import unittest
from src.calc import add, subtract, multiply, divide

class TestCalculator(unittest.TestCase):

    def test_add_positive_numbers(self):
        self.assertEqual(add(5, 3), 8)
        self.assertEqual(add(100, 200), 300)

    def test_add_negative_numbers(self):
        self.assertEqual(add(-5, -3), -8)
        self.assertEqual(add(-10, -20), -30)

    def test_add_mixed_numbers(self):
        self.assertEqual(add(5, -3), 2)
        self.assertEqual(add(-5, 3), -2)
        self.assertEqual(add(10, -15), -5)

    def test_add_with_zero(self):
        self.assertEqual(add(0, 7), 7)
        self.assertEqual(add(7, 0), 7)
        self.assertEqual(add(0, 0), 0)
        self.assertEqual(add(-10, 0), -10)

    def test_add_floating_point_numbers(self):
        self.assertAlmostEqual(add(0.1, 0.2), 0.3)
        self.assertAlmostEqual(add(1.5, 2.5), 4.0)
        self.assertAlmostEqual(add(-0.5, 0.7), 0.2)

    def test_subtract_positive_numbers(self):
        self.assertEqual(subtract(5, 3), 2)
        self.assertEqual(subtract(10, 20), -10)

    def test_subtract_negative_numbers(self):
        self.assertEqual(subtract(-5, -3), -2)
        self.assertEqual(subtract(-3, -5), 2)
        self.assertEqual(subtract(-10, -20), 10)

    def test_subtract_mixed_numbers(self):
        self.assertEqual(subtract(5, -3), 8)
        self.assertEqual(subtract(-5, 3), -8)
        self.assertEqual(subtract(10, -15), 25)

    def test_subtract_with_zero(self):
        self.assertEqual(subtract(7, 0), 7)
        self.assertEqual(subtract(0, 7), -7)
        self.assertEqual(subtract(0, 0), 0)
        self.assertEqual(subtract(-10, 0), -10)

    def test_subtract_floating_point_numbers(self):
        self.assertAlmostEqual(subtract(0.3, 0.1), 0.2)
        self.assertAlmostEqual(subtract(2.5, 1.5), 1.0)
        self.assertAlmostEqual(subtract(0.7, -0.5), 1.2)

    def test_multiply_positive_numbers(self):
        self.assertEqual(multiply(5, 3), 15)
        self.assertEqual(multiply(10, 20), 200)

    def test_multiply_negative_numbers(self):
        self.assertEqual(multiply(-5, -3), 15)
        self.assertEqual(multiply(-10, -2), 20)

    def test_multiply_mixed_numbers(self):
        self.assertEqual(multiply(5, -3), -15)
        self.assertEqual(multiply(-5, 3), -15)
        self.assertEqual(multiply(10, -1), -10)

    def test_multiply_by_zero(self):
        self.assertEqual(multiply(7, 0), 0)
        self.assertEqual(multiply(0, 7), 0)
        self.assertEqual(multiply(0, 0), 0)
        self.assertEqual(multiply(-10, 0), 0)

    def test_multiply_by_one(self):
        self.assertEqual(multiply(7, 1), 7)
        self.assertEqual(multiply(1, 7), 7)
        self.assertEqual(multiply(-10, 1), -10)

    def test_multiply_floating_point_numbers(self):
        self.assertAlmostEqual(multiply(2.5, 2.0), 5.0)
        self.assertAlmostEqual(multiply(0.5, 0.5), 0.25)
        self.assertAlmostEqual(multiply(-1.5, 2.0), -3.0)

    def test_divide_positive_numbers(self):
        self.assertEqual(divide(6, 3), 2.0)
        self.assertEqual(divide(10, 2), 5.0)

    def test_divide_negative_numbers(self):
        self.assertEqual(divide(-6, -3), 2.0)
        self.assertEqual(divide(-10, -2), 5.0)

    def test_divide_mixed_numbers(self):
        self.assertEqual(divide(6, -3), -2.0)
        self.assertEqual(divide(-6, 3), -2.0)
        self.assertEqual(divide(10, -5), -2.0)

    def test_divide_by_one(self):
        self.assertEqual(divide(7, 1), 7.0)
        self.assertEqual(divide(-10, 1), -10.0)

    def test_divide_zero_by_non_zero(self):
        self.assertEqual(divide(0, 5), 0.0)
        self.assertEqual(divide(0, -5), 0.0)

    def test_divide_floating_point_numbers(self):
        self.assertAlmostEqual(divide(5.0, 2.0), 2.5)
        self.assertAlmostEqual(divide(1.0, 3.0), 1/3)
        self.assertAlmostEqual(divide(-10.0, 4.0), -2.5)

    def test_divide_by_zero(self):
        with self.assertRaises(ValueError) as cm:
            divide(10, 0)
        self.assertEqual(str(cm.exception), "Cannot divide by zero!")

        with self.assertRaises(ValueError) as cm:
            divide(-5, 0)
        self.assertEqual(str(cm.exception), "Cannot divide by zero!")

        with self.assertRaises(ValueError) as cm:
            divide(0, 0) # Even 0/0 should raise error according to function doc
        self.assertEqual(str(cm.exception), "Cannot divide by zero!")

if __name__ == '__main__':
    unittest.main()"""

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Helper for dummy subprocess result
def dummy_subprocess_run(*args, **kwargs):
    class DummyResult:
        def __init__(self):
            self.returncode = 0
            self.stdout = 'src/calc.py\n'
            self.stderr = ''
    return DummyResult()

REQUIRED_ENV = {
    'BOT': 'gemini',
    'LLM_URL': 'http://dummy-url',
    'LLM_MODEL': 'dummy-model',
    'LLM_KEY': 'dummy-key',
    'REPO_OWNER': 'dummy-owner',
    'REPO_NAME': 'dummy-repo',
    'PULL_NUMBER': '1',
    'GITHUB_TOKEN': 'dummy-token',
    'GITHUB_HEAD_REF': 'main',
    'GITHUB_BASE_REF': 'main',
    'TARGET_EXTENSIONS': 'py',
    'BUILD_TOOL': 'pytest',
    'GENERATE_MODE': 'FULL',
    'SRC_PATH': 'src',
    'TEST_PATH': 'tests'
}

def set_required_env(monkeypatch, overrides=None):
    env = REQUIRED_ENV.copy()
    if overrides:
        env.update(overrides)
    for k, v in env.items():
        monkeypatch.setenv(k, v)


def mock_get_file_content_side_effect(file_path):
    if file_path == 'src/calc.py':
        return SRC_CODE
    return ''

def mock_overwrite_unit_test_file(file_path: str, content: str):
    return

@patch('src.github_test_coverage.get_file_content', side_effect=mock_get_file_content_side_effect)
@patch('src.github_test_coverage.overwrite_unit_test_file', side_effect=mock_overwrite_unit_test_file)
@patch('ai.gemini_bot.GeminiBot.ai_generate_test_coverage', return_value=UNIT_TEST_CODE)
def test_bot_selection_gemini(mock_ai_generate, mock_get_file_content, mock_overwrite_unit_test_file, monkeypatch):
    set_required_env(monkeypatch, {'BOT': 'gemini'})
    with patch('github_test_coverage.Git') as MockGit, \
            patch('git.Git.get_diff_files', return_value=['src/calc.py']), \
            patch('git.Git.get_remote_name', return_value='origin'), \
            patch('subprocess.run', side_effect=dummy_subprocess_run):
        import src.github_test_coverage
        src.github_test_coverage.main()
        mock_ai_generate.assert_called()
# Patch imports for the test context
