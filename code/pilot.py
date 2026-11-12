import numpy as np, time, sys
from algorithms import *
def pilot(kind,n,R,seeds=(9001,9002,9003),mult=1500):
    P=Problem(kind,n,R); B=mult*P.sweep
    out={}
    for alg in ['gd','sa','ls']:
        sc=[];tm=[]
        for s in seeds:
            X0=P.initial(np.random.default_rng(s))
            r=run_algorithm(alg,P,X0,B,[s,7])
            assert abs(r['final_check']-r['score'])<1e-9
            sc.append(r['score']);tm.append(r['time'])
        out[alg]=(np.mean(sc),max(sc),np.mean(tm))
    print(kind,n,R,{k:tuple(round(x,4) for x in v) for k,v in out.items()})
if __name__=='__main__':
    for args in [('S2',4,None),('S2',12,None),('S2',13,None),('S2',30,None),('H2',12,2.0),('R2',12,2.0)]:
        pilot(*args)
