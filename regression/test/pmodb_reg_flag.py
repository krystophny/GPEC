"""Regression: with reg_flag=f, pmodb must be independent of reg_spot.

Build bin/dcon and bin/gpec, then run this script.
"""
from pathlib import Path
import os
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]

def table(path):
    rows = []
    for line in path.read_text().splitlines():
        if len(line.split()) == 10:
            try:
                rows.append([float(x) for x in line.split()])
            except ValueError:
                pass
    return rows

with tempfile.TemporaryDirectory(prefix='gpec-regflag-') as tmp:
    run = Path(tmp)
    shutil.copytree(ROOT/'docs/examples/regression_solovev_ideal_example', run, dirs_exist_ok=True)
    env = dict(os.environ, OMP_NUM_THREADS='2', OPENBLAS_NUM_THREADS='2', MPLBACKEND='Agg')
    env.pop('DISPLAY', None)
    def execute(name):
        with (run/(name+'.log')).open('w') as log:
            subprocess.run([str(ROOT/'bin'/name)], cwd=run, env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
    execute('dcon')
    original = (run/'gpec.in').read_text().replace('coil_flag=t', 'coil_flag=f').replace('harmonic_flag=f', 'harmonic_flag=t')
    outputs = []
    for width in ('0.01', '0.2'):
        text = re.sub(r'(?im)(reg_flag\s*=)\s*\w+', r'\1f', original)
        text = re.sub(r'(?im)(reg_spot\s*=)\s*[\w.+-]+', r'\g<1>'+width, text)
        (run/'gpec.in').write_text(text)
        execute('gpec')
        outputs.append(table(run/'gpec_pmodb_n1.out'))
    assert outputs[0], 'pmodb output is empty'
    assert outputs[0] == outputs[1], 'pmodb depends on disabled regularization width'
    print('PASS: unregularized pmodb is independent of reg_spot')
