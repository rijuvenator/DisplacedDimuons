# -*- coding: utf-8 -*-
import ROOT as R
import DisplacedDimuons.Analysis.HistogramGetter as HG

FILES = {
    100  : R.TFile.Open('test_Trig_HTo2XTo2Mu2J_1000_150_100.root'),
    1000 : R.TFile.Open('test_Trig_HTo2XTo2Mu2J_1000_150_1000.root')
}

for cTau in FILES:
    for factor in (1, 2, 5, 10):
        h = HG.getHistogram(FILES[cTau], ('2Mu2J', (1000, 150, cTau)), 'genTime_{}'.format(factor))
        f = R.TF1('f'+str(cTau)+str(factor), 'expo')
        h.Fit(f, 'qWL' if factor != 1 else 'qL')
        print '{:3d} --> {:3d} : fitted cτ = {:7.3f} ± {:5.3f}'.format(cTau/10, cTau/10/factor, -1./f.GetParameter(1), f.GetParError(1)/f.GetParameter(1)**2.)
