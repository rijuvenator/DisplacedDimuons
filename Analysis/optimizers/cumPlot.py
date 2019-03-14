import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr, SPLumiStr
import DisplacedDimuons.Analysis.AnalysisTools as AT
import DisplacedDimuons.Analysis.HistogramGetter as HG

TAG = 'Dimuon'
#TAG = 'RecoMuon'

FILES = {
    'Signal_Prompt'   : R.TFile.Open('../analyzers/roots/Main/'+TAG+'Plots_Trig_Prompt_NS_NH_FPTE_PT_HLT_PC_LXYE_M_SignalOnly.root'),
    'Signal_NoPrompt' : R.TFile.Open('../analyzers/roots/Main/'+TAG+'Plots_Trig_NoPrompt_NS_NH_FPTE_PT_HLT_PC_LXYE_M_SignalOnly.root'),
    'MC_Prompt'       : R.TFile.Open('../analyzers/roots/Main/'+TAG+'Plots_Prompt_NS_NH_FPTE_PT_HLT_PC_LXYE_M_NoSignal.root'),
    'MC_NoPrompt'     : R.TFile.Open('../analyzers/roots/Main/'+TAG+'Plots_NoPrompt_NS_NH_FPTE_PT_HLT_PC_LXYE_M_MCOnly.root'),
}

BGORDER = ('WJets', 'WW', 'WZ', 'ZZ', 'tW', 'tbarW', 'ttbar', 'QCD20toInf-ME', 'DY10to50', 'DY50toInf')
SPLIST = SIGNALPOINTS

#SPSPLITLIST = ((125, 20, 13), (200, 20, 7), (400, 20, 4), (1000, 20, 2))
#SPSPLITLIST = ((125, 50, 5000), (200, 50, 2000), (400, 150, 4000), (1000, 350, 3500))
#SPSPLITLIST = ((1000, 20, 20), (400, 150, 400))
SPSPLITLIST = SIGNALPOINTS
#SPSPLITLIST = ((125, 20, 13),)

PC = HG.PLOTCONFIG

if TAG == 'Dimuon':
    CONFIG = (
        ('deltaR'  , False, False),
        ('vtxChi2' , False, False),
        ('vtxChi2' , False, True ),
        ('cosAlpha', True , False),
        ('LxySig'  , True , True ),
        ('LxySig'  , True , False),
        ('deltaPhi', False, False),
    )
elif TAG == 'RecoMuon':
    CONFIG = (
        ('DSA_d0Sig'   , True , True ),
        ('REF_d0Sig'   , True , True ),
        ('DSA_d0Sig'   , True , False),
        ('REF_d0Sig'   , True , False),
        ('DSA_pTSig'   , False, False),
        ('REF_pTSig'   , False, False),
        ('DSA_normChi2', False, False),
        ('REF_normChi2', False, False),
    )
else:
    raise Exception('Not a good tag')

OPTIONS = (
    (True, True, False),
    (True, False, True),
    (False, True, True)
)

COLORS = {
    (1000, 350,   35) : (R.kRed  +3, 1 ),
	(1000, 350,  350) : (R.kBlue +3, 1 ),
	(1000, 350, 3500) : (R.kGreen+3, 1 ),
	(1000, 150,   10) : (R.kRed  +2, 1 ),
	(1000, 150,  100) : (R.kBlue +2, 1 ),
	(1000, 150, 1000) : (R.kGreen+2, 1 ),
	(1000,  50,    4) : (R.kRed  +1, 1 ),
	(1000,  50,   40) : (R.kBlue +1, 1 ),
	(1000,  50,  400) : (R.kGreen+1, 1 ),
	(1000,  20,    2) : (R.kRed  +0, 1 ),
	(1000,  20,   20) : (R.kBlue +0, 1 ),
	(1000,  20,  200) : (R.kGreen+0, 1 ),
	( 400, 150,   40) : (R.kRed  +2, 2 ),
	( 400, 150,  400) : (R.kBlue +2, 2 ),
	( 400, 150, 4000) : (R.kGreen+2, 2 ),
	( 400,  50,    8) : (R.kRed  +1, 2 ),
	( 400,  50,   80) : (R.kBlue +1, 2 ),
	( 400,  50,  800) : (R.kGreen+1, 2 ),
	( 400,  20,    4) : (R.kRed  +0, 2 ),
	( 400,  20,   40) : (R.kBlue +0, 2 ),
	( 400,  20,  400) : (R.kGreen+0, 2 ),
	( 200,  50,   20) : (R.kRed  +1, 9 ),
	( 200,  50,  200) : (R.kBlue +1, 9 ),
	( 200,  50, 2000) : (R.kGreen+1, 9 ),
	( 200,  20,    7) : (R.kRed  +0, 9 ),
	( 200,  20,   70) : (R.kBlue +0, 9 ),
	( 200,  20,  700) : (R.kGreen+0, 9 ),
	( 125,  50,   50) : (R.kRed  +1, 10),
	( 125,  50,  500) : (R.kBlue +1, 10),
	( 125,  50, 5000) : (R.kGreen+1, 10),
	( 125,  20,   13) : (R.kRed  +0, 10),
	( 125,  20,  130) : (R.kBlue +0, 10),
	( 125,  20, 1300) : (R.kGreen+0, 10),
}

