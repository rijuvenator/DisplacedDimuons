import math
import itertools

counts = {
    'SS' : {
        'SR' : {},
        'CR' : {}
    },
    'OS' : {
        'SR' : {},
        'CR' : {}
    }
}

def whichRegion(deltaPhi):
    if   deltaPhi <    math.pi/4.: return 'SR'
    elif deltaPhi > 3.*math.pi/4.: return 'CR'
    return None

LxySigThresholds = range(9)
WindowThresholds = list(reversed([-1*i for i in range(1, 7)])) + range(16)

for sign in counts:
    for region in counts[sign]:
        for l, w in itertools.product(LxySigThresholds, WindowThresholds):
            counts[sign][region][(l, w)] = 0

for sign in counts:
    for line in open('{}_LxySig_60_115.txt'.format(sign)):

        cols = line.strip('\n').split()
        PATLxySig = float(cols[14])
        DSALxySig = float(cols[15])
        deltaPhi  = float(cols[18])

        region = whichRegion(deltaPhi)

        if region is None: continue

        for l, w in itertools.product(LxySigThresholds, WindowThresholds):
            if DSALxySig > l and PATLxySig < 100+w and PATLxySig > 75-w:
                counts[sign][region][(l, w)] += 1

def safeDivide(a, b):
    try:
        return a/float(b)
    except:
        return 0.

for region in ('SR', 'CR'):
    print '=== {} ==='.format(region)
    for l in LxySigThresholds:
        print '  DSA LxySig > {}'.format(l)
        for w in WindowThresholds:
            print '    {:2d} < PATLxySig < {:3d} : {:3d} {:3d} {:6.4f}'.format(75-w, 100+w, counts['SS'][region][(l, w)], counts['OS'][region][(l, w)], safeDivide(counts['OS'][region][(l, w)], counts['SS'][region][(l, w)]))

