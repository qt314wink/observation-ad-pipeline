from __future__ import annotations

import json
from pathlib import Path
import re

import fastjsonschema
import yaml

from obsad.motion_reference import validate_motion_reference


REQUIRED_DIMENSIONS = {
    "symmetry", "radial-topology", "phase-change", "morphing",
    "alignment", "frequency-behavior", "splice-points", "musical-synchronization",
}
MEASURED_FIELDS = {"sha256", "bytes", "durationSeconds", "width", "height", "fps", "codec"}


def validate_motion_fixture(path: Path, root: Path) -> list[str]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        schema = json.loads(
            (root / "schemas/motion-analysis.schema.json").read_text(encoding="utf-8")
        )
        fastjsonschema.compile(schema)(data)
    except (OSError, ValueError, yaml.YAMLError, fastjsonschema.JsonSchemaException) as exc:
        return [f"{path}: schema validation failed: {exc}"]

    errors: list[str] = []
    sources = data["sources"]
    taxonomy = set(data["taxonomy"])
    if taxonomy != REQUIRED_DIMENSIONS:
        errors.append("taxonomy must contain exactly the eight governed dimensions")
    ids = [item["id"] for item in sources]
    paths = [item["path"] for item in sources]
    if len(set(ids)) != len(ids) or len(set(paths)) != len(paths):
        errors.append("source ids and paths must be unique")
    attrs = (root / ".gitattributes").read_text(encoding="utf-8") if (root / ".gitattributes").exists() else ""
    if not re.search(r"input/videos/\*\.mp4\s+filter=lfs", attrs):
        errors.append("input/videos/*.mp4 must be tracked by Git LFS")
    for source in sources:
        if source["evidenceStatus"] == "pending-source-verification":
            for field in sorted(MEASURED_FIELDS):
                if field in source:
                    errors.append(f"{source['id']}: pending source cannot claim measured field {field}")
            if source.get("observations"):
                errors.append(f"{source['id']}: pending source cannot contain observations")
    return errors
