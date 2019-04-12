import sys
import numpy as np
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT

h = {
    'd0Sig-S':R.TH1F('h1', ';d_{0}/#sigma_{d_{0}};Counts'          , 20, np.logspace(-3., 5., 21)   ),
    'd0Sig-B':R.TH1F('h2', ';d_{0}/#sigma_{d_{0}};Counts'          , 20, np.logspace(-3., 5., 21)   ),
    'dPhi-S' :R.TH1F('h3', ';#Delta#phi(original, refitted);Counts', 40, -R.TMath.Pi(), R.TMath.Pi()),
    'dPhi-B' :R.TH1F('h4', ';#Delta#phi(original, refitted);Counts', 40, -R.TMath.Pi(), R.TMath.Pi()),
    'd0-S'   :R.TH1F('h5', ';d_{0};Counts'                         , 20, np.logspace(-3., 5., 21)   ),
    'd0-B'   :R.TH1F('h6', ';d_{0};Counts'                         , 20, np.logspace(-3., 5., 21)   ),
}

def deltaPhi(phi1, phi2):
    v1 = R.TVector3()
    v2 = R.TVector3()
    v1.SetPtEtaPhi(1., 1., phi1)
    v2.SetPtEtaPhi(1., 1., phi2)
    return v1.DeltaPhi(v2)

l = [
    1094462867,
    1283051327,
    1790870957,
    224954587,
    2660937567,
    706256787,
    819173247,
    871330817,
    1840232227,
    214390057,
    229870167,
    246186967,
]

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


f = open(sys.argv[1])

c = 0
for line in f:
    cols = line.strip('\n').split()
    vals = {key:config[key]['cast'](cols[config[key]['col']]) for key in config}

    if vals['fpte1'] < 0.01 or vals['fpte2'] < 0.01 or vals['fpte1'] > 1. or vals['fpte2'] > 1.:
        c += 1

        if vals['event'] in l:
            print vals['event']

    for i in ('1', '2'):
        if vals['fpte'+i] < 0.01:
            h['d0Sig-S'].Fill(vals['d0Sig'+i])
            h['d0-S']   .Fill(vals['d0'+i])
            h['dPhi-S'] .Fill(deltaPhi(vals['phi'+i], vals['rphi'+i]))
        else:
            h['d0Sig-B'].Fill(vals['d0Sig'+i])
            h['d0-B']   .Fill(vals['d0'+i])
            h['dPhi-B'] .Fill(deltaPhi(vals['phi'+i], vals['rphi'+i]))


print c

for i in ('d0', 'd0Sig', 'dPhi'):
    name = i
    c = Plotter.Canvas(lumi='DSA muons in DSA-DSA dimuons in Data')
    p = {
        'small':Plotter.Plot(h[name+'-S'], 'refitted #sigma_{p_{T}}/p_{T} < 1%', 'l', 'hist'),
        'big'  :Plotter.Plot(h[name+'-B'], 'refitted #sigma_{p_{T}}/p_{T} > 1%', 'l', 'hist'),
    }
    c.addMainPlot(p['small'])
    c.addMainPlot(p['big']  )
    p['small'].setColor(R.kRed, which='L')
    p['big'].setColor(R.kBlue, which='L')
    if 'dPhi' not in name:
        c.mainPad.SetLogx()
    c.setMaximum()
    c.makeLegend(lWidth=.3, pos='tr')
    c.legend.resizeHeight()
    p1 = c.makeStatsBox(p['small'], color=R.kRed)
    p2 = c.makeStatsBox(p['big'], color=R.kBlue)
    Plotter.MOVE_OBJECT(p1, Y=-.1)
    Plotter.MOVE_OBJECT(p2, Y=-.3)
    p2.SetX1(p1.GetX1())
    c.firstPlot.scaleTitleOffsets(1.2, axes='X')
    c.cleanup('{}.pdf'.format(name))
