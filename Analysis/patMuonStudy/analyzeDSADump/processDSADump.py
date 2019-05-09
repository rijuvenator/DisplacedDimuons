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

    'PCA'      : {'cast':float, 'col':31},
    'PCA_XY'   : {'cast':float, 'col':32},
    'PCA_Z'    : {'cast':float, 'col':33},
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
        if vals['PCA'] < 10.:
            print line.strip('\n')
