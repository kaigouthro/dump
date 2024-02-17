import os
import subprocess
import importlib
import subprocess
import sys

def install_module(module_name):
    try:
        importlib.import_module(module_name)
        print(f"{module_name} is already installed.")
    except ImportError:
        print(f"{module_name} is not installed. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])
            print(f"{module_name} has been successfully installed.")
        except Exception as e:
            print(f"Error: Failed to install {module_name}. {str(e)}")

install_module("gitpython")

def set_git_executable(path_to_git):
    os.environ["GIT_PYTHON_REFRESH"] = "quiet"
    os.environ["GIT_PYTHON_GIT_EXECUTABLE"] = path_to_git

def get_git_exec_path():
    try:
        subprocess.run(["apk", "add", "git", "-y"], stderr=subprocess.PIPE)
        output = subprocess.check_output(["git", "--exec-path"], stderr=subprocess.PIPE)
        return output.decode().strip()
    except Exception as e:
        print(f"Error: Failed to retrieve git executable path. {str(e)}")
        return None

# Example usage
if git_exec_path := get_git_exec_path():
    set_git_executable( git_exec_path )


# Verify that the git executable has been set correctly
try:
    output = subprocess.check_output(["git", "--version"])
    git_version = output.decode().strip()
    print(f"Successfully set git executable. Git version: {git_version}")
except Exception as e:
    print(f"Error: Failed to set git executable. {str(e)}")


from git.repo import Repo



class FileGitCodeTool:
    description = "Handle file operations, Git functionalities, and code execution."
    public_description = "Read and write Python, Markdown, and Text files, handle Git operations, and execute code."

    def read_file(self, file_path):
        if not os.path.exists(file_path):
            return f"Error: File '{file_path}' does not exist."
        with open(file_path, 'r') as file:
            return file.read()

    def write_file(self, file_path, content):
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        return f"Successfully wrote content to file '{file_path}'."

    def clone_repo(self, repo_url, dir_path):
        try:
            Repo.clone_from(repo_url, dir_path)
            return f"Successfully cloned repository from '{repo_url}' to '{dir_path}'."
        except Exception as e:
            return f"Error: {str(e)}"

    def pull_repo(self, dir_path):
        try:
            repo = Repo(dir_path)
            origin = repo.remotes.origin
            origin.pull()
            return "Successfully pulled changes from repository."
        except Exception as e:
            return f"Error: {str(e)}"

    def push_repo(self, dir_path):
        try:
            repo = Repo(dir_path)
            origin = repo.remotes.origin
            origin.push()
            return "Successfully pushed changes to repository."
        except Exception as e:
            return f"Error: {str(e)}"

    def execute_code(self, file_path):
        try:
            subprocess.run(["python", file_path])
        except Exception as e:
            return f"Error executing code: {str(e)}"
        return f"Successfully executed code from file '{file_path}'."

    async def call(self, goal, task, input_str, *args, **kwargs):
        if task == "read_file":
            file_path = kwargs.get("file_path")
            return self.read_file(file_path)
        elif task == "write_file":
            file_path = kwargs.get("file_path")
            content = kwargs.get("content")
            return self.write_file(file_path, content)
        elif task == "clone_repo":
            repo_url = kwargs.get("repo_url")
            dir_path = kwargs.get("dir_path")
            return self.clone_repo(repo_url, dir_path)
        elif task == "pull_repo":
            dir_path = kwargs.get("dir_path")
            return self.pull_repo(dir_path)
        elif task == "push_repo":
            dir_path = kwargs.get("dir_path")
            return self.push_repo(dir_path)
        elif task == "execute_code":
            file_path = kwargs.get("file_path")
            return self.execute_code(file_path)
        else:
            return f"Error: Invalid task '{task}' provided."
