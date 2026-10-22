# VERIFIED analytical derivation (before code edits)

Coordinates are (normalized poloidal flux psi, theta in turns, zeta in turns).
The map is R=ro+sqrt(rzphi(1))*cos(2pi*(theta+rzphi(2))),
Z=zo+sqrt(rzphi(1))*sin(...), phi=2pi*zeta+rzphi(3).
Thus v(i,:) in gpec/idcon.f:592-600 and equil/direct.f:233-240 is the
coordinate tangent e_i, despite the comment calling it contravariant.
The metric is g_ij=e_i.e_j, not the inverse metric.
J=rzphi%f(4)=jac=jacfac includes the turns factors; no additional 2pi belongs
in the projection. chi1=2pi*psio (idcon.f:93); B=eqfun%f(1).
B^i=(0,chi1/J,chi1*q/J), q=sq%f(4), and
B²=chi1²*(g22+2*q*g23+q²*g33)/J².

Set X=xsp_fun=xi^psi, A=xms_fun/chi1=xi^s/chi1=q*xi^theta-xi^zeta.
The J-weighted gpeq_contra equations (gpeq.f:198-232) give this invariant
before independent Fourier truncation/regulation of xi^theta,xi^zeta.
Define U=eqfun%f(2)=(g12+q*g13)/(J*B²),
V=eqfun%f(3)=(g23+q*g33)/(J*B²) (idcon.f:614-619, direct.f:245-248).
Subtracting (xi.B/B²)*B and eliminating xi^zeta=q*xi^theta-A gives

    T = J*xi_perp^theta = chi1²*(-U*X+V*A)
    Z = J*xi_perp^zeta  = q*T-J*A
    xi_perp^psi = X.

This is an algebraic identity for arbitrary nonsingular metrics with the B²
norm above, not a numerical probe. derive_check.py verifies both projections
and the retained G7/G8 identities with the native FortSym exact zero test.

With D=xmp1_mn transformed to theta (selected by reg_flag in gpeq_sol:130-145),

    B div(xi_perp) = B*(D+J_psi/J*X+(d_theta T-i*2pi*n*Z)/J).

cspl stores (T,Z); its first theta derivative differentiates the complete
periodic product. Analytically d_theta T=chi1²*(-U_theta*X-U*d_theta X
+V_theta*A+V*d_theta A), with U_theta=eqfun%fy(2), V_theta=eqfun%fy(3).
For each source harmonic m, d_theta=+i*2pi*m, d_zeta=-i*2pi*n.
The sign in internal divxprpfun is negative; the existing output negates it.

Multiplication by J*B² gives exactly idcon.f:1026-1033,1080-1083:

    x=J*B²
    y=J_psi*B²-chi1²*B²*U_theta-i*2pi*(m-n*q)*chi1²*B²*U
    z=chi1²*B²*V_theta+i*2pi*(chi1²*B²*V*(m-n*q)+n*J*B²).

The last coefficient equals i*2pi*chi1²/J*[m*(g23+q*g33)
+n*(g22+q*g23)] plus the V_theta term, by the B² norm identity.
These are xmat,ymat,zmat acting on (D,X,A), as in pentrc/inputs.f90:893-905.

Force balance gives B*kappa.xi_perp=mu0*p_psi*X/B+X*B_psi+(T/J)*B_theta.
sq%f1(2) is mu0*p_psi, already used in gpout; no new pressure conversion.
The existing curvfun is the negative of this quantity, hence becomes

    curvfun=-X*sq%f1(2)/B-X*eqfun%fx(1)-T/J*eqfun%fy(1).

J*B²*kappa.xi_perp=s*X+t*A, with
s=J*(mu0*p_psi+B*B_psi)-chi1²*B*B_theta*U,
t=chi1²*B*B_theta*V: exactly smat,tmat (G7).
lagb is retained in its xi^zeta=0 gauge. Its difference from
-B*(div(xi_perp)+kappa.xi_perp) is the known parallel advective gauge term
and any actual closure/force/interpolation errors; the exact projection alone
does not prove a small residual for regularized outputs.

## VERIFIED exact residual budget and the failed all-m acceptance

For the pointwise induction field from the same X,A,D, the residual is G+F:

    G=(A/q-T/J)*B_theta
    F=X*[B*J_psi/J-chi1²*B/J*(U_theta+q_psi*V)+P/B
         +2*B_psi-2*chi1²/J*U*B_theta]
      +A*chi1²/J*(B*V_theta+2*V*B_theta), P=sq%f1(2).

FortSym's Budget identity proves this without assuming force balance. F=0
for exact force-balanced equilibrium metric jets; interpolated quantities
need not satisfy that identity exactly. The executable diagnostic additionally
accounts for eulb's finite Fourier metric contraction (gpeq.f:307-310) and
the fitted theta derivative (gpout.f:3036,3058). The measured residual budget
closes to <2.1e-13 in the requested squared residual/lagb normalization.
For unregularized ideal m=-4,-3,-2, the large raw residual is predominantly G.
For regularized ideal m=-1, after G and the eulb contraction correction the
ratio remains 0.03454 and is accounted for by F; its peak is psi=0.03729234.
Thus the claimed uniform 1-2% all-m bound is not a consequence of the exact
projection. The retained gauge in gpout.f:3052-3055 and the discrete metric
jets used at gpout.f:3039,3061-3063 are the explicit nonzero budget terms.
HYPOTHESIS: interpolation in the independently fitted B,U,V (idcon.f:634,
17 equilibrium psi nodes for this example) dominates F. No mesh refinement
or extra physics patch was attempted; this is not promoted to a proved cause.
