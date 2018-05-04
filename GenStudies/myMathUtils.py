from math import *
from RecoUtils import *
from myMathUtils import*

def deltaPhi(a,b):
    dphi = abs(a.phi()-b.phi())
    if dphi > pi: dphi = 2*pi-dphi
    return dphi

def deltaR(a,b):
    dphi = deltaPhi(a,b)
    return hypot(a.eta()-b.eta(),dphi)

                    
