# v1.6 slim-fix verification, 2026-10-21

[V] Upstream develop: 24bc45ad5ea75922966a48f7a26670b507cda620; slim fix: 63e8e8a068859290e93355af2327a04863ad9fa4.
[V] Evidence source and tests retain their original pre-slim history. Nothing on this branch adds a test or CI target to the slim PR.

[V] The out-of-tree pentrc_pmodb_gauge.f90 passes on the slim fix and fails on develop at the gauge-invariance assertion (line 38).

[V] Existing regression_solovev_ideal_example, coil_flag=f, harmonic_flag=t: Im(Tpsi_fcgl) at psi=0.4 is 2.690627988547619e-4 before and 2.612960364479537e-4 after. Both probes read the SAME fixed-side euler.bin, kinetic.txt and gpec_pmodb_n1.out; this isolates the reader change. The unchanged CGL implementation is used on both sides. These are example diagnostic values, not an experimental torque prediction.

[V] Reproducer: regression/test/pmodb_result_number.f90. Compile against each source tree with gfortran -O0 -g -fopenmp -I<TREE>/equil -I<TREE>/pentrc <DRIVER> -L<TREE>/deps/lib -lpentrc -llsode -lequil -llapack -lblas -lnetcdff -lnetcdf -o <EXE>; run each executable in the same prepared example directory.

[V] Native GNU Make build passed for the slim source tree and develop with up to four jobs locally (GNU Fortran 16.2.1):

```sh
make -C <TREE>/install -j4 dcon gpec pentrc FC=/usr/bin/gfortran CC=/usr/bin/gcc NETCDFHOME=/usr NETCDF_FORTRAN_HOME=/usr NETCDF_C_HOME=/usr LAPACKHOME=/usr FFLAGS='-O0 -g -fallow-argument-mismatch -fcheck=bounds -fbacktrace'
```

[V] Run the preserved regression outside the source checkout against its bin/ and docs/examples/ paths; compile the Fortran checks against that tree's equil/, pentrc/ and deps/lib/. Use OMP_NUM_THREADS=2, OPENBLAS_NUM_THREADS=2, MPLBACKEND=Agg, unset DISPLAY, and unlimited main-thread stack. No cluster jobs were submitted; gfortran 12.2 was not run.

[V] Preserved gen/ proof rerun with native FortSym ae635c80: perpendicular-pair and distinct-gauge identities proved.
