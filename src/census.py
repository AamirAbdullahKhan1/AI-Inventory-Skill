import argparse
import hashlib
import io
import json
from pathlib import Path
from xml.etree import ElementTree
from zipfile import ZipFile

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def census(data):
    with ZipFile(io.BytesIO(data)) as docx:
        root = ElementTree.fromstring(docx.read("word/document.xml"))
        styles = ElementTree.fromstring(docx.read("word/styles.xml"))
        counts = {}
        for name, tag in {
            "tables": "tbl", "vertical_merge_markers": "vMerge",
            "direct_numbering_markers": "numPr", "drawing_markers": "drawing",
            "legacy_picture_markers": "pict", "declared_header_rows": "tblHeader",
            "text_boxes": "txbxContent", "footnote_references": "footnoteReference",
        }.items():
            counts[name] = sum(1 for _ in root.iter(W + tag))
        counts["horizontal_spans"] = sum(
            int(node.get(W + "val", "1")) > 1 for node in root.iter(W + "gridSpan")
        )
        heading_styles = {
            s.get(W + "styleId") for s in styles.iter(W + "style")
            if s.find(f"./{W}pPr/{W}outlineLvl") is not None
        }
        counts["heading_markers"] = sum(
            p.find(f"./{W}outlineLvl") is not None
            or any(s.get(W + "val") in heading_styles for s in p.findall(W + "pStyle"))
            for p in root.iter(W + "pPr")
        )
        counts["numbered_styles"] = sum(1 for _ in styles.iter(W + "numPr"))
        counts["comments"] = 0
        if "word/comments.xml" in docx.namelist():
            comments = ElementTree.fromstring(docx.read("word/comments.xml"))
            counts["comments"] = sum(1 for _ in comments.iter(W + "comment"))
        counts["revision_markers"] = sum(
            n.tag.startswith(W) and (
                n.tag.endswith("Change") or n.tag[len(W):] in {"ins", "del", "moveFrom", "moveTo"}
            ) for n in root.iter()
        )
        # Count only. No document text is emitted or interpreted.
        counts["body_utf8_bytes"] = sum(len((n.text or "").encode()) for n in root.iter(W + "t"))
        counts["source_token_estimate"] = round(counts["body_utf8_bytes"] / 4)
        counts["file_bytes"] = len(data)
        return counts


def inspect_archive(path):
    result = {"archive_sha256": digest(path.read_bytes()), "dev": [], "test": []}
    families = {}
    with ZipFile(path) as archive:
        manifest = json.loads(archive.read("corpus-manifest.json"))
        for row in manifest["documents"]:
            document_id = row["id"]
            family, level = document_id.rsplit("-", 1)
            split = row["split"]
            if families.setdefault(family, split) != split:
                raise ValueError("Family crosses split boundary")
            docx = archive.read(document_id + ".docx")
            key = archive.read(document_id + ".answer-key.json")
            entry = {"docx_sha256": digest(docx), "key_sha256": digest(key), "census": census(docx)}
            if split == "dev":
                entry.update(id=document_id, domain=row["domain"], complexity=level)
            result[split].append(entry)
    if [len(result[k]) for k in ("dev", "test")] != [15, 15]:
        raise ValueError("Unexpected split sizes")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.write_text(json.dumps(inspect_archive(args.archive), indent=2) + "\n", encoding="utf-8")
