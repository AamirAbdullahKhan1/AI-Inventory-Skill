"""Scan repository files and git history for configured credential values."""
import base64
import json
from pathlib import Path
import subprocess
from urllib.parse import quote, urlsplit
from azure_probe import settings


ROOT = Path(__file__).resolve().parents[1]


def scan():
    env = settings()
    endpoint = urlsplit(env["AZURE_OPENAI_ENDPOINT"])
    values = [env["AZURE_OPENAI_API_KEY"], endpoint.username, endpoint.password]
    needles = set()
    for value in filter(None, values):
        raw = value.encode()
        needles.update((raw, value.encode("utf-16-le"), quote(value, safe="").encode(),
                        base64.b64encode(raw)))
    count = 0
    matches = 0
    for path in ROOT.rglob("*"):
        if path.is_symlink() or not path.is_file() or path == ROOT / ".env" or ".git" in path.parts:
            continue
        count += 1
        data = path.read_bytes()
        matches += any(needle in data for needle in needles)
    history = subprocess.check_output(["git", "log", "--all", "-p"], cwd=ROOT)
    return {"workspace_files_scanned": count, "workspace_files_with_matches": matches,
            "git_patch_history_matches": any(needle in history for needle in needles),
            "env_excluded": True, "endpoint_userinfo_configured": bool(endpoint.username or endpoint.password)}


if __name__ == "__main__":
    result = scan()
    (ROOT / "reports/secret-scan.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))
