"""Apply reviewed first-edition layout edits using exact, unique anchors.

Each replacement is checked independently. Already-applied edits are skipped;
unknown or ambiguous text is rejected. Unrelated user changes are preserved.
"""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]


def main():
    entries = json.loads((ROOT / 'book/release_edits.json').read_text(encoding='utf-8'))
    audit = []
    for entry in entries:
        relative = Path(entry['path'])
        if relative.is_absolute() or '..' in relative.parts or relative.parts[0] not in {'book', 'scripts'}:
            raise ValueError('Invalid editorial target')
        target = ROOT / relative
        text = target.read_text(encoding='utf-8')
        before = hashlib.sha256(text.encode('utf-8')).hexdigest()
        applied = 0
        for change in entry['changes']:
            old, new = change['old'], change['new']
            if old == new:
                continue
            # Some replacements contain their old text as a prefix. Check the
            # complete replacement first so repeated builds remain idempotent.
            if text.count(new) == 1:
                continue
            if text.count(old) != 1:
                raise ValueError(f'Unknown or ambiguous edit anchor: {relative}')
            text = text.replace(old, new, 1)
            applied += 1
        after = hashlib.sha256(text.encode('utf-8')).hexdigest()
        if applied:
            target.write_text(text, encoding='utf-8')
        audit.append({'path': str(relative), 'before': before, 'after': after, 'edits_applied': applied})
        print(f'{relative}: {applied} reviewed edits applied')
    (ROOT / 'build').mkdir(exist_ok=True)
    (ROOT / 'build/editorial-verification.json').write_text(
        json.dumps(audit, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
