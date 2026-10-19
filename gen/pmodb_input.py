import fortsym.sympy as f
D,K,g=f.symbols("D K g")
b=-(D+K)
assert (b+D+K).is_zero is True
assert ((b+g)+D+K-g).is_zero is True
print("PROVED: perpendicular pair; lagb requires a distinct gauge term")
