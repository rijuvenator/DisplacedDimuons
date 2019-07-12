import ROOT as R
R.PyConfig.IgnoreCommandLineOptions = True
R.gROOT.SetBatch(True)
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.RootTools as RT
import argparse, itertools

PARSER = argparse.ArgumentParser()
PARSER.add_argument('FILE', help='which file to run over')
PARSER.add_argument('--cutoff', dest='LXYSIGCUTOFF', type=float, default=0.)
ARGS = PARSER.parse_args()

MKeys = range(50, 201, 10)

singles = {}
for sample in itertools.chain(HG.BGORDER, ['Data']):

    singles[sample] = {}

    for M in MKeys:
        singles[sample][M] = {'plot': R.TH2F('hDalitz_{}_{}'.format(M, sample), ';#rho_{1};#rho_{2};Counts', 100, 0., 0.5, 100, 0., 0.5)}

boolMap = {True:'Less', False:'More'}

f = open(ARGS.FILE)
for line in f:
    cols = line.strip('\n').split()

    name     = cols[0]
    LxySig   = float(cols[15])
    deltaPhi = float(cols[18])
    Lxy      = float(cols[20])
    Sig      = float(cols[21])

    if LxySig < ARGS.LXYSIGCUTOFF: continue

    pA, pB, pM = map(float, cols[23:])

    M = pA+pB+pM

    MKey = int(round(M/10)*10)

    if abs(M-MKey)/MKey > 0.01: continue

    weight = float(cols[4])

    if 'Data' in name:
        sample = 'Data'
    elif 'QCD' in name:
        sample = 'QCD20toInf-ME'
    else:
        sample = name

    try:
        singles[sample][MKey]['plot'].Fill(pA/M, pB/M)
    except:
        pass

f.close()

X = R.TFile.Open('Dalitz{}.root'.format('' if ARGS.LXYSIGCUTOFF == 0. else '_'+str(int(ARGS.LXYSIGCUTOFF))), 'RECREATE')
for sample in singles:
    for key in singles[sample]:
        singles[sample][key]['plot'].Write()
X.Close()
