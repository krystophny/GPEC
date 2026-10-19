pmodb radial-derivative selection
=================================

Verified at base 3622c25c: ``gpec/gpeq.f:114`` selects ``xmp1_mn`` as
``R*xsp1_mn`` only with ``reg_flag=t``, where
``R=(m-nq)^2/[(m-nq)^2+reg_spot^2]``. ``gpec/gpout.f:3005`` previously
applied R unconditionally when computing ``Bdivxprp``. Reuse ``xmp1_mn``
so ``reg_flag=f`` uses the same derivative as the field and displacement.
The regression runs the native Solovev example twice with reg_flag=f and
different reg_spot values; all pmodb columns must be unchanged.

This does not redesign regularization. With reg_flag=t, field, reconstructed
surface displacement and the effective divergence need not describe a
single smooth ideal displacement near rational surfaces. In a diagonal
Jacobian model the effective divergence is
``J D_eff=(1-R)(J R X'+J'X)``; the actual divergence is
``J div xi_rec=J(1-R^2)X'+(1-R)J'X``, and
``chi1(q xi_rec^theta-xi_rec^zeta)=R xi_s``.
These identities are proved by the native FortSym tests in
``gen/pmodb_regularization.py``. They are not estimates of resistive physics.
