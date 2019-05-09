import sys, argparse
import numpy as np
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.PlotterParser as PP
import DisplacedDimuons.Analysis.RootTools as RT

PP.PARSER.add_argument('FILE')
PP.PARSER.add_argument('--sig', dest='SIG', action='store_true')
args = PP.PARSER.parse_args()

h = {
    'trkChi2'    : R.TH1F('h1', ';track #chi^{2}/dof;Counts'       , 100, 0., 5. ),
    'maxtrkChi2' : R.TH1F('h2', ';max track #chi^{2}/dof;Counts'   , 100, 0., 5. ),
    'PCA'        : R.TH1F('h3', ';P.C.A. #minus vPos [cm];Counts'              , 100, 0., 10.),
    'PCA_XY'     : R.TH1F('h4', ';transverse P.C.A. #minus vPos [cm];Counts'   , 100, 0., 10.),
    'PCA_Z'      : R.TH1F('h5', ';longitudinal P.C.A. #minus vPos [cm];Counts' , 100, 0., 10.),
}

def deltaPhi(phi1, phi2):
    v1 = R.TVector3()
    v2 = R.TVector3()
    v1.SetPtEtaPhi(1., 1., phi1)
    v2.SetPtEtaPhi(1., 1., phi2)
    return abs(v1.DeltaPhi(v2))

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


f = open(args.FILE)

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

    h['trkChi2'].Fill(vals['trkChi21'])
    h['trkChi2'].Fill(vals['trkChi22'])

    h['maxtrkChi2'].Fill(max(vals['trkChi21'], vals['trkChi22']))

    for val in ('PCA', 'PCA_XY', 'PCA_Z'):
        h[val].Fill(vals[val])

dtype = 'Data'
if args.SIG: dtype = 'Signal'

for key in ('trkChi2', 'maxtrkChi2', 'PCA', 'PCA_XY', 'PCA_Z'):
    c = Plotter.Canvas(lumi='DSA muons in DSA-DSA dimuons in {}'.format(dtype), logy=(args.SIG and 'PCA' in key))
    p = Plotter.Plot(h[key], '', '', 'hist')
    c.addMainPlot(p)
    p.setColor(R.kBlue, which='L')
    c.setMaximum()
    pave = c.makeStatsBox(p, color=R.kBlue)
    c.firstPlot.scaleTitleOffsets(1.2, axes='X')
    c.cleanup('{}-{}.pdf'.format(key, dtype))
