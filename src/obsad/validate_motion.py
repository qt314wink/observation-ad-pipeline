from __future__ import annotations

from pathlib import Path
import re

import yaml

from obsad.motion_reference import validate_motion_reference


REQUIRED_DIMENSIONS = {
    "symmetry", "radial-topology", "phase-change", "morphing",
    "alignment", "frequency-behavior", "splice-points", "musical-synchronization",
}
MEASURED_FIELDS = {"sha256", "bytes", "durationSeconds", "width", "height", "fps", "codec"}


def validate_motion_fixture(path: Path, root: Path) -> list[str]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    errors: list[str] = []
    sources = data.get("sources", [])
    taxonomy = set(data.get("taxonomy", []))
    if taxonomy != REQUIRED_DIMENSIONS:
        errors.append("taxonomy must contain exactly the eight governed dimensions")
    if len(sources) != 4:
        errors.append("fixture must declare exactly four sources")
    ids = [item.get("id") for item in sources]
    paths = [item.get("path") for item in sources]
    if len(set(ids)) != len(ids) or len(set(paths)) != len(paths):
        errors.append("source ids and paths must be unique")
    attrs = (root / ".gitattributes").read_text(encoding="utf-8") if (root / ".gitattributes").exists() else ""
    if not re.search(r"input/videos/\*\.mp4\s+filter=lfs", attrs):
        errors.append("input/videos/*.mp4 must be tracked by Git LFS")
    for source in sources:
        status = source.get("evidenceStatus")
        if not str(source.get("path", "")).startswith("input/videos/"):
            errors.append(f"{source.get('id')}: source path must be under input/videos")
        if status == "pending-source-verification":
            for field in sorted(MEASURED_FIELDS):
                if field in source:
                    errors.append(f"{source.get('id')}: pending source cannot claim measured field {field}")
            if source.get("observations"):
                errors.append(f"{source.get('id')}: pending source cannot contain observations")
        elif status != "verified":
            errors.append(f"{source.get('id')}: unsupported evidenceStatus")
    return errors
