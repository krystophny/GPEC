#!/usr/bin/env python3
"""Regression check for raw DCON ideal-energy matrix diagnostics."""

import csv
import math
import os
import pathlib
import shutil
import subprocess
import tempfile


def configured_input(source, enabled):
    text = source.read_text()
    text = text.replace("ode_flag=t", "ode_flag=f")
    text = text.replace("vac_flag=t", "vac_flag=f")
    text = text.replace("mer_flag=t", "mer_flag=f")
    text = text.replace("bal_flag=t", "bal_flag=f")
    text = text.replace("delta_mlow=8", "delta_mlow=0")
    text = text.replace("delta_mhigh=8", "delta_mhigh=0")
    if enabled:
        text = text.replace("netcdf_out=t", "netcdf_out=t\n    out_fkg=t")
    return text


def run_case(repo, enabled):
    example = repo / "docs" / "examples" / "solovev_ideal_example"
    with tempfile.TemporaryDirectory() as temporary:
        rundir = pathlib.Path(temporary)
        for source in example.glob("*.in"):
            shutil.copy2(source, rundir / source.name)
        (rundir / "dcon.in").write_text(
            configured_input(rundir / "dcon.in", enabled)
        )
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
        output = rundir / "fkg.csv"
        if not enabled:
            assert not output.exists()
            return
        rows = list(csv.DictReader(output.open()))
        assert rows
        assert set(rows[0]) == {"psi", "matrix", "m1", "m2", "real", "imag"}
        matrices = {}
        for row in rows:
            value = complex(float(row["real"]), float(row["imag"]))
            assert math.isfinite(value.real) and math.isfinite(value.imag)
            key = (float(row["psi"]), row["matrix"])
            matrices.setdefault(key, {})[(int(row["m1"]), int(row["m2"]))] = value
        assert {matrix for _, matrix in matrices} == {"F", "K", "G"}
        for (psi, name), matrix in matrices.items():
            assert psi > 0.0
            modes = {first for first, _ in matrix}
            assert len(matrix) == len(modes) ** 2
            if name in {"F", "G"}:
                for (first, second), value in matrix.items():
                    scale = max(1.0, abs(value))
                    assert abs(value - matrix[second, first].conjugate()) < 1e-12 * scale


def main():
    repo = pathlib.Path(__file__).resolve().parents[2]
    run_case(repo, False)
    run_case(repo, True)
    print("F/K/G diagnostics: PASS")


if __name__ == "__main__":
    main()
