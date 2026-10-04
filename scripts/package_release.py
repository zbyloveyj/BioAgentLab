"""Package source, notebooks and book without secrets, caches or font files."""
from pathlib import Path
import shutil
import zipfile

ROOT=Path(__file__).resolve().parents[1]
ALLOWED_DIRS={'book','bioagent','notebooks','examples','tests','scripts','docs','benchmark','workflows','.github'}
ALLOWED_ROOT={'.gitignore','.env.example','pyproject.toml','requirements.txt','README.md','ROADMAP.md','CHANGELOG.md','CONTRIBUTING.md'}
FONT_EXTENSIONS={'.ttf','.otf','.ttc','.woff','.woff2','.pfb','.pfa'}


def main():
    out=ROOT/'dist'; out.mkdir(exist_ok=True)
    target=out/'BioAgentLab_2026_10.zip'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for path in sorted(ROOT.rglob('*')):
            if not path.is_file() or path.is_symlink(): continue
            rel=path.relative_to(ROOT)
            if rel.parts[0] not in ALLOWED_DIRS and str(rel) not in ALLOWED_ROOT: continue
            if any(part in {'__pycache__','.ipynb_checkpoints','.pytest_cache'} for part in rel.parts): continue
            if path.suffix.lower() in FONT_EXTENSIONS|{'.pyc','.pyo'}: continue
            if path.name.startswith('.env') and path.name!='.env.example': continue
            archive.write(path,'BioAgentLab/'+rel.as_posix())
    shutil.copyfile(ROOT/'docs/pdf/AI_Agent_for_Biology_ZH.pdf',out/'AI_Agent_for_Biology_ZH.pdf')
    shutil.copyfile(ROOT/'docs/verification.json',out/'verification.json')
    print(f'Packaged {target} ({target.stat().st_size} bytes)')


if __name__=='__main__': main()
