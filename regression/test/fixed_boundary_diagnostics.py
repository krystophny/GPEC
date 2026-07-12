#!/usr/bin/env python3
"""Regression check for fixed-boundary DCON diagnostics."""

import csv
import os
import pathlib
import re
import shutil
import subprocess
import tempfile


def read_output(path):
    rows = list(csv.DictReader(path.open()))
    values = {}
    for row in rows:
        values.setdefault(row["quantity"], []).append(
            complex(float(row["value_real"]), float(row["value_imag"]))
        )
    return values


def run_case(repo, q0, expected_crossings):
    example = repo / "docs" / "examples" / "solovev_ideal_example"
    with tempfile.TemporaryDirectory() as temporary:
        rundir = pathlib.Path(temporary)
        for source in example.glob("*.in"):
            shutil.copy2(source, rundir / source.name)
        dcon = (rundir / "dcon.in").read_text()
        dcon = dcon.replace("vac_flag=t", "vac_flag=f")
        dcon = dcon.replace("qlow=1.02", "qlow=0.5")
        dcon = dcon.replace("netcdf_out=t", "netcdf_out=t\n    out_fixed=t")
        (rundir / "dcon.in").write_text(dcon)
        sol = (rundir / "sol.in").read_text()
        sol = re.sub(r"^   q0 = .*$", f"   q0 = {q0}", sol, flags=re.MULTILINE)
        (rundir / "sol.in").write_text(sol)
        environment = os.environ.copy()
        library = str(repo / "deps" / "lib")
        environment["LD_LIBRARY_PATH"] = library + ":" + environment.get(
            "LD_LIBRARY_PATH", ""
        )
        subprocess.run(
            [repo / "bin" / "dcon"],
            cwd=rundir,
            env=environment,
            stdout=subprocess.DEVNULL,
            check=True,
        )
        values = read_output(rundir / "fixed_boundary.csv")
        assert values["newcomb_zero_count"] == [complex(expected_crossings)]
        assert max(abs(value) for value in values["response_eigen_residual"]) < 1e-12
        assert abs(values["response_hermiticity_relative"][0]) < 1e-3
        assert all(value.real > 0.0 for value in values["boundary_norm"])


def main():
    repo = pathlib.Path(__file__).resolve().parents[2]
    run_case(repo, 1.039843, 0)
    run_case(repo, 1.039062, 1)
    print("fixed-boundary diagnostics: PASS")


if __name__ == "__main__":
    main()
