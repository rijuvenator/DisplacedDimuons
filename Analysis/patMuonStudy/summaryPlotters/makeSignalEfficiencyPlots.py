import DisplacedDimuons.Analysis.SummaryPlotter as SumPlotter
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
import DisplacedDimuons.Analysis.HistogramGetter as HG
R, makeSummaryPlot, initializeData, Plotter = SumPlotter.R, SumPlotter.makeSummaryPlot, SumPlotter.initializeData, SumPlotter.Plotter

##### Notes #####
# To make these plots, I copied the DeltaPhi plot (which had the numbers I needed) and only loaded the necessary numbers
# nEvents is really just nEvents
# run1eff I got from the 2014 analysis note
# Then the following changes to the SummaryPlotter module were necessary:
# - canvas cHeight 600 --> 500
# - legend resizeHeight scale 1.1 --> 1.3
# - both "start" values .16 --> .165

def safeDivide(x, y):
    try:
        return float(x)/float(y)
    except:
        return 0.

externalData = {
    (1000, 350,   35) : {'nEvents':27999., 'run1eff':0.033  },
    (1000, 350,  350) : {'nEvents':29997., 'run1eff':0.023  },
    (1000, 350, 3500) : {'nEvents':27999., 'run1eff':0.0033 },
    (1000, 150,   10) : {'nEvents':26000., 'run1eff':0.018  },
    (1000, 150,  100) : {'nEvents':30000., 'run1eff':0.044  },
    (1000, 150, 1000) : {'nEvents':29000., 'run1eff':0.0069 },
    (1000,  50,    4) : {'nEvents':30000., 'run1eff':0.0037 },
    (1000,  50,   40) : {'nEvents':28000., 'run1eff':0.018  },
    (1000,  50,  400) : {'nEvents':30000., 'run1eff':0.0027 },
    (1000,  20,    2) : {'nEvents':29000., 'run1eff':0.00   },
    (1000,  20,   20) : {'nEvents':27000., 'run1eff':0.00043},
    (1000,  20,  200) : {'nEvents':30000., 'run1eff':0.00029},
    ( 400, 150,   40) : {'nEvents':30000., 'run1eff':0.028  },
    ( 400, 150,  400) : {'nEvents':30000., 'run1eff':0.017  },
    ( 400, 150, 4000) : {'nEvents':30000., 'run1eff':0.0021 },
    ( 400,  50,    8) : {'nEvents':30000., 'run1eff':0.0075 },
    ( 400,  50,   80) : {'nEvents':28000., 'run1eff':0.029  },
    ( 400,  50,  800) : {'nEvents':30000., 'run1eff':0.0058 },
    ( 400,  20,    4) : {'nEvents':30000., 'run1eff':0.0016 },
    ( 400,  20,   40) : {'nEvents':30000., 'run1eff':0.0079 },
    ( 400,  20,  400) : {'nEvents':30000., 'run1eff':0.0015 },
    ( 200,  50,   20) : {'nEvents':25000., 'run1eff':0.0089 },
    ( 200,  50,  200) : {'nEvents':30000., 'run1eff':0.0081 },
    ( 200,  50, 2000) : {'nEvents':30000., 'run1eff':0.0012 },
    ( 200,  20,    7) : {'nEvents':30000., 'run1eff':0.0018 },
    ( 200,  20,   70) : {'nEvents':29000., 'run1eff':0.0085 },
    ( 200,  20,  700) : {'nEvents':30000., 'run1eff':0.0014 },
    ( 125,  50,   50) : {'nEvents':30000., 'run1eff':0.003  },
    ( 125,  50,  500) : {'nEvents':30000., 'run1eff':0.0012 },
    ( 125,  50, 5000) : {'nEvents':30000., 'run1eff':0.00017},
    ( 125,  20,   13) : {'nEvents':30000., 'run1eff':0.0016 },
    ( 125,  20,  130) : {'nEvents':30000., 'run1eff':0.0018 },
    ( 125,  20, 1300) : {'nEvents':30000., 'run1eff':0.00039},
}

DATA = initializeData()
with open('summaryPlotters/DeltaPhiCut.txt') as f:
    for line in f:
        cols = line.strip('\n').split()
        fs = '2Mu2J'
        sp = tuple(map(int, cols[0:3]))
        DATA[fs][sp]['C_P2_E'] = safeDivide(float(cols[5]), externalData[sp]['nEvents'])
        DATA[fs][sp]['Run1'  ] = externalData[sp]['run1eff']

makeSummaryPlot(
    DATA,
    '2Mu2J',
    ('C_P2_E', 'Run1'),
    ';;Counts',
    {'C_P2_E':'#varepsilon_{2#mu} (2016)', 'Run1':'#varepsilon_{2#mu} (2014)'},
    {'C_P2_E':R.kRed, 'Run1':R.kRed+2},
    {'min':0., 'max':0.11},
    'pdfs/Signal_Eff_Sel.pdf',
    'tr',
    LEGWIDTH=0.16,
)
