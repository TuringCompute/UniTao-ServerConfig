import json
import os
import subprocess


class ProcessResult:
    stdout: str
    stdout_lines: list[str]
    returncode: int
    stderr: str

    def __init__(self, return_code: int, output_lines: list[str], err: str):
        self.stdout = "".join(output_lines)
        self.stdout_lines = output_lines
        self.returncode = return_code
        self.stderr = err


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

    def run_command(command: str) -> ProcessResult:
        cmd_list = command.split()
        real_cmd_list= []
        for part in cmd_list:
            if part == "":
                continue
            real_cmd_list.append(part.replace("\n", ""))
        try:
            process = subprocess.Popen(real_cmd_list,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        text=True  # Output as strings instead of bytes
                                    )
            # Collect output line-by-line in real time
            stdout_lines = []
            for line in process.stdout:
                print(line, end="")  # Print to console in real time
                stdout_lines.append(line)  # Store line in list for result

            # Collect standard error output
            stderr_output, _ = process.communicate()

            # Wait for the process to complete
            return_code = process.wait()
            if return_code != 0:
                real_cmd_str = " ".join(real_cmd_list)
                raise SystemError(f"command [{real_cmd_str}] run failed with error:{return_code}")
            return ProcessResult(return_code, stdout_lines, stderr_output)
        except Exception as e:
            raise SystemError(f"Error: {e}")
        
    def compare_dict(first: dict, second: dict) -> bool:
        for key in first.keys():
            if key not in second:
                return False
            if first[key] != second[key]:
                return False
        for key in second.keys():
            if key not in first:
                return False
        return True

    # return abspath based on base_path.
    def abs_path(base_path: str, relative_path: str) -> str:
        return os.path.abspath(os.path.join(base_path, relative_path))

    # file_name confain data name.
    # check file exists
    # check ext is .json
    # return data_name
    def file_data_name(file_path: str) -> str:
        file_name = os.path.basename(file_path)
        data_name, file_ext = os.path.splitext(file_name)
        if file_ext!=".json":
            raise ValueError(f"Invalid path, data file should be an json file. got [{file_name}] instead")
        return data_name
