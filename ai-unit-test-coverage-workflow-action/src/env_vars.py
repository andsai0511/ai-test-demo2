import os
from log import Log

class EnvVars:
    def __init__(self):

        self.bot = os.getenv('BOT', 'gemini')
        self.owner = os.getenv('REPO_OWNER')
        self.repo = os.getenv('REPO_NAME')
        self.token = os.getenv('GITHUB_TOKEN')
        self.branch_name = os.getenv('BRANCH_NAME')
        self.base_ref = os.getenv('MASTER_BRANCH_NAME')

        self.llm_token = os.getenv('LLM_KEY')
        self.llm_url = os.getenv('LLM_URL')
        self.llm_model = os.getenv('LLM_MODEL')

        self.target_extensions = os.getenv('TARGET_EXTENSIONS', 'kt,java,py,js,swift,c,h')
        self.target_extensions = [lang.strip() for lang in self.target_extensions.split(",")]
        self.build_tool = os.getenv('BUILD_TOOL')
        self.generate_mode = os.getenv('GENERATE_MODE')
        self.src_path = os.getenv('SRC_PATH')
        self.test_path = os.getenv('TEST_PATH')

        if len(self.target_extensions) == 0:
            raise ValueError(f"Please specify TARGET_EXTENSIONS. Coma separated, could be, like: kt,java,py,js,swift,c,h. Only these files will be reviewed")

        self.env_vars = {
            "owner" : self.owner,
            "repo" : self.repo,
            "token" : self.token,
            "base_ref" : self.base_ref,
            "branch_name" : self.branch_name,
            "llm_url": self.llm_url,
            "llm_model" : self.llm_model,
            "build_tool" : self.build_tool,
            "generate_mode" : self.generate_mode,
            "src_path" : self.src_path,
            "test_path" : self.test_path
        }

    def check_vars(self):
        missing_vars = [var for var, value in self.env_vars.items() if not value]
        if missing_vars:
            missing_vars_str = ", ".join(missing_vars)
            raise ValueError(f"The following environment variables are missing or empty: {missing_vars_str}")
        else:
            Log.print_green("All required environment variables are set.")