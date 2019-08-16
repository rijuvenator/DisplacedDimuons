import ROOT as R
R.PyConfig.IgnoreCommandLineOptions = True
R.gROOT.SetBatch(True)
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.RootTools as RT
import argparse, itertools

PARSER = argparse.ArgumentParser()
PARSER.add_argument('FILE', help='which file to run over')
PARSER.add_argument('--cutoff', dest='LXYSIGCUTOFF', type=float, default=7.)
ARGS = PARSER.parse_args()

singles = {}
for sample in itertools.chain(HG.BGORDER, ['Data']):

    singles[sample] = {
        'deltaPhi-Lxy-Num' : {'plot': R.TH1F('hDeltaPhiLxyNum'+'_'+sample, ';|#Delta#Phi|', 100, 0., R.TMath.Pi()   ), 'legName':''},
        'deltaPhi-Lxy-Den' : {'plot': R.TH1F('hDeltaPhiLxyDen'+'_'+sample, ';|#Delta#Phi|', 100, 0., R.TMath.Pi()   ), 'legName':''},
        'deltaPhi-Sig-Num' : {'plot': R.TH1F('hDeltaPhiSigNum'+'_'+sample, ';|#Delta#Phi|', 100, 0., R.TMath.Pi()   ), 'legName':''},
        'deltaPhi-Sig-Den' : {'plot': R.TH1F('hDeltaPhiSigDen'+'_'+sample, ';|#Delta#Phi|', 100, 0., R.TMath.Pi()   ), 'legName':''},
    }

boolMap = {True:'Less', False:'More'}

f = open(ARGS.FILE)
for line in f:
    cols = line.strip('\n').split()

    name     = cols[0]
    deltaPhi = float(cols[18])
    Lxy      = float(cols[20])
    Sig      = float(cols[21])

    weight = float(cols[4])

    if 'Data' in name:
        sample = 'Data'
    elif 'QCD' in name:
        sample = 'QCD20toInf-ME'
    else:
        sample = name

    singles[sample]['deltaPhi-Lxy-Num']['plot'].Fill(deltaPhi, Lxy*weight)
    singles[sample]['deltaPhi-Lxy-Den']['plot'].Fill(deltaPhi,     weight)
    singles[sample]['deltaPhi-Sig-Num']['plot'].Fill(deltaPhi, Sig*weight)
    singles[sample]['deltaPhi-Sig-Den']['plot'].Fill(deltaPhi,     weight)

f.close()

singles[sample]['deltaPhi-Lxy-Num']['plot'].Divide(singles[sample]['deltaPhi-Lxy-Den']['plot'])
singles[sample]['deltaPhi-Sig-Num']['plot'].Divide(singles[sample]['deltaPhi-Sig-Den']['plot'])

X = R.TFile.Open('roots/Avg.root', 'RECREATE')
for sample in singles:
    for key in singles[sample]:
        singles[sample][key]['plot'].Write()
X.Close()
