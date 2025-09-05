import subprocess
from typing import List
from log import Log

class Git:

    @staticmethod
    def __run_subprocess(options):
        Log.print_green(options)
        try:
            result = subprocess.run(options, capture_output=True, check=True, text=True)
            if result.returncode == 0:
                return result.stdout
            else:
                Log.print_red(options)
                raise Exception(f"Error running {options}: {result.returncode}: {result.stderr}: {result.stdout}")
        except subprocess.CalledProcessError as e:
            Log.print_red(options, e.returncode, e.output)
            raise Exception(f"Error running {options}: {e.returncode}: {e.output}: {e.stderr}: {e.stdout}")

    @staticmethod
    def get_remote_name() -> str:
        command = ["git", "remote", "-v"]
        result = Git.__run_subprocess(command)
        lines = result.strip().splitlines()
        return lines[0].split()[0]

    @staticmethod
    def get_last_commit_sha(file) -> str:
        command = ["git", "log", "-1", "--format=\"%H\"", "--", file]
        result = Git.__run_subprocess(command)
        lines = result.strip().splitlines()
        return lines[0].split()[0].replace('"', "")
        
    @staticmethod
    def get_diff_files(remote_name, head_ref, base_ref) -> List[str]:
        command = ["git", "diff", "--name-only", f"{remote_name}/{base_ref}", f"{remote_name}/{head_ref}"]
        result = Git.__run_subprocess(command)
        return result.strip().splitlines()
        
    @staticmethod
    def get_all_files() -> List[str]:
        """
        Lists all files in the git repository.
        The arguments are kept for compatibility with the call site, but are not used.
        """
        command = ["git", "ls-files"]
        result = Git.__run_subprocess(command)
        return result.strip().splitlines()

    @staticmethod
    def get_diff_in_file(remote_name, head_ref, base_ref, file_path) -> str:
        command = ["git", "diff", f"{remote_name}/{base_ref}", f"{remote_name}/{head_ref}", "--", file_path]
        return Git.__run_subprocess(command)

    @staticmethod
    def push_changes_to_github(branch_name: str, commit_message: str, owner: str, repo: str, token: str, files_to_add: str = 'tests/*'):
        Log.print_green("Pushing changes to GitHub...")
        Git.__run_subprocess(["git", "config", "--global", "user.email",
                              "ai-unit-test-coverage-generator@cvshealth.com"])
        Git.__run_subprocess(["git", "config", "--global", "user.name",
                              "ai-unit-test-coverage-generator"])
        Git.__run_subprocess(["git", "add", files_to_add])
        Git.__run_subprocess(["git", "commit", "-m", commit_message])
        remote_url = f"https://{owner}:{token}@github.com/{owner}/{repo}.git"
        Git.__run_subprocess(["git", "push", "--set-upstream", remote_url,
                              branch_name+":"+branch_name+"-unit-test-coverage"])
