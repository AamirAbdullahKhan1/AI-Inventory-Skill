"""Copy only manifest-held-out members to a new directory outside the workspace."""
import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]


def seal(archive_path, destination):
    destination = destination.resolve()
    if destination.is_relative_to(ROOT) or ROOT.is_relative_to(destination):
        raise ValueError("Destination must be a separate directory outside the workspace")
    census = json.loads((ROOT / "reports/census.json").read_text(encoding="utf-8"))
    if hashlib.sha256(archive_path.read_bytes()).hexdigest() != census["archive_sha256"]:
        raise ValueError("Archive does not match the recorded split")
    expected = {(row["docx_sha256"], row["key_sha256"]) for row in census["test"]}
    members = []
    with ZipFile(archive_path) as archive:
        manifest = json.loads(archive.read("corpus-manifest.json"))
        for row in manifest["documents"]:
            if row["split"] != "test":
                continue
            document_id = row["id"]
            if not document_id.replace("-", "").isalnum():
                raise ValueError("Unsafe manifest member identifier")
            names = (document_id + ".docx", document_id + ".answer-key.json")
            blobs = [archive.read(name) for name in names]
            fingerprints = tuple(hashlib.sha256(blob).hexdigest() for blob in blobs)
            if fingerprints not in expected:
                raise ValueError("Held-out member does not match the recorded split")
            expected.remove(fingerprints)
            members.extend(zip(names, blobs))
    if expected:
        raise ValueError("Held-out manifest is incomplete")
    destination.mkdir(mode=0o700)
    for name, blob in members:
        with (destination / name).open("xb") as output:
            output.write(blob)
    return len(members)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("new_destination", type=Path)
    args = parser.parse_args()
    print(f"Copied {seal(args.archive, args.new_destination)} verified held-out members.")
