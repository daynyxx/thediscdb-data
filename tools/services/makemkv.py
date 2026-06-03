import subprocess
from typing import Any


class MakeMkv:
    def __init__(self, binary_path: str) -> None:
        self.binary: str = binary_path

    def run(self, args: list[str], timeout: int = 120) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [self.binary] + args,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result

    def info(self, drive_index: int, output_path: str) -> subprocess.CompletedProcess[str]:
        return self.run(["--robot", "--messages=" + output_path, "info", f"disc:{drive_index}"])