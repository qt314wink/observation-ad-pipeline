from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = ROOT / "config" / "motion-program-semantics-authority.yaml"


class MotionSemanticAuthorityTest(unittest.TestCase):
    def test_motion_oracle_authority_is_immutable_and_explicit(self) -> None:
        data = yaml.safe_load(AUTHORITY.read_text(encoding="utf-8"))
        self.assertEqual("Motion Oracle", data["system"])
        self.assertEqual("semantic_authority", data["role"])
        self.assertEqual("MelodicBloom/melodyfire", data["repository"])
        self.assertEqual(
            "client/src/content/motion-oracle/generativeMotionGrammar.ts",
            data["path"],
        )
        self.assertRegex(data["commit"], re.compile(r"^[0-9a-f]{40}$"))
        self.assertEqual("provisional-pending-upstream-merge", data["status"])

    def test_local_authority_does_not_claim_upstream_semantic_ownership(self) -> None:
        data = yaml.safe_load(AUTHORITY.read_text(encoding="utf-8"))
        upstream = set(data["owned_fields"])
        local = set(data["local_authority"])
        self.assertTrue("motion grammar identifiers and meanings" in upstream)
        self.assertTrue("provider compilation" in local)
        self.assertTrue("calibration programs" in local)
        self.assertTrue(data["prohibited_local_redefinition"])


if __name__ == "__main__":
    unittest.main()
