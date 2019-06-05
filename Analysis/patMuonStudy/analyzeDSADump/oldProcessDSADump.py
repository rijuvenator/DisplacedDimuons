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
    'vtxChi2'  : {'cast':float, 'col':12},
    'cosAlpha' : {'cast':float, 'col':13},
    'cosAlphaO': {'cast':float, 'col':14},

    'd01'      : {'cast':float, 'col':16},
    'd02'      : {'cast':float, 'col':17},
    'd0Sig1'   : {'cast':float, 'col':18},
    'd0Sig2'   : {'cast':float, 'col':19},

    'fpte1'    : {'cast':float, 'col':21},
    'fpte2'    : {'cast':float, 'col':22},

    'nDSA'     : {'cast':int  , 'col':27},
    'nDSACln'  : {'cast':int  , 'col':28},
    'DCA'      : {'cast':float, 'col':30},
    'nPPM'     : {'cast':int  , 'col':33},
    'nPPP'     : {'cast':int  , 'col':34},
}

f = open(sys.argv[1])

MODE = 'NDSA'

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

    if MODE is not None:
        if (vals['fpte1']<0.01 or vals['fpte2']<0.01 or vals['nDSA']>8) and vals['cosAlphaO'] > -0.8:
            print line.strip('\n')
