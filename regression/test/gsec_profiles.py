#!/usr/bin/env python3
"""Regression checks for the cylindrical GSEC pressure profiles."""

import math
import os
import pathlib
import shutil
import subprocess
import tempfile


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError(f"expected exactly one {old!r} setting")
    return text.replace(old, new)


def write_inputs(repo, rundir, pressure_type):
    dcon = (repo / "input" / "dcon.in").read_text()
    for old, new in (
        ("mat_flag=t", "mat_flag=f"),
        ("ode_flag=t", "ode_flag=f"),
        ("vac_flag=t", "vac_flag=f"),
        ("mer_flag=t", "mer_flag=f"),
        ("kin_flag = t", "kin_flag = f"),
        ("bin_euler=t", "bin_euler=f"),
        ("netcdf_out=t", "netcdf_out=f"),
    ):
        dcon = replace_once(dcon, old, new)
    (rundir / "dcon.in").write_text(dcon)
    equil = (repo / "input" / "equil.in").read_text()
    for old, new in (
        ('eq_type="efit"', 'eq_type="gsec"'),
        ('eq_filename="mypath"', 'eq_filename="gsec.in"'),
        ("mpsi=128", "mpsi=32"),
        ("mtheta=256", "mtheta=64"),
        ("input_only=f", "input_only=t"),
        ("bin_eq_2d=t", "bin_eq_2d=f"),
    ):
        equil = replace_once(equil, old, new)
    (rundir / "equil.in").write_text(equil)
    option = "" if pressure_type is None else f'    pressure_type="{pressure_type}"\n'
    (rundir / "gsec.in").write_text(
        "&gsec_input\n"
        "    a_in=1, r0_in=10, b0_in=1, q0=0.9, beta0_in=0.008\n"
        "    p_pres_in=1, p_sig_in=1, tol_in=1e-10, ma=64, mtau=64\n"
        f"{option}/\n"
    )


def run_case(repo, pressure_type):
    with tempfile.TemporaryDirectory() as temporary:
        rundir = pathlib.Path(temporary)
        write_inputs(repo, rundir, pressure_type)
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
        )
        profile_path = rundir / "gsec.out"
        output = profile_path.read_text() if profile_path.exists() else ""
        return result, parse_profile(output)


def parse_profile(output):
    rows = []
    for line in output.splitlines():
        fields = line.split()
        if len(fields) == 6 and fields[0].isdigit():
            rows.append(tuple(float(value) for value in fields[1:]))
    return rows


def assert_profile(rows, profile):
    assert len(rows) > 50
    assert math.isclose(rows[0][3], 0.9, rel_tol=2e-3)
    for psi, _, pressure, _, _ in rows:
        if 0.05 < psi < 0.95:
            expected = 0.004 * profile(psi)
            assert math.isclose(pressure, expected, rel_tol=2e-3, abs_tol=2e-7)


def main():
    repo = pathlib.Path(__file__).resolve().parents[2]
    linear, linear_rows = run_case(repo, "linear")
    quadratic, quadratic_rows = run_case(repo, "quadratic")
    default, default_rows = run_case(repo, None)
    invalid, _ = run_case(repo, "cubic")
    assert linear.returncode == quadratic.returncode == default.returncode == 0
    assert_profile(linear_rows, lambda psi: 1.0 - psi)
    assert_profile(quadratic_rows, lambda psi: 1.0 - psi * psi)
    assert quadratic_rows == default_rows
    assert invalid.returncode != 0
    assert "GSEC INPUT ERROR: pressure_type must be linear or quadratic" in invalid.stdout
    print("GSEC pressure profiles: PASS")


if __name__ == "__main__":
    main()
