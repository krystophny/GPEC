from pathlib import Path
import numpy as np
E=Path(__file__).resolve().parent
def table(path,ncol):
    rows=[]
    for line in path.read_text().splitlines():
        s=line.split()
        if len(s)!=ncol: continue
        try: rows.append([float(x) for x in s])
        except ValueError: pass
    return np.array(rows)
def pmodb(path):
    a=table(path,10)
    ps=np.unique(a[:,0]); ms=np.unique(a[:,1]).astype(int)
    a=a.reshape(len(ps),len(ms),10)
    return ps,ms,*[a[:,:,k]+1j*a[:,:,k+1] for k in (2,4,6,8)]
def metric(path):
    ps,ms,e,l,d,k=pmodb(path)
    sums=lambda x: np.sum(np.abs(x)**2,axis=0)
    return ms,np.array([sums(d),sums(l+k),sums(d+l+k)/sums(l)]).T
if __name__=='__main__':
    for path in sorted((E/'runs').glob('*/gpec_pmodb_n1.out')):
        ms,v=metric(path)
        lines=[f'# VERIFIED {path.parent.name}', '', 'Definitions: unweighted sum over every output psi; residual ratio=sum|Bdiv+lagb+Bk|²/sum|lagb|².', '', r'|m|sum\|Bdiv\|²|sum\|lagb+Bk\|²|residual ratio|','|--:|--:|--:|--:|']
        sel=(abs(ms)<=4)|(v[:,2]>.05)
        for m,x in zip(ms[sel],v[sel]): lines.append(f'|{m}|{x[0]:.8e}|{x[1]:.8e}|{x[2]:.8e}|')
        for m in range(-4,5):
            if m not in ms: lines.append(f'|{m}|outside retained output spectrum|—|—|')
        (E/f'table-{path.parent.name}.md').write_text('\n'.join(lines)+'\n')
        print(path.parent.name, {int(m):[float(y) for y in x] for m,x in zip(ms[abs(ms)<=4],v[abs(ms)<=4])})
