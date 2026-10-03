"""Audit the NeurIPS minimal metadata profile and its actual local files.

This complements MLCommons format validation. It does not certify construct
validity, author provenance statements, privacy review, or full data release.
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

MIN_RAI = (
    "rai:dataLimitations", "rai:dataBiases", "rai:personalSensitiveInformation",
    "rai:dataUseCases", "rai:dataSocialImpact", "rai:hasSyntheticData",
    "prov:wasDerivedFrom", "prov:wasGeneratedBy",
)


def has_content(value):
    if isinstance(value, bool):
        return True
    if isinstance(value, str):
        return bool(value.strip()) and not re.search(r"AUTHOR INPUT|TODO|TBD", value, re.I)
    if isinstance(value, (dict, list)):
        return bool(value) and all(has_content(v) for v in (value.values() if isinstance(value, dict) else value))
    return value is not None


def local_path(root, content_url):
    """Resolve a Hugging Face file URL only within the supplied data root."""
    parsed = urlparse(content_url)
    marker = "/resolve/"
    if marker not in parsed.path:
        raise ValueError("This example expects direct Hugging Face /resolve/<revision>/<path> URLs")
    _, tail = parsed.path.split(marker, 1)
    relative = tail.split("/", 1)[1]
    target = (Path(root).resolve() / relative).resolve()
    if not target.is_relative_to(Path(root).resolve()):
        raise ValueError("File URL escapes the supplied data root")
    return target


def audit(metadata_path, data_root=None):
    document = json.loads(Path(metadata_path).read_text())
    checks = []
    def add(name, passed, detail, status=None):
        checks.append({"check": name, "status": status or ("pass" if passed else "fail"), "detail": detail})

    for name in MIN_RAI:
        value = document.get(name)
        ok = has_content(value)
        if name == "rai:hasSyntheticData":
            ok = isinstance(value, bool)
        add(name, ok, "Presence/type only; human verification of the content is separate.")
    for name in ("name", "url", "license", "conformsTo", "distribution", "recordSet"):
        add("core:" + name, has_content(document.get(name)), "Required core component is present.")
    context = document.get("@context", {})
    add("jsonld_default_vocabulary", isinstance(context, dict) and context.get("@vocab") == "https://schema.org/",
        "Bare schema properties must expand correctly; a visible JSON name alone is insufficient.")
    for term in ("recordSet", "field", "source", "extract", "fileObject", "column", "dataType", "conformsTo"):
        add("context:" + term, isinstance(context, dict) and term in context,
            "Core terms need the official Croissant JSON-LD bindings.")

    resources = {x.get("@id"): x for x in document.get("distribution", [])}
    mapping = {}
    for rid, resource in resources.items():
        url = resource.get("contentUrl", "")
        add("immutable_url:" + str(rid), bool(re.search(r"/resolve/[0-9a-f]{40}/", url)), url)
        if data_root is None:
            add("file_bytes:" + str(rid), False, "No local data root supplied.", "not_evaluated")
            continue
        try:
            path = local_path(data_root, url)
            mapping[rid] = path
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            add("file_sha256:" + str(rid), digest == resource.get("sha256"), str(path))
        except Exception as exc:
            add("file_sha256:" + str(rid), False, str(exc))

    try:
        import mlcroissant as mlc
        import importlib.metadata
        dataset = mlc.Dataset(jsonld=document, mapping=mapping or None)
        issues = dataset.metadata.issues
        add("mlcommons_format", not issues.errors, str(issues))
        loader_version = importlib.metadata.version("mlcroissant")
    except ImportError:
        loader_version = None
        add("mlcommons_format", False, "Install the pinned metadata environment before claiming validation.", "not_evaluated")
    except Exception as exc:
        loader_version = None
        add("mlcommons_format", False, f"{type(exc).__name__}: {exc}")

    if data_root is not None:
        try:
            import pyarrow as pa
            import pyarrow.parquet as pq
            for record in document.get("recordSet", []):
                rid = record.get("@id")
                fields = record.get("field", [])
                if not fields:
                    add("fields:" + str(rid), False, "Empty record set")
                    continue
                source_id = fields[0].get("source", {}).get("fileObject", {}).get("@id")
                resource = resources.get(source_id, {})
                path = local_path(data_root, resource.get("contentUrl", ""))
                schema = pq.read_schema(path)
                columns = [f.get("source", {}).get("extract", {}).get("column") for f in fields]
                add("columns:" + str(rid), set(columns) == set(schema.names),
                    f"declared {len(columns)}; actual {len(schema.names)}")
                for field in fields:
                    name = field.get("source", {}).get("extract", {}).get("column")
                    if name not in schema.names:
                        continue
                    typ = schema.field(name).type
                    allowed = ({"sc:Boolean"} if pa.types.is_boolean(typ) else
                        {"sc:Integer", "sc:Number"} if pa.types.is_integer(typ) else
                        {"sc:Float", "sc:Number"} if pa.types.is_floating(typ) else None)
                    if allowed is not None:
                        add("datatype:" + str(rid) + "/" + name, field.get("dataType") in allowed,
                            f"Parquet {typ}; declared {field.get('dataType')}")
                # Exercise loading, not only parsing. One row is sufficient for
                # a format/access smoke check; it is not a statistical audit.
                if loader_version:
                    try:
                        loaded = next(iter(dataset.records(record_set=rid)))
                        add("loader:" + str(rid), bool(loaded), "Loaded the first record with MLCommons and local pinned bytes.")
                    except Exception as exc:
                        add("loader:" + str(rid), False, f"{type(exc).__name__}: {exc}")
        except ImportError:
            add("parquet_schema", False, "pyarrow is not installed.", "not_evaluated")
        except Exception as exc:
            add("parquet_schema", False, f"{type(exc).__name__}: {exc}")

    counts = {state: sum(x["status"] == state for x in checks) for state in ("pass", "fail", "not_evaluated")}
    return {
        "metadata_sha256": hashlib.sha256(Path(metadata_path).read_bytes()).hexdigest(),
        "mlcroissant_version": loader_version,
        "scope": "minimal profile, JSON-LD format and first-row access; no scientific or author certification",
        "data_root_supplied": data_root is not None,
        "checks": checks, "counts": counts,
        "passed": counts["fail"] == 0 and counts["not_evaluated"] == 0,
        "human_content_review": "not evaluated",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--data-root")
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    report = audit(args.metadata, args.data_root)
    output = Path(args.report)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in ("passed", "counts", "scope")}, indent=2))
    sys.exit(0 if report["passed"] else 1)
