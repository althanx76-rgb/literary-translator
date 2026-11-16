#!/usr/bin/env python3
"""Consistency checks for the repository (run by the tests and by CI).

- SKILL.md frontmatter respects the Agent Skills limits (name, description), and SKILL.md stays under 500 lines.
- The languages listed in SKILL.md and in the README table match the language files on disk.
- Every language file has a status line and stays compact (it is loaded every time its language is used).
- Every file path that SKILL.md mentions exists.
- The version in SKILL.md matches the latest CHANGELOG entry; plugin and marketplace manifests agree.
- Prints how many characters each language pair loads (SKILL.md + source file + target file).
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills' / 'literary-translator'
MAX_LANGUAGE_FILE = 12000  # characters


def codes_on_disk(role):
    return {p.stem for p in (SKILL / 'languages' / role).glob('*.md') if not p.name.startswith('_')}


def main():
    errors = []
    text = (SKILL / 'SKILL.md').read_text(encoding='utf-8')
    m = re.match(r'---\n(.*?)\n---\n', text, re.S)
    if not m:
        sys.exit('SKILL.md: missing frontmatter')
    fields = dict(line.split(': ', 1) for line in m.group(1).splitlines() if ': ' in line)
    name, description = fields.get('name', '').strip('"'), fields.get('description', '').strip('"')
    if not re.fullmatch(r'[a-z0-9-]{1,64}', name) or 'anthropic' in name or 'claude' in name:
        errors.append(f'name "{name}" breaks the naming rules')
    if name != SKILL.name:
        errors.append(f'name "{name}" differs from the folder name "{SKILL.name}"')
    if not description or len(description) > 1024 or re.search('[<>]', description):
        errors.append(f'description must be 1-1024 characters without < or > (now {len(description)})')
    if text.count('\n') >= 500:
        errors.append(f'SKILL.md has {text.count(chr(10))} lines (keep it under 500)')

    # Languages: SKILL.md list, README table, files on disk
    available = re.search(r'Available now: source (.*?); target (.*?)\. ', text)
    if not available:
        errors.append('SKILL.md lacks the line "Available now: source `xx`; target `yy`, `zz`. "')
    listed = {'source': set(re.findall(r'`([a-z-]+)`', available.group(1))),
              'target': set(re.findall(r'`([a-z-]+)`', available.group(2)))} if available else {}
    readme = (ROOT / 'README.md').read_text(encoding='utf-8')
    table = readme.split('## Languages', 1)[-1].split('\n## ', 1)[0]
    for role in ('source', 'target'):
        on_disk = codes_on_disk(role)
        if listed.get(role) != on_disk:
            errors.append(f'SKILL.md lists {role} {sorted(listed.get(role, []))}, files are {sorted(on_disk)}')
        for code in sorted(on_disk):
            path = SKILL / 'languages' / role / f'{code}.md'
            body = path.read_text(encoding='utf-8')
            if not re.search(rf'^\| `{code}` \|', table, re.M):
                errors.append(f'README.md language table lacks `{code}`')
            if not re.search(r'^> Status: ', body, re.M):
                errors.append(f'{path.relative_to(ROOT)} lacks the "> Status:" line')
            if len(body) > MAX_LANGUAGE_FILE:
                errors.append(f'{path.relative_to(ROOT)} has {len(body)} characters (limit {MAX_LANGUAGE_FILE}): '
                              'keep language files compact, they are loaded on every use of the language')

    for path in sorted(set(re.findall(r'`((?:languages|scripts|templates)/[\w./-]+\.\w+)`', text))):
        if not (SKILL / path).exists():
            errors.append(f'SKILL.md mentions {path}, which does not exist')

    # Versions and manifests
    version = re.search(r'\*\*Version (\d+\.\d+\.\d+)\.\*\*', text)
    latest = re.search(r'^## (\d+\.\d+\.\d+)', (ROOT / 'CHANGELOG.md').read_text(encoding='utf-8'), re.M)
    if not version or not latest or version.group(1) != latest.group(1):
        errors.append(f'SKILL.md version {version and version.group(1)} differs from the latest CHANGELOG entry '
                      f'{latest and latest.group(1)}')
    plugin = json.loads((ROOT / '.claude-plugin' / 'plugin.json').read_text(encoding='utf-8'))
    market = json.loads((ROOT / '.claude-plugin' / 'marketplace.json').read_text(encoding='utf-8'))
    entries = [e for e in market.get('plugins', []) if e.get('name') == plugin.get('name')]
    if plugin.get('name') != SKILL.name or len(entries) != 1:
        errors.append('plugin.json name and the marketplace entry name must both be ' + SKILL.name)
    elif entries[0].get('source') != './':
        errors.append('the marketplace entry source must be "./" (the plugin is the repository root)')
    if 'version' in plugin or any('version' in e for e in entries):
        errors.append('no "version" in plugin.json or marketplace.json: users then track the commits '
                      '(the version lives in SKILL.md and CHANGELOG.md)')

    core = len(text)
    print(f'SKILL.md: {core} characters')
    for s in sorted(codes_on_disk('source')):
        src = len((SKILL / 'languages' / 'source' / f'{s}.md').read_text(encoding='utf-8'))
        for t in sorted(codes_on_disk('target')):
            tgt = len((SKILL / 'languages' / 'target' / f'{t}.md').read_text(encoding='utf-8'))
            print(f'{s} -> {t}: {core + src + tgt} characters loaded ({src + tgt} from the two language files)')
    if errors:
        print('\n'.join('ERROR: ' + e for e in errors))
        sys.exit(1)
    print('repository consistent')


if __name__ == '__main__':
    main()
