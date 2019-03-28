import ROOT as R
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Common.Utilities as Utilities

FILE = R.TFile.Open('roots/ZephyrPlots_Trig_Combined_NS_NH_FPTE_HLT_REP_PQ1_PT_PC_LXYE_MASS_CHI2_HTo2XTo2Mu2J.root')
HISTS, INDIV = HG.getAddedSignalHistograms(FILE, '2Mu2J', ('GEN-Lxy', 'GEN-Lxy-PAT', 'GEN-Lxy-HYB', 'GEN-Lxy-DSA'), getIndividuals=True)

for sp in INDIV['GEN-Lxy'].keys() + [None]:
    h = {}
    if sp is not None:
        SOURCEDICT = {key:INDIV[key][sp] for key in INDIV}
    else:
        SOURCEDICT = HISTS

    h['Tot'] = SOURCEDICT['GEN-Lxy'].Clone()
    for RTYPE in ('DSA', 'PAT', 'HYB'):
        h[RTYPE] = SOURCEDICT['GEN-Lxy-'+RTYPE].Clone()

    print '{:13s} ::: {:6.0f} ::: DSA {:6.0f} ( {:6.2%} ) ::: PAT {:6.0f} ( {:6.2%} ) ::: HYB {:6.0f} ( {:6.2%} )'.format(
            'Global - -' if sp is None else '{:4d} {:3d} {:4d}'.format(*sp),
            h['Tot'].Integral(0, h['Tot'].GetNbinsX()+1),
            h['DSA'].Integral(0, h['DSA'].GetNbinsX()+1), h['DSA'].Integral(0, h['DSA'].GetNbinsX()+1)/h['Tot'].Integral(0, h['Tot'].GetNbinsX()+1),
            h['PAT'].Integral(0, h['PAT'].GetNbinsX()+1), h['PAT'].Integral(0, h['PAT'].GetNbinsX()+1)/h['Tot'].Integral(0, h['Tot'].GetNbinsX()+1),
            h['HYB'].Integral(0, h['HYB'].GetNbinsX()+1), h['HYB'].Integral(0, h['HYB'].GetNbinsX()+1)/h['Tot'].Integral(0, h['Tot'].GetNbinsX()+1),
    )

    h['Tot'].Rebin(10)
    for RTYPE in ('DSA', 'PAT', 'HYB'):
        h[RTYPE].Rebin(10)

    #g = {}
    #p = {}
    #for RTYPE in ('DSA', 'PAT', 'HYB'):
    #    g[RTYPE] = R.TGraphAsymmErrors(h[RTYPE], h['Tot'], 'cp')
    #    p[RTYPE] = Plotter.Plot(g[RTYPE], RTYPE, 'lp', 'p')

    p = {}
    for RTYPE in ('DSA', 'PAT', 'HYB'):
        h[RTYPE].Divide(h['Tot'])
        p[RTYPE] = Plotter.Plot(h[RTYPE], RTYPE, 'lp', 'p')

    canvas = Plotter.Canvas(lumi=Utilities.SPLumiStr('2Mu2J', *sp) if sp is not None else '2Mu2J')
    for i, RTYPE in enumerate(('DSA', 'PAT', 'HYB'), start=2):
        canvas.addMainPlot(p[RTYPE])
        p[RTYPE].setColor(i, which='LM')

    canvas.makeLegend(pos='br', lWidth=.5)
    canvas.legend.resizeHeight()
    canvas.legend.moveLegend(Y=.2)
    canvas.legend.SetMargin(0.15)

    canvas.firstPlot.setTitles(Y='Fraction of matches', X='gen L_{xy} [cm]')
    canvas.firstPlot.SetMinimum(0.)
    canvas.firstPlot.SetMaximum(1.1)
    canvas.firstPlot.GetXaxis().SetRangeUser(0., 400.)

    canvas.cleanup('pdfs/RTypeEff_HTo2XTo2Mu2J_{}.pdf'.format(Utilities.SPStr(*sp) if sp is not None else 'Global'))