for SPLIT, DO2MU, DO4MU in OPTIONS:
    for quantity, isGreater, RESIZE in CONFIG:
        LOGY = quantity in ('DSA_d0Sig', 'REF_d0Sig', 'LxySig')
        if RESIZE:
            LOGY = False
        if TAG == 'Dimuon':
            qkeyname = 'Dim_{}'.format(quantity)
        elif TAG == 'RecoMuon':
            qkeyname = quantity

        h = {}

        h['MC'] = HG.getHistogram(FILES['MC_Prompt'], BGORDER[0], qkeyname)

        for key in BGORDER:
            for fkey in ('MC_Prompt', 'MC_NoPrompt'):
                if key == BGORDER[0] and fkey == 'MC_Prompt':
                    h['MC'].Scale(PC[key]['WEIGHT'])
                else:
                    hTemp = HG.getHistogram(FILES[fkey], key, qkeyname)
                    hTemp.Scale(PC[key]['WEIGHT'])
                    h['MC'].Add(hTemp)


        if not SPLIT:
            h['2Mu'] = HG.getHistogram(FILES['Signal_Prompt'], ('2Mu2J', SPLIST[0]), qkeyname)
            h['4Mu'] = HG.getHistogram(FILES['Signal_Prompt'], ('4Mu'  , SPLIST[0]), qkeyname)

            for SP in SPLIST:
                for fkey in ('Signal_Prompt', 'Signal_NoPrompt'):
                    if not (SP == SPLIST[0] and fkey == 'Signal_Prompt'):
                        h['2Mu'].Add(HG.getHistogram(FILES[fkey], ('2Mu2J', SP), qkeyname))
                        h['4Mu'].Add(HG.getHistogram(FILES[fkey], ('4Mu'  , SP), qkeyname))

        else:
            for SP in SPSPLITLIST:
                h['2Mu_'+SPStr(SP)] = HG.getHistogram(FILES['Signal_Prompt'], ('2Mu2J', SP), qkeyname)
                h['4Mu_'+SPStr(SP)] = HG.getHistogram(FILES['Signal_Prompt'], ('4Mu'  , SP), qkeyname)

            for SP in SPSPLITLIST:
                for fkey in ('Signal_NoPrompt',):
                    h['2Mu_'+SPStr(SP)].Add(HG.getHistogram(FILES[fkey], ('2Mu2J', SP), qkeyname))
                    h['4Mu_'+SPStr(SP)].Add(HG.getHistogram(FILES[fkey], ('4Mu'  , SP), qkeyname))

        cums = {key:h[key].GetCumulative(not isGreater) for key in h}
        for key in cums:
            cums[key].Scale(1./cums[key].GetBinContent(1 if isGreater else cums[key].GetNbinsX()))

        p = {}
        for key in cums:
            p[key] = Plotter.Plot(cums[key], key, 'l', 'hist')

        canvas = Plotter.Canvas(lumi='', logy=LOGY)
        if not SPLIT:
            if DO2MU:
                canvas.addMainPlot(p['2Mu'])
                p['2Mu'].setColor(R.kRed, which='L')
            if DO4MU:
                canvas.addMainPlot(p['4Mu'])
                p['4Mu'].setColor(R.kBlue, which='L')
        else:
            if DO2MU:
                for i,SP in enumerate(SPSPLITLIST):
                    canvas.addMainPlot(p['2Mu_'+SPStr(SP)])
                    #p['2Mu_'+SPStr(SP)].setColor(R.kRed+i, which='L')
                    #p['2Mu_'+SPStr(SP)].setColor(i%10 if i%10!=0 else 46, which='L')
                    p['2Mu_'+SPStr(SP)].setColor(COLORS[SP][0], which='L')
                    p['2Mu_'+SPStr(SP)].SetLineStyle(COLORS[SP][1])
            if DO4MU:
                for i,SP in enumerate(SPSPLITLIST):
                    canvas.addMainPlot(p['4Mu_'+SPStr(SP)])
                    #p['4Mu_'+SPStr(SP)].setColor(R.kBlue+i, which='L')
                    #p['4Mu_'+SPStr(SP)].setColor(i%10 if i%10!=0 else 46, which='L')
                    p['4Mu_'+SPStr(SP)].setColor(COLORS[SP][0], which='L')
                    p['4Mu_'+SPStr(SP)].SetLineStyle(COLORS[SP][1])
        canvas.addMainPlot(p['MC'])
        p['MC'].legType = 'f'
        p['MC'].setColor(0, which='L', alpha=0)
        p['MC'].setColor(R.kOrange, which='F', alpha=.4)

        if RESIZE:
            if 'vtxChi2' in quantity:
                canvas.firstPlot.GetXaxis().SetRangeUser(0., 5.)
            else:
                canvas.firstPlot.GetXaxis().SetRangeUser(0., 15.)

        canvas.firstPlot.setTitles(Y='Efficiency if cut were {} than X value'.format('less' if not isGreater else 'greater'))
        if not SPLIT:
            canvas.makeLegend(lWidth=.2, pos='br')
            canvas.legend.resizeHeight()
        else:
            ystart = 0.3 if not isGreater else 0.85
            xstart = .6
            if quantity == 'cosAlpha':
                xstart = .2
                ystart = 0.3
            canvas.drawText(text='#color[3]{long}, #color[4]{medium}, #color[2]{short} lifetimes', pos=(xstart, ystart    ), align='cl', fontscale=.7)
            canvas.drawText(text='darker color = larger X mass'                                  , pos=(xstart, ystart-.04), align='cl', fontscale=.7)
            canvas.drawText(text='solid #rightarrow dashed = smaller H mass'                     , pos=(xstart, ystart-.08), align='cl', fontscale=.7)
            canvas.drawText(text='#color[797]{MC}'                                               , pos=(xstart, ystart-.12), align='cl', fontscale=.7)

        if DO4MU and DO2MU:
            fs = 'Both'
        elif DO4MU:
            fs = '4Mu'
        else:
            fs = '2Mu2J'
        canvas.cleanup('cumPlot_{}_{}{}{}.pdf'.format(fs, quantity, '-Zoomed' if RESIZE else '', '' if SPLIT else '_Global'))
