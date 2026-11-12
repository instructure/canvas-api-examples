"""Print every Canvas endpoint the recipes call, one "METHOD /path" per line.

    python scripts/list_apis.py

The api-docu-portal repo runs this and compares the list with the Canvas OpenAPI spec.

The list comes from the recipe tests: it runs them and records every endpoint the
recipes choose (see record_sent_requests in tests/conftest.py).
"""

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API_PREFIX = "/api/v1/"
FIXED_SEGMENT = re.compile(r"[a-z_]+")  # Canvas path words: courses, student_view_student


def normalize(path):
    """Replace every path parameter (a number, a slug like demo-page) with {id}."""
    segments = path[len(API_PREFIX):].split("/")
    return API_PREFIX + "/".join(s if FIXED_SEGMENT.fullmatch(s) else "{id}" for s in segments)


def record_requests():
    """Run the recipe tests and return the (method, path) lines they recorded."""
    with tempfile.TemporaryDirectory() as folder:
        record = Path(folder) / "requests.txt"
        env = {**os.environ, "USED_APIS_RECORD": str(record)}
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/test_recipes.py", "-q"], cwd=ROOT, env=env, stdout=sys.stderr
        )
        if result.returncode != 0:
            sys.exit("The recipe tests failed, so the list could not be built.")
        return record.read_text().splitlines()


def build_list():
    endpoints = set()
    for line in record_requests():
        method, path = line.split(" ", 1)
        endpoints.add(f"{method} {normalize(path)}")
    return "".join(f"{e}\n" for e in sorted(endpoints))


def main():
    sys.stdout.write(build_list())
    return 0


if __name__ == "__main__":
    sys.exit(main())
