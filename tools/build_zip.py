#!/usr/bin/env python3
"""Builds dist/literary-translator.zip: the skill folder alone, ready to upload as a custom skill.
Files and folders whose name starts with "_" (the contributors' templates, caches) are left out."""
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills' / 'literary-translator'
OUT = ROOT / 'dist' / 'literary-translator.zip'


def main():
    OUT.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
        for f in sorted(SKILL.rglob('*')):
            parts = f.relative_to(SKILL).parts
            if f.is_file() and not any(p.startswith('_') for p in parts) and f.suffix != '.pyc':
                z.write(f, Path(SKILL.name) / f.relative_to(SKILL))
        z.write(ROOT / 'LICENSE', Path(SKILL.name) / 'LICENSE')  # the notice travels with the skill
    print(OUT)


if __name__ == '__main__':
    main()
