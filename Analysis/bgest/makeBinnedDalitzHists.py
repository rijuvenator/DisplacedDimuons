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

singles = {}
for sample in itertools.chain(HG.BGORDER, ['Data']):

    singles[sample] = {'plot': R.TH3F('hDalitz_{}'.format(sample), ';#rho_{1};#rho_{2};M', 100, 0., 0.5, 100, 0., 0.5, 20, 50., 250.)}

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

    weight = float(cols[4])

    if 'Data' in name:
        sample = 'Data'
    elif 'QCD' in name:
        sample = 'QCD20toInf-ME'
    else:
        sample = name

    try:
        singles[sample]['plot'].Fill(pA/M, pB/M, M)
    except:
        pass

f.close()

X = R.TFile.Open('Dalitz{}.root'.format('' if ARGS.LXYSIGCUTOFF == 0. else '_'+str(int(ARGS.LXYSIGCUTOFF))), 'RECREATE')
for sample in singles:
    singles[sample]['plot'].Write()
X.Close()
