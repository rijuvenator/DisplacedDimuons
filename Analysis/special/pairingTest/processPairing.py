import re
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr

Patterns = {
    'HTo2XTo4Mu'   : re.compile(r'(.*)_HTo2XTo4Mu_(\d{3,4})_(\d{2,3})_(\d{1,4})'),
    'HTo2XTo2Mu2J' : re.compile(r'(.*)_HTo2XTo2Mu2J_(\d{3,4})_(\d{2,3})_(\d{1,4})')
}
f = R.TFile.Open('pairingCriteria.root')
HISTS = {}
for hkey in [tkey.GetName() for tkey in f.GetListOfKeys()]:
    if 'HTo2X' in hkey:
        if '4Mu' in hkey:
            # hkey has the form KEY_HTo2XTo4Mu_mH_mX_cTau
            matches = Patterns['HTo2XTo4Mu'].match(hkey)
            fs = '4Mu'
        elif '2Mu2J' in hkey:
            # hkey has the form KEY_HTo2XTo2Mu2J_mH_mX_cTau
            matches = Patterns['HTo2XTo2Mu2J'].match(hkey)
            fs = '2Mu2J'
        key = matches.group(1)
        sp = tuple(map(int, matches.group(2, 3, 4)))
        if (fs, sp) not in HISTS:
            HISTS[(fs, sp)] = {}
        HISTS[(fs, sp)][key] = f.Get(hkey)
        HISTS[(fs, sp)][key].SetDirectory(0)


for sp in SIGNALPOINTS:
    RT.addFlows(HISTS[('2Mu2J', sp)]['goodChi2'])
    RT.addFlows(HISTS[('2Mu2J', sp)]['badChi2' ])
    pGood = Plotter.Plot(HISTS[('2Mu2J', sp)]['goodChi2'], 'good', 'l', 'hist')
    pBad  = Plotter.Plot(HISTS[('2Mu2J', sp)]['badChi2' ], 'bad' , 'l', 'hist')

    canvas = Plotter.Canvas(lumi='{} ({} GeV, {} GeV, {} mm)'.format('2Mu2J', *sp))
    canvas.addMainPlot(pGood)
    canvas.addMainPlot(pBad )

    canvas.makeLegend(pos='tl')

    pGood.SetLineColor(R.kBlue)
    pBad .SetLineColor(R.kRed )

    canvas.firstPlot.setTitles(X='vtx #chi^{2}/dof')

    paveGood = canvas.makeStatsBox(pGood, color=R.kBlue)
    paveBad  = canvas.makeStatsBox(pBad , color=R.kRed )
    Plotter.MOVE_OBJECT(paveBad, Y=-.22, NDC=False)
    canvas.cleanup('pdfs/chi2_2Mu2J_{}.pdf'.format(SPStr(sp)))
