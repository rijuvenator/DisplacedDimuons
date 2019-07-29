import sys

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
}

f = open(sys.argv[1])

MODE = 'HITS'
MODE = 'DPHI'
MODE = 'CHARGE'
MODE = 'PRUNE'

for line in f:

    cols = line.strip('\n').split()

    # normalize the number of columns in case the first entry is a number (signalpoint)
    try:
        int(cols[0])
        cols = ['{}_{}_{}'.format(*cols[:3])]+cols[3:]
    except:
        pass

    # extract the values
    vals = {key:config[key]['cast'](cols[config[key]['col']]) for key in config}

    # some useful expressions... nothing yet

    if MODE == 'HITS':
        nCSC1, nCSC2, nDT1, nDT2 = vals['nCSC1'], vals['nCSC2'], vals['nDT1'], vals['nDT2']
        pure1 = (nDT1 > 0 and nCSC1 == 0) #or (nCSC1 > 0 and nDT1 == 0)
        pure2 = (nDT2 > 0 and nCSC2 == 0) #or (nCSC2 > 0 and nDT2 == 0)
        if pure1 or pure2:
            print '{} {}'.format('{:2d}'.format(nDT1) if pure1 else '  ', '{:2d}'.format(nDT2) if pure2 else '  ')

    if MODE == 'DPHI':
        if vals['deltaPhi'] < 1.5707963268:
            print line.strip('\n')

    if MODE == 'CHARGE':
        if vals['DCA'] > 30.: print line.strip('\n')

    if MODE == 'PRUNE':
        print '{:5s} {:6d} {:4d} {:10d} ::: {:9.4f} {:8.4f} {:5.2f} {:6.3f} {:5.2f} ::: {:6.4f} ::: {:2d} {:2d} ::: {:2d} {:2d}'.format(
            *(vals[z] for z in ('name', 'run', 'lumi', 'event', 'LxySig', 'Lxy', 'vtxChi2', 'cosAlphaO', 'DCA', 'deltaPhi', 'nDSA', 'nPP', 'q1', 'q2'))
        )
