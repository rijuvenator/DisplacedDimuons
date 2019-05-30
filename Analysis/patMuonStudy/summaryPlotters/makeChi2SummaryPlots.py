import DisplacedDimuons.Analysis.SummaryPlotter as SumPlotter
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
import DisplacedDimuons.Analysis.HistogramGetter as HG
R, makeSummaryPlot, initializeData, Plotter = SumPlotter.R, SumPlotter.makeSummaryPlot, SumPlotter.initializeData, SumPlotter.Plotter

DATA = initializeData()
with open('summaryPlotters/Chi2Cut.txt') as f:
    for line in f:
        cols = line.strip('\n').split()
        fs = '2Mu2J'
        sp = tuple(map(int, cols[0:3]))
        DATA[fs][sp]['C_IN'] = float(cols[4])
        DATA[fs][sp]['C_50'] = float(cols[5])
        DATA[fs][sp]['C_20'] = float(cols[6])
        DATA[fs][sp]['C_10'] = float(cols[7])
        DATA[fs][sp]['C_05'] = float(cols[8])

        DATA[fs][sp]['G_IN'] = float(cols[10])
        DATA[fs][sp]['G_50'] = float(cols[11])
        DATA[fs][sp]['G_20'] = float(cols[12])
        DATA[fs][sp]['G_10'] = float(cols[13])
        DATA[fs][sp]['G_05'] = float(cols[14])

        DATA[fs][sp]['C_IN_E'] = float(cols[4])/float(cols[4])
        DATA[fs][sp]['C_50_E'] = float(cols[5])/float(cols[4])
        DATA[fs][sp]['C_20_E'] = float(cols[6])/float(cols[4])
        DATA[fs][sp]['C_10_E'] = float(cols[7])/float(cols[4])
        DATA[fs][sp]['C_05_E'] = float(cols[8])/float(cols[4])

        DATA[fs][sp]['G_IN_E'] = float(cols[10])/float(cols[10])
        DATA[fs][sp]['G_50_E'] = float(cols[11])/float(cols[10])
        DATA[fs][sp]['G_20_E'] = float(cols[12])/float(cols[10])
        DATA[fs][sp]['G_10_E'] = float(cols[13])/float(cols[10])
        DATA[fs][sp]['G_05_E'] = float(cols[14])/float(cols[10])

colors = [
    (255, 255, 178),
    (254, 204,  92),
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
    ('C_IN', 'C_50', 'C_20', 'C_10', 'C_05'),
    ';;Counts',
    {'C_IN':'#chi^{2} < #infty', 'C_50':'#chi^{2} < 50', 'C_20':'#chi^{2} < 20', 'C_10':'#chi^{2} < 10', 'C_05':'#chi^{2} < 5'},
    {'C_IN':7000, 'C_50':7001, 'C_20':7002, 'C_10':7003, 'C_05':7004},
    {'min':0., 'max':3500.},
    'pdfs/Chi2Cut_Total_Sel.pdf',
    'tr'
)

makeSummaryPlot(
    DATA,
    '2Mu2J',
    ('G_IN', 'G_50', 'G_20', 'G_10', 'G_05'),
    ';;Counts',
    {'G_IN':'#chi^{2} < #infty', 'G_50':'#chi^{2} < 50', 'G_20':'#chi^{2} < 20', 'G_10':'#chi^{2} < 10', 'G_05':'#chi^{2} < 5'},
    {'G_IN':7000, 'G_50':7001, 'G_20':7002, 'G_10':7003, 'G_05':7004},
    {'min':0., 'max':3500.},
    'pdfs/Chi2Cut_Total_Gen.pdf',
    'tr'
)

makeSummaryPlot(
    DATA,
    '2Mu2J',
    ('C_IN_E', 'C_50_E', 'C_20_E', 'C_10_E', 'C_05_E'),
    ';;Counts',
    {'C_IN_E':'#chi^{2} < #infty', 'C_50_E':'#chi^{2} < 50', 'C_20_E':'#chi^{2} < 20', 'C_10_E':'#chi^{2} < 10', 'C_05_E':'#chi^{2} < 5'},
    {'C_IN_E':7000, 'C_50_E':7001, 'C_20_E':7002, 'C_10_E':7003, 'C_05_E':7004},
    {'min':0.7, 'max':1.},
    'pdfs/Chi2Cut_Eff_Sel.pdf',
    'br'
)

makeSummaryPlot(
    DATA,
    '2Mu2J',
    ('G_IN_E', 'G_50_E', 'G_20_E', 'G_10_E', 'G_05_E'),
    ';;Counts',
    {'G_IN_E':'#chi^{2} < #infty', 'G_50_E':'#chi^{2} < 50', 'G_20_E':'#chi^{2} < 20', 'G_10_E':'#chi^{2} < 10', 'G_05_E':'#chi^{2} < 5'},
    {'G_IN_E':7000, 'G_50_E':7001, 'G_20_E':7002, 'G_10_E':7003, 'G_05_E':7004},
    {'min':0.7, 'max':1.},
    'pdfs/Chi2Cut_Eff_Gen.pdf',
    'br'
)
