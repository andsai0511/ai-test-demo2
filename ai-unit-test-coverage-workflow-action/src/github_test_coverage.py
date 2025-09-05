import os
from pathlib import Path
from env_vars import EnvVars
from git import Git
from log import Log

separator = "\n\n----------------------------------------------------------------------\n\n"
def get_unit_test_file_path(file_path: str, src_path: str, test_path: str) -> str:
    if not file_path.startswith(src_path):
        return ""

    test_path_base = test_path + file_path[len(src_path):]
    path = Path(test_path_base)
    file_name = path.stem
    extension = path.suffix

    test_file_name = ""
    if extension in ['.py', '.c', '.h']:
        test_file_name = f"test_{file_name}{extension}"
    elif extension in ['.java', '.kt']:
        test_file_name = f"{file_name}Test{extension}"
    elif extension == '.swift':
        test_file_name = f"{file_name}Tests{extension}"
    elif extension in ['.js', '.ts']:
        test_file_name = f"{file_name}.test{extension}"
    elif extension in ['.scala', '.groovy']:
        test_file_name = f"{file_name}Spec{extension}"
    else:
        return ""

    return str(path.parent / test_file_name)

def overwrite_unit_test_file(file_path: str, content: str):
    Log.print_green("Overwriting unit test file", file_path)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        f.write(content)

def get_build_and_test_command(build_tool: str) -> str:
    build_tool = build_tool.lower()
    if build_tool == 'mvn':
        return 'mvn clean verify'
    elif build_tool == 'gradle':
        return './gradlew clean test'
    elif build_tool == 'npm':
        return 'npm test -- --coverage'
    elif build_tool == 'pytest':
        return 'pytest --cov=src tests/'
    elif build_tool == 'swift':
        return 'swift test --enable-code-coverage'
    elif build_tool == 'sbt':
        return 'sbt clean coverage test'
    else:
        Log.print_yellow(f"Unknown build tool: {build_tool}. No build will be run.")
        return ""

def build_and_run_unit_tests_coverage():
    Log.print_green("Building and running unit tests coverage...")
    command = get_build_and_test_command(vars.build_tool)
    if not command:
        return

    report_file = "coverage_report.txt"
    full_command = f"{command} > {report_file} 2>&1"

    Log.print_green(f"Using build command: {full_command}")
    return_code = os.system(full_command)

    if os.path.exists(report_file):
        with open(report_file, 'r') as f:
            coverage_report = f.read()
        Log.print_green("--- Coverage Report ---")
        # We use print directly here to preserve formatting
        print(coverage_report)
        Log.print_green("-----------------------")
        os.remove(report_file)  # Clean up

    if return_code != 0:
        Log.print_red("Unit tests failed or coverage failed.")
    else:
        Log.print_green("Unit tests passed.")

def get_file_content(file)-> str:
    try:
        with open(file, 'r') as file_opened:
            file_content = file_opened.read()
            return file_content
    except FileNotFoundError:
        Log.print_yellow("File not found in the PR.", file)
        return ""

def main():
    global vars
    vars = EnvVars()
    vars.check_vars()

    # Select AI Bot based on the BOT environment variable (case-insensitive)
    bot_type = vars.bot.strip().lower()
    if bot_type == "gemini":
        from ai.gemini_bot import GeminiBot
        ai = GeminiBot(vars.llm_url, vars.llm_token, vars.llm_model)
    elif bot_type == "ollama":
        from ai.ollama_bot import OllamaBot
        ai = OllamaBot(vars.llm_url, vars.llm_model)
    elif bot_type == "chatgpt":
        from ai.chat_gpt import ChatGPT
        ai = ChatGPT(vars.llm_token, vars.llm_model)
    else:
        raise ValueError(f"Unsupported BOT type: {vars.bot}")

    remote_name = Git.get_remote_name()

    all_source_files_content = []
    for file in Git.get_all_files():
        if file.startswith(vars.src_path):
            all_source_files_content.append(f'File: {file}{separator}{get_file_content(file)}')
    all_source_files_content = separator.join(all_source_files_content)

    Log.print_green("Remote is", remote_name)
    changed_files = []
    if vars.generate_mode.lower() == "full":
        changed_files = Git.get_all_files()
    else :
        changed_files = Git.get_diff_files(remote_name=remote_name, head_ref=vars.branch_name, base_ref=vars.base_ref)

    Log.print_green("Found changes in files", changed_files)
    if len(changed_files) == 0: 
        Log.print_red("No changes between branch")

    for file in changed_files:
        Log.print_green("Checking file", file)

        _, file_extension = os.path.splitext(file)
        file_extension = file_extension.lstrip('.')
        if file_extension not in vars.target_extensions:
            Log.print_yellow(f"Skipping, unsupported extension {file_extension} file {file}")
            continue

        file_content = get_file_content(file)
        if not file_content:
            continue

        unit_test_file_content=""
        unit_test_file = get_unit_test_file_path(file_path=file, src_path=vars.src_path, test_path=vars.test_path)
        if not unit_test_file:
            Log.print_yellow("Could not determine test file path for", file)
            continue
        else:
            unit_test_file_content = get_file_content(unit_test_file)

        if not unit_test_file_content:
            Log.print_yellow("Unit test file does not exist or is empty", unit_test_file)
            unit_test_file_content = "" # Start with an empty string if no test file
        
        Log.print_green(f"Asking AI for test coverage for {file}")
        new_unit_test_file_content = ai.ai_generate_test_coverage(code=file_content, unit_test=unit_test_file_content, all_source_files=all_source_files_content, unit_test_file_path=unit_test_file)

        if new_unit_test_file_content:
            overwrite_unit_test_file(unit_test_file, new_unit_test_file_content)
        else:
            Log.print_yellow("AI did not return unit test content for", file)

    build_and_run_unit_tests_coverage()
    commit_message = f'feat: Add AI-generated unit test coverage for branch #{vars.branch_name}'
    Git.push_changes_to_github(vars.branch_name, commit_message, vars.owner, vars.repo, vars.token,
                               vars.test_path+"/*")

if __name__ == "__main__":
    main()
