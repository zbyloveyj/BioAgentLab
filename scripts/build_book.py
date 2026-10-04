"""Build a conventional Chinese book with Pandoc and XeLaTeX.

Requires pandoc, xelatex, ctex, Noto CJK, Liberation and DejaVu system fonts.
No font files are copied into the repository or release archive.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PREAMBLE = r'''\documentclass[UTF8,11pt,openany,twoside,fontset=none]{ctexbook}
\usepackage[a5paper,inner=19mm,outer=16mm,top=19mm,bottom=19mm,headheight=14pt,headsep=7mm]{geometry}
\setmainfont{Liberation Serif}
\setsansfont{Liberation Sans}
\setmonofont{DejaVu Sans Mono}[Scale=0.80]
\setCJKmainfont{Noto Serif CJK SC}
\setCJKsansfont{Noto Sans CJK SC}
\setCJKmonofont{Noto Sans Mono CJK SC}
\usepackage{amsmath,amssymb,booktabs,longtable,array,calc}
\usepackage{graphicx,xcolor,fvextra,fancyhdr,setspace,enumitem,xurl,hyperref,bookmark}
\definecolor{ink}{HTML}{263B48}
\definecolor{muted}{HTML}{62727C}
\hypersetup{unicode=true,colorlinks=true,linkcolor=ink,urlcolor=ink,pdftitle={AI Agent for Biology：生物科研智能体原理与实践},pdfauthor={BioAgentLab},pdfsubject={中文教学版}}
\setcounter{secnumdepth}{-1}
\setcounter{tocdepth}{0}
\setstretch{1.40}
\setlength{\parindent}{2em}
\setlength{\parskip}{0.25em}
\setlist{nosep,leftmargin=2em}
\emergencystretch=2em
\setlength{\LTpre}{0.6em}
\setlength{\LTpost}{0.6em}
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\DefineVerbatimEnvironment{verbatim}{Verbatim}{fontsize=\small,breaklines=true,breakanywhere=true,breaksymbolleft={},baselinestretch=1.0,frame=leftline,rulecolor=\color{muted},framesep=3mm}
\ctexset{chapter={format=\sffamily\Large\bfseries\raggedright,beforeskip=8pt,afterskip=20pt},section={format=\sffamily\normalsize\bfseries,beforeskip=14pt,afterskip=5pt},subsection={format=\sffamily\normalsize\bfseries}}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[LE]{\small\sffamily\color{muted}AI AGENT FOR BIOLOGY}
\fancyhead[RO]{\small\sffamily\color{muted}\nouppercase{\leftmark}}
\fancyfoot[LE,RO]{\small\thepage}
\renewcommand{\headrulewidth}{0.2pt}
\fancypagestyle{plain}{\fancyhf{}\fancyfoot[LE,RO]{\small\thepage}\renewcommand{\headrulewidth}{0pt}}
\renewcommand{\chaptermark}[1]{\markboth{#1}{}}
\let\cleardoublepage\clearpage
\begin{document}
\frontmatter
\begin{titlepage}
\thispagestyle{empty}
\vspace*{12mm}
{\sffamily\small\color{muted} BIOAGENTLAB / 中文教学版}\par
\vspace{21mm}
{\sffamily\fontsize{29}{35}\selectfont\bfseries AI Agent\\[3mm]for Biology}\par
\vspace{11mm}
{\sffamily\Large\bfseries 生物科研智能体\par 原理与实践}\par
\vspace{9mm}
{\large 从语言模型、工具调用与证据检索\par 到微生物—代谢物—宿主单细胞研究}\par
\vfill
{\sffamily\small 2026 年 10 月\par 理论 · 代码 · 案例 · 练习}
\end{titlepage}
\chapter*{版本与使用说明}
本书是 BioAgentLab 的教学版本。离线例子、合成数据和示例假设用于学习与测试，不代表真实生物医学研究发现。真实数据分析、外部服务调用与临床使用需要另行验证和审批。\par
教材源文件、完整代码、测试与构建脚本保存在配套仓库。正文中的参考资料使用 R 编号，具体版本与入口列于书末。软件接口可能变化，使用时应核对实际环境。\par
本书不包含可重新分发的字体文件，也不重新发布受限制的论文全文。源码与内容的许可状态以仓库说明为准。\par
\url{https://github.com/zbyloveyj/BioAgentLab}
'''


def convert(paths: list[Path], dest: Path) -> str:
    dest.write_text('\n\n'.join(p.read_text(encoding='utf-8') for p in paths), encoding='utf-8')
    out = subprocess.run(['pandoc', str(dest), '--from=markdown', '--to=latex',
                          '--top-level-division=chapter', '--no-highlight'],
                         check=True, capture_output=True, text=True).stdout
    def wrap_inline(match):
        value = match.group(1).replace(r'\_', r'\_\allowbreak{}')
        value = value.replace('/', r'/\allowbreak{}').replace('-', r'-\allowbreak{}')
        return r'\texttt{' + value + '}'
    return re.sub(r'\\texttt\{([^{}]*)\}', wrap_inline, out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--min-pages', type=int, default=0)
    args = parser.parse_args()
    for tool in ('pandoc', 'xelatex'):
        if not shutil.which(tool):
            raise SystemExit(f'Missing executable: {tool}')
    build = ROOT / 'build/book'
    build.mkdir(parents=True, exist_ok=True)
    sources = sorted((ROOT / 'book/zh').glob('*.md'))
    if not sources:
        raise SystemExit('No book sources')
    prefaces = [p for p in sources if p.name.startswith('00_')]
    chapters = [p for p in sources if p not in prefaces]
    preface_tex = convert(prefaces, build/'preface.md') if prefaces else ''
    body_tex = convert(chapters, build/'body.md')
    tex = PREAMBLE + preface_tex + '\n\\tableofcontents\n\\mainmatter\n' + body_tex + '\n\\end{document}\n'
    (build/'book.tex').write_text(tex, encoding='utf-8')
    for i in range(3):
        run = subprocess.run(['xelatex', '-interaction=nonstopmode', '-halt-on-error', 'book.tex'],
                             cwd=build, capture_output=True, text=True)
        (build/f'compile-{i}.log').write_text(run.stdout + run.stderr, encoding='utf-8')
        if run.returncode:
            raise SystemExit(run.stdout[-6000:])
    out = ROOT/'docs/pdf'
    out.mkdir(parents=True, exist_ok=True)
    target = out/'AI_Agent_for_Biology_ZH.pdf'
    shutil.copyfile(build/'book.pdf', target)
    import fitz
    with fitz.open(target) as doc:
        pages = len(doc)
        bookmarks = len(doc.get_toc())
    full = '\n'.join(p.read_text(encoding='utf-8') for p in sources)
    info = {'pages': pages, 'bookmarks': bookmarks, 'source_files': len(sources),
            'core_chapters': len([p for p in sources if re.match(r'(0[1-9]|[12][0-9]|3[0-2])_', p.name)]),
            'labs': len([p for p in sources if re.match(r'4[0-9]_lab', p.name)]),
            'chinese_characters': len(re.findall(r'[\u4e00-\u9fff]', full)),
            'source_characters': len(full),
            'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
            'format': 'A5, 11pt, single-column, Chinese serif body, mirrored margins',
            'edition': '2026-10 teaching edition'}
    (out/'AI_Agent_for_Biology_ZH.build.json').write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding='utf-8')
    index = ['# AI Agent for Biology：中文教材', '',
             '[下载 PDF](../docs/pdf/AI_Agent_for_Biology_ZH.pdf)', '',
             '32章正文、10项实训、术语、接口、故障排查与参考资料。', '', '## 目录', '']
    for source in sources:
        title = source.read_text(encoding='utf-8').splitlines()[0].lstrip('# ').strip()
        index.append(f'- [{title}](zh/{source.name})')
    (ROOT/'book/README.md').write_text('\n'.join(index)+'\n', encoding='utf-8')
    print(json.dumps(info, ensure_ascii=False, indent=2))
    if pages < args.min_pages:
        raise SystemExit(f'Page target not met: {pages} < {args.min_pages}')


if __name__ == '__main__':
    main()
