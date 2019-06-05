import DisplacedDimuons.Analysis.SummaryPlotter as SumPlotter
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
import DisplacedDimuons.Analysis.HistogramGetter as HG
R, makeSummaryPlot, initializeData, Plotter = SumPlotter.R, SumPlotter.makeSummaryPlot, SumPlotter.initializeData, SumPlotter.Plotter

def safeDivide(x, y):
    try:
        return float(x)/float(y)
    except:
        return 0.

DATA = initializeData()
with open('summaryPlotters/DeltaPhiCut.txt') as f:
    for line in f:
        cols = line.strip('\n').split()
        fs = '2Mu2J'
        sp = tuple(map(int, cols[0:3]))
        DATA[fs][sp]['C_IN'] = float(cols[4])
        DATA[fs][sp]['C_P2'] = float(cols[5])

        DATA[fs][sp]['G_IN'] = float(cols[7])
        DATA[fs][sp]['G_P2'] = float(cols[8])

        DATA[fs][sp]['C_IN_E'] = safeDivide(float(cols[4]), float(cols[4]))
        DATA[fs][sp]['C_P2_E'] = safeDivide(float(cols[5]), float(cols[4]))

        DATA[fs][sp]['G_IN_E'] = safeDivide(float(cols[7]), float(cols[7]))
        DATA[fs][sp]['G_P2_E'] = safeDivide(float(cols[8]), float(cols[7]))

colors = [
    (255, 255, 178),
    (254, 204,  92),
]
rcolors = []
idx = 7000
for i, c in enumerate(colors):
    #idx = R.TColor.GetFreeColorIndex()
    rcolors.append(R.TColor(idx+i, c[0]/255., c[1]/255., c[2]/255.))

makeSummaryPlot(
    DATA,
    '2Mu2J',
    ('C_IN', 'C_P2'),
    ';;Counts',
    {'C_IN':'|#Delta#Phi| < #infty', 'C_P2':'|#Delta#Phi| < #pi/2'},
    {'C_IN':R.kRed+2, 'C_P2':R.kRed},
    {'min':0., 'max':3500.},
    'pdfs/DeltaPhiCut_Total_Sel.pdf',
    'tr'
)

makeSummaryPlot(
    DATA,
    '2Mu2J',
    ('G_IN', 'G_P2'),
    ';;Counts',
    {'G_IN':'|#Delta#Phi| < #infty', 'G_P2':'|#Delta#Phi| < #pi/2'},
    {'G_IN':R.kRed+2, 'G_P2':R.kRed},
    {'min':0., 'max':3500.},
    'pdfs/DeltaPhiCut_Total_Gen.pdf',
    'tr'
)

makeSummaryPlot(
    DATA,
    '2Mu2J',
    ('C_IN_E', 'C_P2_E'),
    ';;Counts',
    {'C_IN_E':'|#Delta#Phi| < #infty', 'C_P2_E':'|#Delta#Phi| < #pi/2'},
    {'C_IN_E':0, 'C_P2_E':R.kRed},
    {'min':0.985, 'max':1.0},
    'pdfs/DeltaPhiCut_Eff_Sel.pdf',
    'tr'
)

makeSummaryPlot(
    DATA,
    '2Mu2J',
    ('G_IN_E', 'G_P2_E'),
    ';;Counts',
    {'G_IN_E':'|#Delta#Phi| < #infty', 'G_P2_E':'|#Delta#Phi| < #pi/2'},
    {'G_IN_E':0, 'G_P2_E':R.kRed},
    {'min':0.985, 'max':1.0},
    'pdfs/DeltaPhiCut_Eff_Gen.pdf',
    'tr'
)
