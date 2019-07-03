import DisplacedDimuons.Analysis.SummaryPlotter as SumPlotter
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
import DisplacedDimuons.Analysis.HistogramGetter as HG
R, makeSummaryPlot, initializeData, Plotter = SumPlotter.R, SumPlotter.makeSummaryPlot, SumPlotter.initializeData, SumPlotter.Plotter

def safeDivide(a, b):
    return a/b if b != 0. else 0.

DATA = initializeData()
with open('summaryPlotters/TrackChi2Cut.txt') as f:
    for line in f:
        cols = line.strip('\n').split()
        fs = '2Mu2J'
        sp = tuple(map(int, cols[0:3]))
        DATA[fs][sp]['C_IN'] = float(cols[4])
        DATA[fs][sp]['C_10'] = float(cols[5])
        DATA[fs][sp]['C_04'] = float(cols[6])
        DATA[fs][sp]['C_03'] = float(cols[7])
        DATA[fs][sp]['C_25'] = float(cols[8])
        DATA[fs][sp]['C_02'] = float(cols[9])

        DATA[fs][sp]['G_IN'] = float(cols[11])
        DATA[fs][sp]['G_10'] = float(cols[12])
        DATA[fs][sp]['G_04'] = float(cols[13])
        DATA[fs][sp]['G_03'] = float(cols[14])
        DATA[fs][sp]['G_25'] = float(cols[15])
        DATA[fs][sp]['G_02'] = float(cols[16])

        DATA[fs][sp]['C_IN_E'] = safeDivide(float(cols[ 4]), float(cols[ 4]))
        DATA[fs][sp]['C_10_E'] = safeDivide(float(cols[ 5]), float(cols[ 4]))
        DATA[fs][sp]['C_04_E'] = safeDivide(float(cols[ 6]), float(cols[ 4]))
        DATA[fs][sp]['C_03_E'] = safeDivide(float(cols[ 7]), float(cols[ 4]))
        DATA[fs][sp]['C_25_E'] = safeDivide(float(cols[ 8]), float(cols[ 4]))
        DATA[fs][sp]['C_02_E'] = safeDivide(float(cols[ 9]), float(cols[ 4]))

        DATA[fs][sp]['G_IN_E'] = safeDivide(float(cols[11]), float(cols[11]))
        DATA[fs][sp]['G_10_E'] = safeDivide(float(cols[12]), float(cols[11]))
        DATA[fs][sp]['G_04_E'] = safeDivide(float(cols[13]), float(cols[11]))
        DATA[fs][sp]['G_03_E'] = safeDivide(float(cols[14]), float(cols[11]))
        DATA[fs][sp]['G_25_E'] = safeDivide(float(cols[15]), float(cols[11]))
        DATA[fs][sp]['G_02_E'] = safeDivide(float(cols[16]), float(cols[11]))

colors = [
    (255, 255, 178),
    (254, 217, 118),
    (254, 178,  76),
    (253, 141,  60),
    (240,  59,  32),
    (189,   0,  38),
]
rcolors = []
idx = 7000
for i, c in enumerate(colors):
    #idx = R.TColor.GetFreeColorIndex()
    rcolors.append(R.TColor(idx+i, c[0]/255., c[1]/255., c[2]/255.))

makeSummaryPlot(
    DATA,
    '2Mu2J',
    ('C_IN', 'C_10', 'C_04', 'C_03', 'C_25', 'C_02'),
    ';;Counts',
    {'C_IN':'#chi^{2} < #infty', 'C_10':'#chi^{2} < 10', 'C_04':'#chi^{2} < 4', 'C_03':'#chi^{2} < 3', 'C_25':'#chi^{2} < 2.5', 'C_02':'#chi^{2} < 2'},
    {'C_IN':7000, 'C_10':7001, 'C_04':7002, 'C_03':7003, 'C_25':7004, 'C_02':7005},
    {'min':0., 'max':3500.},
    'pdfs/TrackChi2Cut_Total_Sel.pdf',
    'tr'
)

makeSummaryPlot(
    DATA,
    '2Mu2J',
    ('G_IN', 'G_10', 'G_04', 'G_03', 'G_25', 'G_02'),
    ';;Counts',
    {'G_IN':'#chi^{2} < #infty', 'G_10':'#chi^{2} < 10', 'G_04':'#chi^{2} < 4', 'G_03':'#chi^{2} < 3', 'G_25':'#chi^{2} < 2.5', 'G_02':'#chi^{2} < 2'},
    {'G_IN':7000, 'G_10':7001, 'G_04':7002, 'G_03':7003, 'G_25':7004, 'G_02':7005},
    {'min':0., 'max':3500.},
    'pdfs/TrackChi2Cut_Total_Gen.pdf',
    'tr'
)

makeSummaryPlot(
    DATA,
    '2Mu2J',
    ('C_IN_E', 'C_10_E', 'C_04_E', 'C_03_E', 'C_25_E', 'C_02_E'),
    ';;Counts',
    {'C_IN_E':'#chi^{2} < #infty', 'C_10_E':'#chi^{2} < 10', 'C_04_E':'#chi^{2} < 4', 'C_03_E':'#chi^{2} < 3', 'C_25_E':'#chi^{2} < 2.5', 'C_02_E':'#chi^{2} < 2'},
    {'C_IN_E':7000, 'C_10_E':7001, 'C_04_E':7002, 'C_03_E':7003, 'C_25_E':7004, 'C_02_E':7005},
    {'min':0.7, 'max':1.},
    'pdfs/TrackChi2Cut_Eff_Sel.pdf',
    'br'
)

makeSummaryPlot(
    DATA,
    '2Mu2J',
    ('G_IN_E', 'G_10_E', 'G_04_E', 'G_03_E', 'G_25_E', 'G_02_E'),
    ';;Counts',
    {'G_IN_E':'#chi^{2} < #infty', 'G_10_E':'#chi^{2} < 10', 'G_04_E':'#chi^{2} < 4', 'G_03_E':'#chi^{2} < 3', 'G_25_E':'#chi^{2} < 2.5', 'G_02_E':'#chi^{2} < 2'},
    {'G_IN_E':7000, 'G_10_E':7001, 'G_04_E':7002, 'G_03_E':7003, 'G_25_E':7004, 'G_02_E':7005},
    {'min':0.7, 'max':1.},
    'pdfs/TrackChi2Cut_Eff_Gen.pdf',
    'br'
)
