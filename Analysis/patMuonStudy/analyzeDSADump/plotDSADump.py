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
    'trkChi2'    : R.TH1F('h1' , ';track #chi^{2}/dof;Counts'       , 100, 0., 5. ),
    'maxtrkChi2' : R.TH1F('h2' , ';max track #chi^{2}/dof;Counts'   , 100, 0., 5. ),
    'PCA'        : R.TH1F('h3' , ';P.C.A. #minus vPos [cm];Counts'              , 100, 0., 10.),
    'PCA_XY'     : R.TH1F('h4' , ';transverse P.C.A. #minus vPos [cm];Counts'   , 100, 0., 10.),
    'PCA_Z'      : R.TH1F('h5' , ';longitudinal P.C.A. #minus vPos [cm];Counts' , 100, 0., 10.),
    'd0Sig'      : R.TH1F('h6' , ';|d_{0}|/#sigma_{d_{0}};Counts'               , 100, 0., 50.),
    'mind0Sig'   : R.TH1F('h7' , ';min |d_{0}|/#sigma_{d_{0}};Counts'           , 100, 0., 50.),
    'LxySig'     : R.TH1F('h8' , ';L_{xy}/#sigma_{L_{xy}};Counts'               , 100, 0., 50.),
    'vtxChi2'    : R.TH1F('h9' , ';vtx #chi^{2};Counts'                         , 100, 0., 20.),
    'nCSCHits'   : R.TH1F('h10', ';N(CSC Hits);Counts'                          ,  50, 0., 50.),
    'nDTHits'    : R.TH1F('h11', ';N(DT Hits);Counts'                           ,  50, 0., 50.),
    'nHitsScat'  : R.TH2F('h12', ';N(CSC Hits);N(DT Hits);Counts'               ,  30, 0., 30., 40, 0., 40.),
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

    'nCSC1'    : {'cast':int  , 'col':35},
    'nCSC2'    : {'cast':int  , 'col':36},
    'nDT1'     : {'cast':int  , 'col':37},
    'nDT2'     : {'cast':int  , 'col':38},
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

    for val in ('PCA', 'PCA_XY', 'PCA_Z', 'LxySig', 'vtxChi2'):
        h[val].Fill(vals[val])

    h['d0Sig'].Fill(vals['d0Sig1'])
    h['d0Sig'].Fill(vals['d0Sig2'])
    h['mind0Sig'].Fill(min(vals['d0Sig1'], vals['d0Sig2']))

    for idx in ('1', '2'):
        nCSC, nDT = vals['nCSC'+idx], vals['nDT'+idx]
        if nCSC == 0:
            h['nDTHits'].Fill(nDT)
        elif nDT == 0:
            h['nCSCHits'].Fill(nCSC)
        else:
            h['nHitsScat'].Fill(nCSC, nDT)

dtype = 'Data'
if args.SIG: dtype = 'Signal'

# make plots, special things for 2D
for key in ('trkChi2', 'maxtrkChi2', 'PCA', 'PCA_XY', 'PCA_Z', 'd0Sig', 'mind0Sig', 'LxySig', 'vtxChi2', 'nDTHits', 'nCSCHits', 'nHitsScat'):
    IS2D = 'Scat' in key
    logy = (args.SIG and ('PCA' in key or key.endswith('Hits')))

    c = Plotter.Canvas(lumi='DSA muons in DSA-DSA dimuons in {}'.format(dtype), logy=logy)
    p = Plotter.Plot(h[key], '', '', 'hist' if not IS2D else 'text')
    c.addMainPlot(p)
    p.setColor(R.kBlue, which='L')
    c.setMaximum()

    if not IS2D:
        pave = c.makeStatsBox(p, color=R.kBlue)

    c.firstPlot.scaleTitleOffsets(1.2, axes='X')

    if IS2D:
        # scale down if you want a percent
        if True:
            p.Scale(100./p.GetEntries())
            R.gStyle.SetPaintTextFormat('.1f')
        if True:
            R.gStyle.SetPaintTextFormat('.0f')
        c.mainPad.SetLogz()
        c.scaleMargins(1.75, edges='R')
        c.scaleMargins(0.8, edges='L')

    c.cleanup('{}-{}.pdf'.format(key, dtype))

# cumulative plots
for key in ('nDTHits', 'nCSCHits'):
    z = h[key].GetCumulative()
    z.Scale(1./h[key].Integral(0, h[key].GetNbinsX()+1))
    c = Plotter.Canvas(lumi='DSA muons in DSA-DSA dimuons in {}'.format(dtype), logy=True)
    p = Plotter.Plot(z, '', '', 'hist')
    c.addMainPlot(p)
    p.setColor(R.kBlue, which='L')
    c.firstPlot.SetMaximum(1.)
    c.firstPlot.SetMinimum(1.e-3)
    c.cleanup('{}-Cum-{}.pdf'.format(key, dtype))
