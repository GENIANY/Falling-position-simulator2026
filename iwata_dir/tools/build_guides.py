"""Build TeX guide sources into PDFs and searchable text in a fresh directory.

XeLaTeX must already be on PATH; pypdf is a Python dependency. No installation.
Only --publish copies successfully built selected pairs back into docs.
Rendered-page review is a separate required human/agent check.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess

GUIDES=('THEORY_GUIDE','PROGRAM_GUIDE')


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('root',nargs='?',type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument('--output-dir',type=Path,required=True)
    p.add_argument('--publish',action='store_true')
    p.add_argument('--guide',choices=GUIDES,action='append',help='build only the named guide; repeat to select both (default: both)')
    a=p.parse_args(argv);root=a.root.resolve();out=a.output_dir.resolve()
    if out.exists():p.error('output directory already exists')
    for tool in ('xelatex',):
        if shutil.which(tool) is None:p.error('missing dependency: '+tool)
    try:
        from pypdf import PdfReader
    except ImportError:
        p.error('missing Python dependency: pypdf; use the configured document Python')
    selected=list(dict.fromkeys(a.guide or GUIDES))
    sources=[root/'docs'/(name+'.tex') for name in selected]
    if any(not source.is_file() for source in sources):p.error('missing TeX source')
    out.mkdir(parents=True)
    manifest={'schema':'balloon.guide.build/1','selected_guides':selected,'sources':{},'outputs':{},'warnings':{},'render_review':'required separately'}
    for source in sources:
        manifest['sources'][source.name]=hashlib.sha256(source.read_bytes()).hexdigest()
        for i in range(3):
            run=subprocess.run(['xelatex','-no-shell-escape','-interaction=nonstopmode','-halt-on-error',
                '-output-directory='+out.as_posix(),source.as_posix()],cwd=root,capture_output=True,timeout=180)
            (out/(source.stem+f'-pass{i+1}.stdout')).write_bytes(run.stdout)
            (out/(source.stem+f'-pass{i+1}.stderr')).write_bytes(run.stderr)
            if run.returncode:raise RuntimeError('XeLaTeX failed; inspect '+str(out))
        pdf=out/(source.stem+'.pdf');text=out/(source.stem+'.txt')
        text.write_text('\n\f\n'.join(page.extract_text() or '' for page in PdfReader(pdf).pages)+'\n',encoding='utf-8',newline='\n')
        log=(out/(source.stem+'.log')).read_text(encoding='utf-8',errors='replace')
        warnings=[line for line in log.splitlines() if 'Overfull' in line or 'Missing character' in line]
        manifest['warnings'][source.stem]=warnings
        if warnings:raise RuntimeError('unresolved layout/font warnings; inspect '+str(out))
        for file in (pdf,text):manifest['outputs'][file.name]=hashlib.sha256(file.read_bytes()).hexdigest()
    (out/'build.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if a.publish:
        for name in manifest['outputs']:shutil.copyfile(out/name,root/'docs'/name)
    print(json.dumps(manifest,ensure_ascii=False,indent=2))
    return 0


if __name__=='__main__':raise SystemExit(main())
