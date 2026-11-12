from tune import ev
from algorithms import *
for dt_f,g0,g1 in [(0.06,1.0,0.03),(0.1,1.5,0.05),(0.06,0.6,0.01),(0.1,1.0,0.02),(0.15,1.5,0.03)]:
    print(dt_f,g0,g1,ev(run_ls,dict(dt_f=dt_f,g0=g0,g1=g1)))
