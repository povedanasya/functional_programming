"""Запускає ruff, black, mypy і pytest окремо для кожної labNN/."""

import subprocess
import sys
from pathlib import Path

COMMANDS = (
    ["ruff", "check", "."],
    ["black", "--check", "."],
    ["mypy", "--strict", "."],
    ["pytest", "-q"],
)


def main() -> int:
    """Повертає 0, якщо всі перевірки всіх лаб зелені."""
    failed = 0
    for lab in sorted(Path(__file__).parent.glob("lab0*")):
        for cmd in COMMANDS:
            result = subprocess.run([sys.executable, "-m", *cmd], cwd=lab)
            status = "ok" if result.returncode == 0 else "FAIL"
            failed += result.returncode != 0
            print(f"[{lab.name}] {' '.join(cmd)}: {status}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
