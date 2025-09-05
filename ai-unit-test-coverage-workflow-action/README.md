# AI Generate Unit Test Coverage GitHub Action

This project provides a custom GitHub Action that uses AI bots (Gemini, Ollama, or others) to generate unit test 
coverage for pull requests and pushes the unit test coverage to GitHub.

## Features
- Automated Unit Test Coverage Generation
- Supports multiple LLM backends (Gemini, Ollama, etc.)
- Configurable via Action inputs

## Bot Selection

The action supports multiple AI bots. Choose which AI model to use by setting the `BOT` environment variable (case-insensitive) to one of the following:

- `gemini`   — Uses GeminiBot
- `ollama`   — Uses OllamaBot
- `chatgpt`  — Uses ChatGPT

Example (in your workflow YAML):

```yaml
      - name: AI Unit Test Generator
        uses: ./
        with:
          BOT: "gemini"
          ...
```

If an unsupported bot name is provided, the action will fail with an error.

## Usage
Add the following to your workflow YAML (e.g., `.github/workflows/ai-generate-unit-test-coverage-workflow-action.yml`):

```yaml
name: Generate Unit Test Coverage using Gemini API
on: workflow_dispatch
jobs:
  ai_review:
    runs-on: self-hosted
    steps:
      - uses: actions/checkout@v4
      - name: AI Unit Test Generator
        uses: ./  # or specify your repo, e.g. your-org/ai-unit-test-coverage-workflow-action@v1
        with:
          LLM_URL: ${{ secrets.LLM_URL }}
          LLM_KEY: ${{ secrets.LLM_KEY }}
          LLM_MODEL: "your-model"
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          REPO_OWNER: ${{ github.repository_owner }}
          REPO_NAME: ${{ github.event.repository.name }}
          BRANCH_NAME: ${{ github.ref }}
          MASTER_BRANCH_NAME: "ref/heads/master"
          TARGET_EXTENSIONS: ".py"
          BOT: "gemini"
          BUILD_TOOL: "mvn"
          GENERATE_MODE: "FULL"
          SRC_PATH: "src/main/java"
          TEST_PATH: "src/test/java"
```

## Inputs
| Name                   | Description                                   | Required |
|------------------------|-----------------------------------------------|----------|
| `LLM_URL`              | URL for the LLM (Ollama, Gemini, etc.)        | Yes      |
| `LLM_KEY`              | Token for the LLM (if required)               | No       |
| `LLM_MODEL`            | Model name for the LLM                        | Yes      |
| `GITHUB_TOKEN`         | GitHub Token for API access                   | Yes      |
| `REPO_OWNER`           | Repository owner                              | Yes      |
| `REPO_NAME`            | Repository name                               | Yes      |
| `BRANCH_NAME`          | branch name                                   | Yes      |
| `MASTER_BRANCH_NAME`   | base branch name                              | Yes      |
| `TARGET_EXTENSIONS`    | Target file extensions to review (e.g., .py)  | Yes      |
| `BOT`                  | AI bot to use (`gemini`, `ollama`, `chatgpt`) | Yes      |
| `BUILD_TOOL`           | mvn, gradle                                   | Yes      |
| `GENERATE_MODE`        | FULL, PR                                      | Yes      |
| `SRC_PATH`             | src, src/main/java                            | Yes      |
| `TEST_PATH`            | tests, src/test/java                          | Yes      |

## Recent Changes
- **Bot selection is now case-insensitive** via the `BOT` input/environment variable.
- **ChatGPT support is enabled** (ensure `openai` is in `requirements.txt`).
- **All environment variable names** in `action.yml` and workflow YAML use uppercase (e.g., `LLM_URL`, `BOT`, etc.).
- **New input:** `TARGET_EXTENSIONS` allows you to specify which file types to review (e.g., `.py`, `.js`).
- **Flexible configuration**: All main parameters are now configurable via workflow YAML or repository/organization secrets and variables.

## Development

- Python dependencies are listed in `requirements.txt` (`requests`, `openai`, `ollama`).
- Main entry point: `src/github_test_coverage.py` (now selects the bot based on the `BOT` variable).
- Custom action defined in `action.yml`.
- Example bots implemented: `GeminiBot`, `OllamaBot`, `ChatGPT` (see `src/ai/`).

## Local Build

- Clone the repository: `git clone https://github.com/narmada-rajendran/ai-unit-test-coverage-workflow-action.git`
- Create a virtual environment: `python3 -m venv venv`
- Activate the virtual environment: `source venv/bin/activate`
- Install dependencies: `pip3 install -r requirements.txt`
- Create a `.env` file (optional):
- Set Environment Variables in .env file (`GITHUB_TOKEN`, `BRANCH_NAME`, `MASTER_BRANCH_NAME, `LLM_KEY`, `LLM_MODEL`, 
  `LLM_URL`, `REPO_OWNER`, `REPO_NAME`, `TARGET_EXTENSIONS`, `BOT`, `BUILD_TOOL`, `GENERATE_MODE`, 
  `SRC_PATH`, `TEST_PATH`):
- Run the action: `python3 src/github_test_coverage.py`

## Testing
- Install pytest: `python3 -m pip install pytest`
- Run Unit tests: `PYTHONPATH=. pytest tests/test_github_test_coverage.py`

## Git Tag
- git tag -a -m "Description of this release" v1
- git push --follow-tags
