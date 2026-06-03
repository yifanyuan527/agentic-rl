#!/usr/bin/env python3
"""Decode the text-safe Agentic RL PPTX base64 file into an openable PPTX."""
from __future__ import annotations

import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "agentic_rl_survey_cn.pptx.base64"
OUT = ROOT / "agentic_rl_survey_cn.pptx"


def main() -> None:
    OUT.write_bytes(base64.b64decode(SRC.read_text(encoding="ascii")))
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
