import math
import itertools
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('FILE')
parser.add_argument('--ll', dest='LL', type=float, default=6.)
parser.add_argument('--lu', dest='LU', type=float, default=float('inf'))
parser.add_argument('--w' , dest='W' , type=float, default=0.)
args = parser.parse_args()

def whichRegion(deltaPhi):
    if   deltaPhi <    math.pi/4.: return 'SR'
    elif deltaPhi > 3.*math.pi/4.: return 'CR'
    return None

LL  = args.LL
LU  = args.LU
W   = args.W
REG = 'SR'

for line in open(args.FILE):

    cols = line.strip('\n').split()
    PATLxySig = float(cols[14])
    DSALxySig = float(cols[15])
    deltaPhi  = float(cols[18])

    region = whichRegion(deltaPhi)

    if region is None: continue

    if LL < DSALxySig < LU and 75.-W < PATLxySig < 100.+W:
        print line.strip('\n')
