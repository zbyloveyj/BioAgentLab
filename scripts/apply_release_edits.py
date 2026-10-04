"""Apply the recorded first-edition layout corrections, idempotently.

This preserves a reviewable record of the final editorial changes. It refuses
unknown source versions rather than overwriting later user modifications.
"""
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]


def main():
    changes=json.loads((ROOT/'book/release_edits.json').read_text(encoding='utf-8'))
    for entry in changes:
        relative=Path(entry['path'])
        if relative.is_absolute() or '..' in relative.parts or relative.parts[0] not in {'book','scripts'}:
            raise ValueError('Invalid editorial target')
        target=ROOT/relative
        text=target.read_text(encoding='utf-8')
        digest=hashlib.sha256(text.encode()).hexdigest()
        if digest==entry['after']:
            continue
        if digest!=entry['before']:
            raise ValueError(f'Unexpected source version: {relative}')
        for change in entry['changes']:
            if text.count(change['old'])!=1:
                raise ValueError(f'Non-unique edit anchor: {relative}')
            text=text.replace(change['old'],change['new'],1)
        if hashlib.sha256(text.encode()).hexdigest()!=entry['after']:
            raise ValueError(f'Edited content checksum mismatch: {relative}')
        target.write_text(text,encoding='utf-8')
        print('Applied reviewed layout edit:',relative)


if __name__=='__main__': main()
