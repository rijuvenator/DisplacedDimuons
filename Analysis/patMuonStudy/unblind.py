import sys
import math
import operator

##### COLUMNS #####
config = {
    'name'     : {'cast':str  , 'col': 0},
    'run'      : {'cast':int  , 'col': 1},
    'lumi'     : {'cast':int  , 'col': 2},
    'event'    : {'cast':int  , 'col': 3},

    'type'     : {'cast':str  , 'col': 6},
    'idx1'     : {'cast':int  , 'col': 7},
    'idx2'     : {'cast':int  , 'col': 8},

    'LxySig'   : {'cast':float, 'col':10},
    'Lxy'      : {'cast':float, 'col':11},
    'vtxChi2'  : {'cast':float, 'col':12},
    'cosAlpha' : {'cast':float, 'col':13},
    'cosAlphaO': {'cast':float, 'col':14},
    'DCA'      : {'cast':float, 'col':15},

    'd01'      : {'cast':float, 'col':17},
    'd02'      : {'cast':float, 'col':18},
    'd0Sig1'   : {'cast':float, 'col':19},
    'd0Sig2'   : {'cast':float, 'col':20},

    'nDSA'     : {'cast':int  , 'col':22},
    'nDSACln'  : {'cast':int  , 'col':23},
    'nPPM'     : {'cast':int  , 'col':24},
    'nPPP'     : {'cast':int  , 'col':25},
    'nPP'      : {'cast':int  , 'col':26},

    'trkChi21' : {'cast':float, 'col':28},
    'trkChi22' : {'cast':float, 'col':29},

    'nCSC1'    : {'cast':int  , 'col':31},
    'nCSC2'    : {'cast':int  , 'col':32},
    'nDT1'     : {'cast':int  , 'col':33},
    'nDT2'     : {'cast':int  , 'col':34},

    'deltaPhi' : {'cast':float, 'col':36},

    'q1'       : {'cast':int  , 'col':38},
    'q2'       : {'cast':int  , 'col':39},
    'rq1'      : {'cast':int  , 'col':40},
    'rq2'      : {'cast':int  , 'col':41},

    'mass'     : {'cast':float, 'col':47},

    'time1'    : {'cast':float, 'col':49},
    'time2'    : {'cast':float, 'col':50},
}

##### CONDITIONS #####
def oppositeSign(vals): return vals['rq1']+vals['rq2'] == 0

REGIONS = {
    'CR' : [3.*math.pi/4.,    math.pi   ],
    'SR' : [0.           ,    math.pi/4.],
    'I1' : [   math.pi/4.,    math.pi/2.],
    'I2' : [   math.pi/2., 3.*math.pi/4.]
}

def deltaPhi(vals, region='CR'): return REGIONS[region][0] < vals['deltaPhi'] < REGIONS[region][1]

def slices(vals, enddigit=7): return vals['event'] % 10 == enddigit

LESSMOREDICT = {'Less':operator.lt, 'More':operator.gt}

def LxySig(vals, cut=6., lessMore='Less'): return LESSMOREDICT[lessMore](vals['LxySig'], cut)

##### RUN OVER FILE #####
f = open(sys.argv[1])

for line in f:

    strippedLine = line.strip('\n')
    cols = strippedLine.split()

    # normalize the number of columns in case the first entry is a number (signalpoint)
    try:
        int(cols[0])
        cols = ['{}_{}_{}'.format(*cols[:3])]+cols[3:]
    except:
        pass

    # extract the values
    vals = {key:config[key]['cast'](cols[config[key]['col']]) for key in config}

    # apply the conditions
    if LxySig(vals, lessMore='More'): continue

    # figure out the region
    region = None
    for reg in REGIONS:
        if deltaPhi(vals, region=reg):
            region = reg
            break

    # all same sign is currently unblinded
    if True:
        if not oppositeSign(vals):
            print '=== SAME SIGN, REGION = {} ==='.format(region)
            print strippedLine

    # opposite sign: odd enddigits
    if True:
        if oppositeSign(vals):
            print '== OPPOSITE SIGN, REGION = {} ==='.format(region)
            print strippedLine

    # Examples
    #if oppositeSign(vals): print strippedLine
    #if deltaPhi(vals, region='CR'): print strippedLine
    #if slices(vals, 7): print strippedLine
    #if not LxySig(vals): continue
