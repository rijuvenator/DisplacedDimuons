import DisplacedDimuons.Analysis.SummaryPlotter as SumPlotter
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
import DisplacedDimuons.Analysis.HistogramGetter as HG
R, makeSummaryPlot, initializeData, Plotter = SumPlotter.R, SumPlotter.makeSummaryPlot, SumPlotter.initializeData, SumPlotter.Plotter

DATA = initializeData()
with open('summaryPlotters/LxySigCut.txt') as f:
    for line in f:
        cols = line.strip('\n').split()
        fs = '2Mu2J'
        sp = tuple(map(int, cols[0:3]))
        DATA[fs][sp]['C_0'] = float(cols[4])
        DATA[fs][sp]['C_1'] = float(cols[5])
        DATA[fs][sp]['C_3'] = float(cols[6])
        DATA[fs][sp]['C_5'] = float(cols[7])
        DATA[fs][sp]['C_7'] = float(cols[8])

        DATA[fs][sp]['G_0'] = float(cols[10])
        DATA[fs][sp]['G_1'] = float(cols[11])
        DATA[fs][sp]['G_3'] = float(cols[12])
        DATA[fs][sp]['G_5'] = float(cols[13])
        DATA[fs][sp]['G_7'] = float(cols[14])

        DATA[fs][sp]['C_0_E'] = float(cols[4])/float(cols[4])
        DATA[fs][sp]['C_1_E'] = float(cols[5])/float(cols[4])
        DATA[fs][sp]['C_3_E'] = float(cols[6])/float(cols[4])
        DATA[fs][sp]['C_5_E'] = float(cols[7])/float(cols[4])
        DATA[fs][sp]['C_7_E'] = float(cols[8])/float(cols[4])

        DATA[fs][sp]['G_0_E'] = float(cols[10])/float(cols[10])
        DATA[fs][sp]['G_1_E'] = float(cols[11])/float(cols[10])
        DATA[fs][sp]['G_3_E'] = float(cols[12])/float(cols[10])
        DATA[fs][sp]['G_5_E'] = float(cols[13])/float(cols[10])
        DATA[fs][sp]['G_7_E'] = float(cols[14])/float(cols[10])

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
    ('C_0', 'C_1', 'C_3', 'C_5', 'C_7'),
    ';;Counts',
    {'C_0':'L_{xy} sig. > 0', 'C_1':'L_{xy} sig. > 1', 'C_3':'L_{xy} sig. > 3', 'C_5':'L_{xy} sig. > 5', 'C_7':'L_{xy} sig. > 7'},
    {'C_0':7000, 'C_1':7001, 'C_3':7002, 'C_5':7003, 'C_7':7004},
    {'min':0., 'max':3500.},
    'pdfs/LxySigCut_Total_Sel.pdf',
    'tr',
    False,
    0.2,
)

makeSummaryPlot(
    DATA,
    '2Mu2J',
    ('G_0', 'G_1', 'G_3', 'G_5', 'G_7'),
    ';;Counts',
    {'G_0':'L_{xy} sig. > 0', 'G_1':'L_{xy} sig. > 1', 'G_3':'L_{xy} sig. > 3', 'G_5':'L_{xy} sig. > 5', 'G_7':'L_{xy} sig. > 7'},
    {'G_0':7000, 'G_1':7001, 'G_3':7002, 'G_5':7003, 'G_7':7004},
    {'min':0., 'max':3500.},
    'pdfs/LxySigCut_Total_Gen.pdf',
    'tr',
    False,
    0.2,
)

makeSummaryPlot(
    DATA,
    '2Mu2J',
    ('C_0_E', 'C_1_E', 'C_3_E', 'C_5_E', 'C_7_E'),
    ';;Counts',
    {'C_0_E':'L_{xy} sig. > 0', 'C_1_E':'L_{xy} sig. > 1', 'C_3_E':'L_{xy} sig. > 3', 'C_5_E':'L_{xy} sig. > 5', 'C_7_E':'L_{xy} sig. > 7'},
    {'C_0_E':7000, 'C_1_E':7001, 'C_3_E':7002, 'C_5_E':7003, 'C_7_E':7004},
    {'min':0.5, 'max':1.},
    'pdfs/LxySigCut_Eff_Sel.pdf',
    'br',
    False,
    0.2,
)

makeSummaryPlot(
    DATA,
    '2Mu2J',
    ('G_0_E', 'G_1_E', 'G_3_E', 'G_5_E', 'G_7_E'),
    ';;Counts',
    {'G_0_E':'L_{xy} sig. > 0', 'G_1_E':'L_{xy} sig. > 1', 'G_3_E':'L_{xy} sig. > 3', 'G_5_E':'L_{xy} sig. > 5', 'G_7_E':'L_{xy} sig. > 7'},
    {'G_0_E':7000, 'G_1_E':7001, 'G_3_E':7002, 'G_5_E':7003, 'G_7_E':7004},
    {'min':0.5, 'max':1.},
    'pdfs/LxySigCut_Eff_Gen.pdf',
    'br',
    False,
    0.2,
)
