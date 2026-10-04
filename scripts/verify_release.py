"""Run tests and verify built teaching artifacts. No network model is invoked."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import fitz

ROOT=Path(__file__).resolve().parents[1]


def main():
    build=ROOT/'build'; build.mkdir(exist_ok=True)
    subprocess.run([sys.executable,'-m','pytest','-q','--junitxml='+str(build/'test-results.xml')],cwd=ROOT,check=True)
    suites=ET.parse(build/'test-results.xml').getroot()
    cases=suites.findall('.//testcase')
    failures=len(suites.findall('.//failure'))+len(suites.findall('.//error'))
    skipped=len(suites.findall('.//skipped'))
    if failures: raise SystemExit('Tests failed')
    notebook_info=json.loads((build/'notebook_verification.json').read_text())
    if notebook_info['executed']!=8: raise SystemExit('Eight executed notebooks required')
    pdf=ROOT/'docs/pdf/AI_Agent_for_Biology_ZH.pdf'
    info=json.loads((ROOT/'docs/pdf/AI_Agent_for_Biology_ZH.build.json').read_text())
    with fitz.open(pdf) as doc:
        if len(doc)<200: raise SystemExit('Book must contain at least 200 pages')
        if len(doc)!=info['pages']: raise SystemExit('PDF metadata page mismatch')
        if len(doc.get_toc())<40: raise SystemExit('Missing PDF navigation')
        blank=[]
        edge=[]
        for i,page in enumerate(doc):
            if not page.get_text().strip(): blank.append(i+1)
            for block in page.get_text('blocks'):
                if len(block)>6 and block[6]!=0: continue
                if block[0]<5 or block[2]>page.rect.width-5 or block[1]<0 or block[3]>page.rect.height:
                    edge.append(i+1)
        pdf_audit={'pages':len(doc),'bookmarks':len(doc.get_toc()),
                   'blank_pages':blank,'text_near_physical_edges':sorted(set(edge))}
    if blank or edge: raise SystemExit('PDF has blank pages or text outside safe physical bounds')
    log=(build/'book/book.log').read_text(errors='replace')
    missing=[line for line in log.splitlines() if 'Missing character:' in line]
    if missing: raise SystemExit('Missing glyphs in PDF build')
    overfull=re.findall(r'Overfull \\hbox \(([0-9.]+)pt too wide\)',log)
    digest=hashlib.sha256(pdf.read_bytes()).hexdigest()
    if digest!=info['sha256']: raise SystemExit('PDF hash mismatch')
    result={'verified_at_utc':datetime.now(timezone.utc).isoformat(),
            'python':platform.python_version(),
            'tests':{'total':len(cases),'passed':len(cases)-skipped,'failed':failures,'skipped':skipped},
            'notebooks':notebook_info,'pdf':pdf_audit,
            'latex_overfull_hbox_widths_pt':[float(x) for x in overfull],
            'pdf_sha256':digest,
            'scope':'offline teaching contracts, numerical examples, fixtures and synthetic workflow',
            'not_validated':['live external model calls','live PubMed service calls','real biological discovery','clinical use'],
            'visual_review':'Automated checks do not replace inspection of rendered pages.'}
    (ROOT/'docs/verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__': main()
