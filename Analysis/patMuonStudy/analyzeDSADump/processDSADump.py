import sys

config = {
    'event'   : {'cast':int  , 'col': 3},

    'LxySig'  : {'cast':float, 'col':10},
    'vtxChi2' : {'cast':float, 'col':12},
    'cosAlpha': {'cast':float, 'col':13},

    'd01'     : {'cast':float, 'col':15},
    'd02'     : {'cast':float, 'col':16},
    'd0Sig1'  : {'cast':float, 'col':17},
    'd0Sig2'  : {'cast':float, 'col':18},

    'dR1'     : {'cast':float, 'col':19},
    'dR2'     : {'cast':float, 'col':20},

    'fpte1'   : {'cast':float, 'col':22},
    'fpte2'   : {'cast':float, 'col':23},
    'phi1'    : {'cast':float, 'col':24},
    'phi2'    : {'cast':float, 'col':25},
    'rphi1'   : {'cast':float, 'col':26},
    'rphi2'   : {'cast':float, 'col':27},
}

tests = {'total':{'count':0, 'lines':''}, 'LxySig':{'count':0, 'lines':''}, 'd0Sig':{'count':0, 'lines':''}, 'vtxChi2':{'count':0, 'lines':''}}

f = open(sys.argv[1])

for line in f:
    cols = line.strip('\n').split()
    vals = {key:config[key]['cast'](cols[config[key]['col']]) for key in config}

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

for key in ('total', 'LxySig', 'd0Sig', 'vtxChi2'):
    print '===', key, ':::', tests[key]['count']
    if True:
        print tests[key]['lines']
        print ''
