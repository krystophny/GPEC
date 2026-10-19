"""Compare the actual diagnostic projection to pmodb on a Hamada case."""
from pathlib import Path
import os
import math
import shutil
import subprocess
import tempfile

root = Path(__file__).resolve().parents[2]

def table(path, n):
    rows = []
    for line in path.read_text().splitlines():
        if len(line.split()) == n:
            try:
                rows.append([float(x) for x in line.split()])
            except ValueError:
                pass
    return rows

with tempfile.TemporaryDirectory(prefix='gpec-diagnostic-') as tmp:
    run = Path(tmp)
    shutil.copytree(root/'docs/examples/regression_solovev_ideal_example',run,dirs_exist_ok=True)
    p = run/'equil.in'
    p.write_text(p.read_text().replace('jac_type="pest"','jac_type="hamada"').replace('psilow=1e-4','psilow=0.05'))
    p = run/'dcon.in'
    p.write_text(p.read_text().replace('psilow=1e-4','psilow=0.05'))
    p = run/'gpec.in'
    text = p.read_text().replace('coil_flag=t','coil_flag=f').replace('harmonic_flag=f','harmonic_flag=t')
    text = text.replace('jac_out="pest"','jac_out="hamada"')
    text = text.replace('&GPEC_DIAGNOSE','&GPEC_DIAGNOSE\n   pmodbmn_flag=t')
    p.write_text(text)
    env = dict(os.environ,OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',MPLBACKEND='Agg')
    env.pop('DISPLAY',None)
    for name in ('dcon','gpec'):
        with (run/(name+'.log')).open('w') as log:
            subprocess.run([str(root/'bin'/name)],cwd=run,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
    if not (run/'gpec_pmodb_n1.out').exists():
        raise RuntimeError((run/'gpec.log').read_text()[-4000:])
    out = table(run/'gpec_pmodb_n1.out',10)
    diag = table(run/'gpec_diagnostics_pmodb_n1.out',16)
    assert out and len(out)==len(diag)
    error = sum((a[6]-b[8])**2+(a[7]-b[9])**2 for a,b in zip(out,diag))
    norm = sum(a[6]**2+a[7]**2 for a in out)
    relative = math.sqrt(error/norm)
    assert relative < 1e-7, relative
    print('PASS: diagnostic/pmodb divergence relative difference',relative)
