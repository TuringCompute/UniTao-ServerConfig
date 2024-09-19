import sys
import json
import subprocess

class Util:
    def read_json_file(file_path):
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                return data
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found.")
            sys.exit(-2)
        except json.JSONDecodeError:
            print(f"Error: The file '{file_path}' is not a valid JSON file.")
            sys.exit(-3)

    def run_command(command: str):
        cmd_list = command.split()
        try:
            result = subprocess.run(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                print(f"Error: command [{command}] run failed with error:{result.stderr}")
                sys.exit(-9)
            return result
        except Exception as e:
            print(f"Error: Command [{command}] got an error: {e}")
            sys.exit(-8)
