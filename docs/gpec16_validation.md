# v1.6 slim-fix verification, 2026-10-21

[V] Upstream develop: 24bc45ad5ea75922966a48f7a26670b507cda620; slim fix: 2380bc6622488a767c42f17ada8883065b0987cb.
[V] Evidence source and tests retain their original pre-slim history. Nothing on this branch adds a test or CI target to the slim PR.

[V] The out-of-tree pentrc_cgl_pressure.f90 passes on the slim fix and fails on develop at its independent double-adiabatic pressure-work assertion (line 48).

[V] Manufactured complex displacement on the existing Solovev ideal equilibrium at psi=0.4: Im(Tpsi_fcgl) = 2.410379216933e5 before, 2.731839412786e5 after, pressure-work oracle = 2.731839412786e5. This is a manufactured normalization test, not an experimental torque prediction. The regression tolerance is 1e-10 relative for the direct algebraic pressure-work identity.

[V] Native GNU Make build passed for the slim source tree and develop with up to four jobs locally (GNU Fortran 16.2.1):

```sh
make -C <TREE>/install -j4 dcon gpec pentrc FC=/usr/bin/gfortran CC=/usr/bin/gcc NETCDFHOME=/usr NETCDF_FORTRAN_HOME=/usr NETCDF_C_HOME=/usr LAPACKHOME=/usr FFLAGS='-O0 -g -fallow-argument-mismatch -fcheck=bounds -fbacktrace'
```

[V] Run the preserved regression outside the source checkout against its bin/ and docs/examples/ paths; compile the Fortran checks against that tree's equil/, pentrc/ and deps/lib/. Use OMP_NUM_THREADS=2, OPENBLAS_NUM_THREADS=2, MPLBACKEND=Agg, unset DISPLAY, and unlimited main-thread stack. No cluster jobs were submitted; gfortran 12.2 was not run.

[V] Preserved gen/ proof rerun with native FortSym ae635c80: K5 complex pressure-work and K6 curvature-reconstruction identities proved.
