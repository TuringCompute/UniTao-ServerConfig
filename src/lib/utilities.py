import json
import subprocess

class Util:
    def read_json_file(file_path):
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                return data
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: The file '{file_path}' was not found.")
        except json.JSONDecodeError:
            raise json.JSONDecodeError(f"Error: The file '{file_path}' is not a valid JSON file.")
        

    def run_command(command: str):
        cmd_list = command.split()
        try:
            result = subprocess.run(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                raise SystemError(f"Error: command [{command}] run failed with error:{result.stderr}")
            return result
        except Exception as e:
            raise SystemError(f"Error: Command [{command}] got an error: {e}")
