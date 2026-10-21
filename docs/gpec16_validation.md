# v1.6 slim-fix verification, 2026-10-21

[V] Upstream develop: 24bc45ad5ea75922966a48f7a26670b507cda620; slim fix: f44643a80eb34ac0198ec321f3c079cb2cca9c90.
[V] Evidence source and tests retain their original pre-slim history. Nothing on this branch adds a test or CI target to the slim PR.

[V] The out-of-tree pmodb_diagnostic.py passes on the slim fix (diagnostic/pmodb divergence relative difference 0) and fails on develop at line 46 (relative difference 0.0016685808864671458; threshold 1e-7). The existing Hamada fixture excludes the pre-existing near-axis singularity.

[V] Native GNU Make build passed for the slim source tree and develop with up to four jobs locally (GNU Fortran 16.2.1):

```sh
make -C <TREE>/install -j4 dcon gpec pentrc FC=/usr/bin/gfortran CC=/usr/bin/gcc NETCDFHOME=/usr NETCDF_FORTRAN_HOME=/usr NETCDF_C_HOME=/usr LAPACKHOME=/usr FFLAGS='-O0 -g -fallow-argument-mismatch -fcheck=bounds -fbacktrace'
```

[V] Run the preserved regression outside the source checkout against its bin/ and docs/examples/ paths; compile the Fortran checks against that tree's equil/, pentrc/ and deps/lib/. Use OMP_NUM_THREADS=2, OPENBLAS_NUM_THREADS=2, MPLBACKEND=Agg, unset DISPLAY, and unlimited main-thread stack. No cluster jobs were submitted; gfortran 12.2 was not run.
