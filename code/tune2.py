import numpy as np
from tune import ev
from algorithms import *
print('GD extra')
for p0,pmax in [(2,150),(2,300),(4,200)]:
    print(p0,pmax,ev(run_gd,dict(p0=p0,pmax=pmax)))
print('LS')
for dt_f,g0,g1 in [(0.03,0.6,0.02),(0.01,0.3,0.01),(0.01,0.1,0.005),(0.005,0.1,0.002),(0.02,0.2,0.01)]:
    print(dt_f,g0,g1,ev(run_ls,dict(dt_f=dt_f,g0=g0,g1=g1)))
