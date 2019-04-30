import sys

config = {
    'event'    : {'cast':int  , 'col': 3},

    'type'     : {'cast':str  , 'col': 6},

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
    'phi1'     : {'cast':float, 'col':23},
    'phi2'     : {'cast':float, 'col':24},
    'rphi1'    : {'cast':float, 'col':25},
    'rphi2'    : {'cast':float, 'col':26},

    'nDSA'     : {'cast':int  , 'col':27},
    'nDSACln'  : {'cast':int  , 'col':28},
    'qsum'     : {'cast':int  , 'col':29},
    'DCA'      : {'cast':float, 'col':30},
}

tests = {'total':{'count':0, 'lines':''}, 'LxySig':{'count':0, 'lines':''}, 'd0Sig':{'count':0, 'lines':''}, 'vtxChi2':{'count':0, 'lines':''}}

f = open(sys.argv[1])

#MODE = 'FPTE'
MODE = 'DCA'
#MODE = 'DCA-SIG'
#MODE = 'CUTTEST'
#MODE = 'CHARGE'

for line in f:
    cols = line.strip('\n').split()
    vals = {key:config[key]['cast'](cols[config[key]['col']]) for key in config}

    if MODE == 'FPTE':
        if vals['fpte1'] < 0.01 or vals['fpte2'] < 0.01:
            print line.strip('\n')

    elif MODE == 'DCA':
        if (vals['fpte1'] < 0.01 or vals['fpte2'] < 0.01) and vals['DCA'] < 60.:
            print line.strip('\n')

    elif MODE == 'DCA-SIG':
        if vals['DCA'] > 60.:
            print line.strip('\n')

    elif MODE == 'CHARGE':
        if vals['fpte1'] < 0.01 or vals['fpte2'] < 0.01:
            if vals['charge1'] != vals['rcharge1'] or vals['charge2'] != vals['rcharge2']:
                print line.strip('\n')

    elif MODE == 'CUTTEST':
        bools = {'LxySig':False, 'd0Sig':False, 'vtxChi2':False}

        if vals['LxySig'] > 3.:
            tests['LxySig']['count'] += 1
            tests['LxySig']['lines'] += line
            bools['LxySig'] = True

        if vals['d0Sig1'] > 3. and vals['d0Sig2'] > 3.:
            tests['d0Sig']['count'] += 1
            tests['d0Sig']['lines'] += line
            bools['d0Sig'] = True

        if vals['vtxChi2'] < 20.:
            tests['vtxChi2']['count'] += 1
            tests['vtxChi2']['lines'] += line
            bools['vtxChi2'] = True

        if all(bools.values()):
            tests['total']['count'] += 1
            tests['total']['lines'] += line

if MODE == 'CUTTEST':
    for key in ('total', 'LxySig', 'd0Sig', 'vtxChi2'):
        print '===', key, ':::', tests[key]['count']
        if True:
            print tests[key]['lines']
            print ''
