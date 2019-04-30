import sys, argparse
import numpy as np
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.PlotterParser as PP
import DisplacedDimuons.Analysis.RootTools as RT

PP.PARSER.add_argument('FILE')
PP.PARSER.add_argument('--hyb', dest='HYB', action='store_true')
PP.PARSER.add_argument('--mc' , dest='MC' , action='store_true')
PP.PARSER.add_argument('--sig', dest='SIG', action='store_true')
args = PP.PARSER.parse_args()

h = {
    'd0Sig-S':R.TH1F('h1', ';d_{0}/#sigma_{d_{0}};Counts'            , 80, np.logspace(-3., 5., 81)   ),
    'd0Sig-B':R.TH1F('h2', ';d_{0}/#sigma_{d_{0}};Counts'            , 80, np.logspace(-3., 5., 81)   ),
    'dPhi-S' :R.TH1F('h3', ';|#Delta#phi(original, refitted)|;Counts', 80, 0.           , R.TMath.Pi()),
    'dPhi-B' :R.TH1F('h4', ';|#Delta#phi(original, refitted)|;Counts', 80, 0.           , R.TMath.Pi()),
    'd0-S'   :R.TH1F('h5', ';d_{0};Counts'                           , 80, np.logspace(-3., 5., 81)   ),
    'd0-B'   :R.TH1F('h6', ';d_{0};Counts'                           , 80, np.logspace(-3., 5., 81)   ),

    'dR'     :R.TH1F('h7', ';proximity #DeltaR;Counts'               , 37, 0.04, 0.41),
    'DCA'    :R.TH1F('h8', ';D.C.A. [cm];Counts'                     , 50, 0.  , 1000.),
}

def deltaPhi(phi1, phi2):
    v1 = R.TVector3()
    v2 = R.TVector3()
    v1.SetPtEtaPhi(1., 1., phi1)
    v2.SetPtEtaPhi(1., 1., phi2)
    return abs(v1.DeltaPhi(v2))

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
    'name'     : {'cast':str  , 'col': 0},
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


f = open(args.FILE)

c = 0
nDR7 = 0
for line in f:
    cols = line.strip('\n').split()
    vals = {key:config[key]['cast'](cols[config[key]['col']]) for key in config}

    h['DCA'].Fill(vals['DCA'])

    if vals['fpte1'] < 0.01 or vals['fpte2'] < 0.01:
        c += 1

        h['DCA'].Fill(vals['DCA'])

        if vals['event'] in l:
            print vals['event']

#    if vals['dR1'] < 0.07 or vals['dR2'] < 0.07:
#        nDR7 += 1

    for i in ('1', '2'):
        if vals['fpte'+i] < 0.01:
            h['d0Sig-S'].Fill(vals['d0Sig'+i])
            h['d0-S']   .Fill(vals['d0'+i])
            h['dPhi-S'] .Fill(deltaPhi(vals['phi'+i], vals['rphi'+i]))
        else:
            h['d0Sig-B'].Fill(vals['d0Sig'+i])
            h['d0-B']   .Fill(vals['d0'+i])
            h['dPhi-B'] .Fill(deltaPhi(vals['phi'+i], vals['rphi'+i]))

#        if vals['nDSA'] < 10:
#            if i == '2' and vals['type'] == 'HYB': continue
#            if vals['dR'+i] > .4 and vals['dR'+i] != float('inf'): print line.strip('\n')
#            if 'Data' not in vals['name'] and 'QCD' not in vals['name']: continue
#            h['dR'].Fill(vals['dR'+i])


print c
print nDR7

if args.HYB:
    rtype = 'DSA-PAT'
    fname = '-HYB'
else:
    rtype = 'DSA-DSA'
    fname = ''

if args.MC:
    dtype = 'MC'
elif args.SIG:
    dtype = 'Signal'
else:
    dtype = 'Data'

for i in ('d0', 'd0Sig', 'dPhi'):
    name = i
    c = Plotter.Canvas(lumi='DSA muons in {} dimuons in {}'.format(rtype, dtype), logy=name=='dPhi')
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
    c.cleanup('{}{}.pdf'.format(name, fname))

if False:
    c = Plotter.Canvas(lumi='DSA muons in {} dimuons in {}'.format(rtype, dtype))
    p = Plotter.Plot(h['dR'], '', '', 'hist')
    c.addMainPlot(p)
    p.setColor(R.kBlue, which='L')
    c.setMaximum()
    pave = c.makeStatsBox(p, color=R.kBlue)
    c.firstPlot.scaleTitleOffsets(1.2, axes='X')
    c.cleanup('dR{}.pdf'.format(fname))

if True:
    c = Plotter.Canvas(lumi='DSA muons in {} dimuons in {}'.format(rtype, dtype), logy=True)
    p = Plotter.Plot(h['DCA'], '', '', 'hist')
    c.addMainPlot(p)
    p.setColor(R.kBlue, which='L')
    c.setMaximum()
    pave = c.makeStatsBox(p, color=R.kBlue)
    c.firstPlot.scaleTitleOffsets(1.2, axes='X')
    c.cleanup('DCA{}.pdf'.format(fname))
