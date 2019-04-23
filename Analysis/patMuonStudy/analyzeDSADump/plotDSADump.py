import sys
import numpy as np
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT

h = {
    'd0Sig-S':R.TH1F('h1', ';d_{0}/#sigma_{d_{0}};Counts'          , 20, np.logspace(-3., 5., 21)   ),
    'd0Sig-B':R.TH1F('h2', ';d_{0}/#sigma_{d_{0}};Counts'          , 20, np.logspace(-3., 5., 21)   ),
    'dPhi-S' :R.TH1F('h3', ';#Delta#phi(original, refitted);Counts', 40, -R.TMath.Pi(), R.TMath.Pi()),
    'dPhi-B' :R.TH1F('h4', ';#Delta#phi(original, refitted);Counts', 40, -R.TMath.Pi(), R.TMath.Pi()),
}

def deltaPhi(phi1, phi2):
    v1 = R.TVector3()
    v2 = R.TVector3()
    v1.SetPtEtaPhi(1., 1., phi1)
    v2.SetPtEtaPhi(1., 1., phi2)
    return v1.DeltaPhi(v2)

l = [
    1094462867,
    1283051327,
    1790870957,
    224954587,
    2660937567,
    706256787,
    819173247,
    871330817,
    1840232227,
    214390057,
    229870167,
    246186967,
]

f = open(sys.argv[1])

c = 0
for line in f:
    cols = line.strip('\n').split()

    event = int(cols[3])

    LxySig, chi2, cosAlpha, d0Sig1, d0Sig2, deltaR1, deltaR2 = map(float, cols[10:11]+cols[12:14]+cols[15:19])

    d0Sig = {'1':d0Sig1, '2':d0Sig2}
    fpte, phi, rphi = {}, {}, {}
    fpte['1'], fpte['2'], phi['1'], phi['2'], rphi['1'], rphi['2'] = map(float, cols[20:])

    # for Bob
    #if LxySig > 5. and d0Sig1 > 3. and d0Sig2 > 3. and cosAlpha > -.8 and chi2 < 20.:
    #    print line.strip('\n')

    # for Slava
    #if LxySig > 5 and chi2 < 20 and cosAlpha < -0.9:
    #    print line.strip('\n')

    # cuts
    #if LxySig > 5 and chi2 < 20 and cosAlpha > -0.8 and d0Sig1 > 3. and d0Sig2 > 3:
    #    print line.strip('\n')

    #if cosAlpha > -0.9:
    #    print line.strip('\n')

    if fpte['1'] < 0.01 or fpte['2'] < 0.01 or fpte['1'] > 1. or fpte['2'] > 1.:
        c += 1

        if event in l:
            print event

    for i in ('1', '2'):
        if fpte[i] < 0.01:
            h['d0Sig-S'].Fill(d0Sig[i])
            h['dPhi-S'] .Fill(deltaPhi(phi[i], rphi[i]))
        else:
            h['d0Sig-B'].Fill(d0Sig[i])
            h['dPhi-B'] .Fill(deltaPhi(phi[i], rphi[i]))


print c

c = Plotter.Canvas(lumi='DSA muons in DSA-DSA dimuons in Data')
p = {
    'small':Plotter.Plot(h['d0Sig-S'], 'refitted #sigma_{p_{T}}/p_{T} < 1%', 'l', 'hist'),
    'big'  :Plotter.Plot(h['d0Sig-B'], 'refitted #sigma_{p_{T}}/p_{T} > 1%', 'l', 'hist'),
}
c.addMainPlot(p['small'])
c.addMainPlot(p['big']  )
c.mainPad.SetLogx()
p['small'].setColor(R.kRed, which='L')
p['big'].setColor(R.kBlue, which='L')
c.setMaximum()
c.makeLegend(lWidth=.3, pos='tr')
c.legend.resizeHeight()
p1 = c.makeStatsBox(p['small'], color=R.kRed)
p2 = c.makeStatsBox(p['big'], color=R.kBlue)
Plotter.MOVE_OBJECT(p1, Y=-.1)
Plotter.MOVE_OBJECT(p2, Y=-.3)
p2.SetX1(p1.GetX1())
c.firstPlot.scaleTitleOffsets(1.2, axes='X')
c.cleanup('d0Sig.pdf')

c = Plotter.Canvas(lumi='DSA muons in DSA-DSA dimuons in Data')
p = {
    'small':Plotter.Plot(h['dPhi-S'], 'refitted #sigma_{p_{T}}/p_{T} < 1%', 'l', 'hist'),
    'big'  :Plotter.Plot(h['dPhi-B'], 'refitted #sigma_{p_{T}}/p_{T} > 1%', 'l', 'hist'),
}
c.addMainPlot(p['small'])
c.addMainPlot(p['big']  )
p['small'].setColor(R.kRed, which='L')
p['big'].setColor(R.kBlue, which='L')
c.setMaximum()
c.makeLegend(lWidth=.3, pos='tr')
c.legend.resizeHeight()
p1 = c.makeStatsBox(p['small'], color=R.kRed)
p2 = c.makeStatsBox(p['big'], color=R.kBlue)
Plotter.MOVE_OBJECT(p1, Y=-.1)
Plotter.MOVE_OBJECT(p2, Y=-.3)
p2.SetX1(p1.GetX1())
c.firstPlot.scaleTitleOffsets(1.2, axes='X')
c.cleanup('dPhi.pdf')
