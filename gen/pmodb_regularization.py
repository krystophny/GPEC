"""Native FortSym proof of diagonal regularization identities."""
import fortsym.sympy as f
J,Jp,X,Xp,R,c,m,n,q,S=f.symbols("J Jp X Xp R c m n q S")
t=-R*(J*R*Xp+Jp*X+2*f.pi*f.I*n*J*S/c)/(2*f.pi*f.I*(m-n*q))
z=-R*(q*J*R*Xp+q*Jp*X+2*f.pi*f.I*m*J*S/c)/(2*f.pi*f.I*(m-n*q))
angular=2*f.pi*f.I*(m*t-n*z)
checks={"R1":J*R*Xp+Jp*X+angular-(1-R)*(J*R*Xp+Jp*X),
        "R1a":J*Xp+Jp*X+angular-J*(1-R**2)*Xp-(1-R)*Jp*X,
        "R4":c*(q*t-z)/J-R*S}
for label,residual in checks.items():
    assert residual.is_zero is True, label
    print(label,"PROVED")
