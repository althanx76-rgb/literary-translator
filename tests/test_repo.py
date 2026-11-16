"""The repository stays consistent, and the skill zip has the layout the Claude apps expect."""
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_check_repo_passes():
    result = subprocess.run([sys.executable, str(ROOT / 'tools' / 'check_repo.py')], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


def test_skill_zip_has_the_skill_folder_at_its_root():
    subprocess.run([sys.executable, str(ROOT / 'tools' / 'build_zip.py')], check=True, capture_output=True)
    names = zipfile.ZipFile(ROOT / 'dist' / 'literary-translator.zip').namelist()
    assert 'literary-translator/SKILL.md' in names
    assert 'literary-translator/scripts/check_translation.py' in names
    assert all(n.startswith('literary-translator/') for n in names)
    assert not any('/_' in n or n.endswith('.pyc') for n in names)
    with zipfile.ZipFile(ROOT / 'dist' / 'literary-translator.zip') as z:
        assert z.read('literary-translator/LICENSE') == (ROOT / 'LICENSE').read_bytes()
