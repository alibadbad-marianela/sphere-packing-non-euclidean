import numpy as np, itertools, functools
from algorithms import *
seeds=(9001,9002,9003,9004)
confs=[('S2',13,None),('S2',30,None),('H2',12,2.0),('R2',19,3.0)]
def ev(fn,kw):
    tot=[]
    for kind,n,R in confs:
        P=Problem(kind,n,R);B=1500*P.sweep;sc=[]
        for s in seeds:
            X0=P.initial(np.random.default_rng(s))
            r=fn(P,X0,B,np.random.default_rng([s,7]),**kw);sc.append(r['score'])
        tot.append(np.mean(sc))
    return np.round(tot,4)
