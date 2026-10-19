PENTRC ASCII pmodb gauge contract
=================================

Verified at base 3622c25c: ``pentrc/inputs.f90:469`` reads positive
``Bdivxprp`` and ``Bkxprp`` from columns 7-10, then ``:487`` discards the
former and combines ``lagb`` with curvature. The lagb column instead uses
``xi_g^zeta=0`` in GPEC's working chart (``gpec/gpout.f:3035``).
Its difference from the perpendicular value is
``lagb-b_perp=-(xi_perp^zeta/q) d_theta B``.

The reader now keeps the supplied divergence and forms
``b_perp=-(Bdivxprp+Bkxprp)`` in Tesla before deweighting both by B.
This supplies the same displacement gauge to the field-strength drive and
the explicit Jacobian term in ``pentrc/torque.F90``. It matches the
``set_peq`` input convention, subject to equilibrium force balance and the
same regularization limitations as the supplied columns. A file with no
valid divergence column cannot be recovered by assuming lagb is b_perp.

``regression/test/pentrc_pmodb_gauge.f90`` passes two complete ASCII tables
through the actual reader, with identical divergence/curvature but different
lagb. The drive and Jacobian must be unchanged. Run in the native Solovev
ideal example after dcon and gpec. The linear algebra proof is
``gen/pmodb_input.py`` (FortSym native only).
