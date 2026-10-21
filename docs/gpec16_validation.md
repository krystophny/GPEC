# v1.6 slim-fix verification, 2026-10-21

[V] Upstream develop: 24bc45ad5ea75922966a48f7a26670b507cda620; slim fix: 0bb870bd76d290bb476639c31834de00440cf1ae.
[V] Evidence source and tests retain their original pre-slim history. Nothing on this branch adds a test or CI target to the slim PR.

[V] The out-of-tree pmodb_reg_flag.py passes on the slim fix and fails on develop at its disabled-width invariance assertion (line 42).

[V] Native GNU Make build passed for the slim source tree and develop with up to four jobs locally (GNU Fortran 16.2.1):

```sh
make -C <TREE>/install -j4 dcon gpec pentrc FC=/usr/bin/gfortran CC=/usr/bin/gcc NETCDFHOME=/usr NETCDF_FORTRAN_HOME=/usr NETCDF_C_HOME=/usr LAPACKHOME=/usr FFLAGS='-O0 -g -fallow-argument-mismatch -fcheck=bounds -fbacktrace'
```

[V] Run the preserved regression outside the source checkout against its bin/ and docs/examples/ paths; compile the Fortran checks against that tree's equil/, pentrc/ and deps/lib/. Use OMP_NUM_THREADS=2, OPENBLAS_NUM_THREADS=2, MPLBACKEND=Agg, unset DISPLAY, and unlimited main-thread stack. No cluster jobs were submitted; gfortran 12.2 was not run.

[V] Preserved gen/ proof rerun with native FortSym ae635c80: R1, R1a, R4 proved.
