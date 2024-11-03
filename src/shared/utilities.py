import json
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
        try:
            process = subprocess.Popen(cmd_list,
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
                raise SystemError(f"Error: command [{command}] run failed with error:{return_code}")
            return ProcessResult(return_code, stdout_lines, stderr_output)
        except Exception as e:
            raise SystemError(f"Error: Command [{command}] got an error: {e}")
