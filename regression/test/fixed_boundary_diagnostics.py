#!/usr/bin/env python3
"""Regression check for fixed-boundary DCON diagnostics."""

import csv
import os
import pathlib
import re
import shutil
import subprocess
import tempfile


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError(f"expected exactly one {old!r} setting")
    return text.replace(old, new)


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


def run_rejected_flip_case(repo):
    source = repo / "input"
    with tempfile.TemporaryDirectory() as temporary:
        rundir = pathlib.Path(temporary)
        for name in ("dcon.in", "equil.in", "lar.in", "vac.in"):
            shutil.copy2(source / name, rundir / name)

        dcon_path = rundir / "dcon.in"
        dcon = dcon_path.read_text()
        for old, new in (
            ("vac_flag=t", "vac_flag=f"),
            ("qlow=1.02", "qlow=0.5"),
            ("kin_flag = t", "kin_flag = f"),
            ("bin_euler=t", "bin_euler=f"),
            ("netcdf_out=t", "netcdf_out=f"),
        ):
            dcon = replace_once(dcon, old, new)
        dcon_path.write_text(dcon)

        equil_path = rundir / "equil.in"
        equil = equil_path.read_text()
        for old, new in (
            ('eq_type="efit"', 'eq_type="lar"'),
            ('eq_filename="mypath"', 'eq_filename="lar.in"'),
            ("psilow=1e-2", "psilow=1e-5"),
            ("mpsi=128", "mpsi=256"),
        ):
            equil = replace_once(equil, old, new)
        equil_path.write_text(equil)

        lar_path = rundir / "lar.in"
        lar = lar_path.read_text()
        for old, new in (
            ("beta0=1e-3", "beta0=0.002"),
            ("q0=1.5", "q0=0.9"),
            ("p_pres=2", "p_pres=1"),
            ("sigma_type='default'", "sigma_type='wesson'"),
        ):
            lar = replace_once(lar, old, new)
        lar_path.write_text(lar)

        environment = os.environ.copy()
        library = str(repo / "deps" / "lib")
        environment["LD_LIBRARY_PATH"] = library + ":" + environment.get(
            "LD_LIBRARY_PATH", ""
        )
        result = subprocess.run(
            [repo / "bin" / "dcon"],
            cwd=rundir,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=True,
        )
        assert "q =  1.000" in result.stdout
        assert "Zero crossing at" in result.stdout


def main():
    repo = pathlib.Path(__file__).resolve().parents[2]
    run_case(repo, 1.039843, 0)
    run_case(repo, 1.039062, 1)
    run_rejected_flip_case(repo)
    print("fixed-boundary diagnostics: PASS")


if __name__ == "__main__":
    main()
