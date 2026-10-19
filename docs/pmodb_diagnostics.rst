Local Jacobian in pmodb diagnostics
===================================

Verified at base 3622c25c: ``gpec/gpdiag.f:1012`` forms
``J xi_perp^theta=xmt-(chi1/B)^2*(xvt+q*xvz)/J`` using a stale local J.
The current theta's equilibrium values have just been evaluated, but J was
not assigned until the following loop (``:1034``). Assign ``jac=rzphi%f(4)``
before the projection, as ``gpout_pmodb`` already does.

The native regression compares diagnostic and pmodb divergence on a Hamada
case (J constant on each surface), avoiding different spline construction
for an angularly varying J. The projection and Lagrangian relation are
proved by FortSym G4.1-G5.6 in the separate pmodb derivation topic.
This corrects only diagnostics; ``llagb`` was already formed with a local J.
