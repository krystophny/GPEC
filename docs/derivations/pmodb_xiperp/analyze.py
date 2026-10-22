from pathlib import Path
import json
import numpy as np
from tables import table,pmodb,metric
E=Path(__file__).resolve().parent
def complex_grid(path,ncol):
    a=table(path,ncol)
    ps=np.unique(a[:,0]);ms=np.unique(a[:,1]).astype(int)
    a=a.reshape(len(ps),len(ms),ncol)
    return ps,ms,*[a[:,:,k]+1j*a[:,:,k+1] for k in range(2,ncol,2)]
def energy(ps,x): return float(np.trapezoid(np.sum(abs(x)**2,axis=1),ps))
records=[]
lines=['# VERIFIED numerical evidence','',
       'Residual ratio = sum_psi |Bdiv+lagb+Bk|² / sum_psi |lagb|² (unweighted).',
       'PENTRC energies use trapezoidal integration in normalized psi of sum_m |X_m|².',
       'Independent reconstruction uses exact Fourier derivatives and PENTRC equilibrium metric jets,',
       'rather than the fitted-product theta derivative used in gpout. See probe.f90.', '']
for ex in ['ideal','kinetic']:
    for reg in ['t','f']:
        b=E/'runs'/f'base-{ex}-{reg}'; f=E/'runs'/f'fix-{ex}-{reg}'
        ps,ms,eb,lb,db,kb=pmodb(b/'gpec_pmodb_n1.out')
        pf,mf,ef,lf,df,kf=pmodb(f/'gpec_pmodb_n1.out')
        assert np.array_equal(ms,mf) and np.array_equal(ps,pf)
        pi,mi,di,ki,gauge,dspline,eind,force=complex_grid(f/'independent.out',14)
        assert np.array_equal(mi,mf)
        # pmodb psi is written to 8 digits; independent uses xclebsch's 16 digits.
        assert np.max(abs(ps-pi))<5.1e-10
        rel=lambda a,b: np.linalg.norm(a-b,axis=0)/np.linalg.norm(b,axis=0)
        resid=df+lf+kf
        independent=rel(di,df)
        kdiff=rel(ki,kf)
        remaining=np.sum(abs(resid-gauge)**2,axis=0)/np.sum(abs(lf)**2,axis=0)
        after_eul=np.sum(abs(resid-gauge-(ef-eind))**2,axis=0)/np.sum(abs(lf)**2,axis=0)
        budget=gauge+(ef-eind)+force+(dspline-di)
        after_budget=np.sum(abs(resid-budget)**2,axis=0)/np.sum(abs(lf)**2,axis=0)
        br=metric(b/'gpec_pmodb_n1.out')[1];fr=metric(f/'gpec_pmodb_n1.out')[1]
        lines += [f'## {ex}, reg_flag={reg}', '',
          '|m|base sum Bdiv²|fix sum Bdiv²|base sum (lagb+Bk)²|fix sum (lagb+Bk)²|base residual|fix residual|independent Bdiv relative L2|after gauge subtraction|',
          '|--:|--:|--:|--:|--:|--:|--:|--:|--:|']
        for j,m in enumerate(ms):
            lines += [f'|{m}|{br[j,0]:.6e}|{fr[j,0]:.6e}|{br[j,1]:.6e}|{fr[j,1]:.6e}|{br[j,2]:.6g}|{fr[j,2]:.6g}|{independent[j]:.6g}|{remaining[j]:.6g}|']
        lines+=['|4|outside retained m=-4…3 spectrum|—|—|—|—|—|—|—|','']
        pb,mb,divb,dbob_b=complex_grid(b/'reader-pair.out',6)
        pfix,mfix,divf,dbob_f=complex_grid(f/'reader-pair.out',6)
        ix,im,matdiv,matdb=complex_grid(f/'matrix-pair.out',6)
        energies={name:{'base':energy(pb,bv),'fix':energy(pfix,fv)}
                  for name,bv,fv in [('divx',divb,divf),('dbob',dbob_b,dbob_f)]}
        for v in energies.values():v['change_percent']=100*(v['fix']/v['base']-1)
        lines+=['|PENTRC quantity|develop energy|new energy|change %|','|--|--:|--:|--:|']
        for name,v in energies.items():lines +=[f"|{name}|{v['base']:.10e}|{v['fix']:.10e}|{v['change_percent']:.6g}|"]
        lines+=['']
        records.append(dict(example=ex,reg=reg,ms=ms.tolist(),base=br.tolist(),fix=fr.tolist(),
            independent_Bdiv_L2=independent.tolist(),independent_Bk_L2=kdiff.tolist(),
            independent_spline_L2=rel(dspline,df).tolist(),
            after_gauge_ratio=remaining.tolist(),after_eul_ratio=after_eul.tolist(),
            after_budget_ratio=after_budget.tolist(),energies=energies))
(E/'comparison.md').write_text('\n'.join(lines)+'\n')
(E/'analysis.json').write_text(json.dumps(records,indent=2)+'\n')
for r in records:
    print(r['example'],r['reg'],'max independent Bdiv',max(r['independent_Bdiv_L2']),
          'max after gauge',max(r['after_gauge_ratio']), 'PENTRC energies',r['energies'])
