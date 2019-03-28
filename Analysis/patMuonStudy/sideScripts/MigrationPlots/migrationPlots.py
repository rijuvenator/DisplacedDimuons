import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT

CKEYS = ('X', 'G', 'GN', 'M', 'MN')

data = {}

f = open('text/migrationData.txt')
for line in f:
    cols = line.split()

    # if the line begins with :, it's a new event
    # identify it with name, run, lumi, event
    # the first column is ::: so ignore it
    if line[0] == ':':
        ekey = (cols[1], cols[2], cols[3], cols[4])
        if False:
        #if 'DY' not in ekey[0]:
            ekey = None
            continue
        data[ekey] = {ckey:[] for ckey in CKEYS}
        continue

    if ekey is None: continue

    # otherwise, we're saving lines
    # ekey is already saved from before
    ckey = cols[0]

    # this might be an empty line; skip it if so
    if cols[2] == '-': continue

    # okay, so there's info here. copy it into a dict
    # and add it to data

    cdata = {'sig':(cols[2], cols[3], cols[4]), 'LxySig':float(cols[6]), 'Lxy':float(cols[7]), 'vtxChi2':float(cols[8]), 'mind0Sig':float(cols[9])}
    data[ekey][ckey].append(cdata)

# now the data is filled

# some aesthetic things

binLabels = {
    0:'None',
    1:'DSA',
    2:'HYB',
    3:'PAT',
    4:'DSA-DSA',
    5:'DSA-HYB',
    6:'DSA-PAT',
    7:'HYB-HYB',
    8:'HYB-PAT',
    9:'PAT-PAT',
    (0, 3):'None #rightarrow PAT',
}

prettyCKeys = {'X':'baseline', 'G':'global', 'GN':'global + N(trk lays)', 'M':'medium', 'MN':'medium + N(trk lays)'}
prettyQKeys = {'Lxy':'L_{xy}', 'LxySig':'L_{xy}/#sigma_{L_{xy}}', 'vtxChi2':'vtx #chi^{2}'}

# info should be a data[ekey][ckey]

typeSig = {'DSA':0, 'HYB':1, 'PAT':2}
def signature(info):
    nDims = len(info)

    # 0 dims : = state 0
    if nDims == 0: return 0

    # 1 dim : DSA PAT HYB = state 1, 2, 3
    if nDims == 1:
        cdata = info[0]
        rtype = cdata['sig'][0]
        sig = 1 + typeSig[rtype]
        return sig

    # 2 dims : DSA-DSA DSA-HYB DSA-PAT HYB-HYB HYB-PAT PAT-PAT = state 4, 5, 6, 7, 8, 9
    if nDims == 2:
        rtypes = [info[0]['sig'][0], info[1]['sig'][1]]
        rtypeCounts = {rtype:rtype.count(rtype) for rtype in typeSig}
        if rtypeCounts['DSA'] == 0:
            sig = 9 - rtypeCounts['HYB']
        else:
            sig = 4 + rtypeCounts['HYB']*1 + rtypeCounts['PAT']*2
        return sig

# whether or not the actual dimuons changed
def changed(bsInfo, info):
    return set([cdata['sig'] for cdata in bsInfo]) != set([cdata['sig'] for cdata in info])

# whether or not the changed dimuons are "better"
def better(key, bsInfo, info):
    oldVals = [cdata[key] for cdata in bsInfo]
    newVals = [cdata[key] for cdata in   info]
    isBetter = True
    for oval in oldVals:
        for nval in newVals:
            if nval > oval:
                isBetter = False
                break
    return isBetter

# whether or not the new dimuon is "within limits"
def withinLimits(key, info):
    limits = {'LxySig':5., 'Lxy':1., 'vtxChi2':5.}
    return info[0][key] <= limits[key]

# state migration matrix, one per G GN M MN
migrationHists = {}
for ckey in prettyCKeys:
    if ckey == 'X': continue
    migrationHists[ckey] = R.TH2F('h'+ckey, ';baseline;'+prettyCKeys[ckey]+';Counts', 10, 0., 10., 10, 0., 10.)

# changed hists and better hists for each improvement type, binned by cut mode
#diagonalKeys = (2, 3, 7, 9)
diagonalKeys = (2, 3, 7)
changedHists = {}
betterHists = {'LxySig':{}, 'Lxy':{}, 'vtxChi2':{}}
for diagonal in diagonalKeys:
    changedHists[diagonal] = R.TH1F('hc'+str(diagonal), ';Cut Mode;Fraction Changed', 4, 0., 4.)
    for key in betterHists:
        betterHists[key][diagonal] = R.TH1F('hb'+key+str(diagonal), ';Cut Mode;Fraction Improved', 4, 0., 4.)

# one extra special one for the 0 --> 3 (None --> PAT) case
changedHists[(0, 3)] = R.TH1F('hc03', ';Cut Mode;Counts', 4, 0., 4.)
for key in betterHists:
    betterHists[key][(0, 3)] = R.TH1F('hb'+key+'03', ';Cut Mode;Fraction Improved', 4, 0., 4.)

# Lxy significance histograms
LxySigHists = {}
for ckey in prettyCKeys:
    LxySigHists[ckey] = R.TH1F('hLxySig'+ckey, ';L_{xy}/#sigma_{L_{xy}};Counts', 100, 0., 100.)

# change bin labels
for ckey in migrationHists:
    for ax in ('X', 'Y'):
        axis = getattr(migrationHists[ckey], 'Get'+ax+'axis')()
        for sig, lab in binLabels.iteritems():
            if sig == (0, 3): continue
            axis.SetBinLabel(sig+1, lab)

for diagonal in changedHists:
    xaxis = changedHists[diagonal].GetXaxis()
    for i, ckey in enumerate(CKEYS[1:], 1):
        xaxis.SetBinLabel(i, ckey)
    for key in betterHists:
        xaxis = betterHists[key][diagonal].GetXaxis()
        for i, ckey in enumerate(CKEYS[1:], 1):
            xaxis.SetBinLabel(i, ckey)

# loop over the data
# CKEYS.index - 1 happens to be the right bin with the current ordering; be careful
# ckey == G idiom is for making sure something only happens once
for ekey in data:
    bsInfo = data[ekey]['X']
    for ckey in migrationHists:
        info = data[ekey][ckey]
        bsSig, infoSig = signature(bsInfo), signature(info)
        migrationHists[ckey].Fill(bsSig, infoSig)

        if bsSig == infoSig and bsSig in diagonalKeys:
            diagonal = bsSig
            if changed(bsInfo, info):
                changedHists[diagonal].Fill(CKEYS.index(ckey)-1)
                for key in betterHists:
                    if better(key, bsInfo, info):
                        betterHists[key][diagonal].Fill(CKEYS.index(ckey)-1)

        if bsSig == 0 and infoSig == 3:
            diagonal = (0, 3)
            changedHists[diagonal].Fill(CKEYS.index(ckey)-1)
            for key in betterHists:
                if withinLimits(key, info):
                    betterHists[key][diagonal].Fill(CKEYS.index(ckey)-1)

        if bsSig == 3 and ckey == 'G':
            LxySigHists['X'].Fill(bsInfo[0]['LxySig'])
        if bsSig == 3 and infoSig == 3:
            LxySigHists[ckey].Fill(info[0]['LxySig'])

### plots ###

# migration matrices and Lxy significances
# again, ckey == G idiom is for making sure something only happens once
for ckey in CKEYS[1:]:
    p = Plotter.Plot(migrationHists[ckey], '', '', 'text')
    c = Plotter.Canvas(cWidth=900)
    c.addMainPlot(p)
    c.scaleMargins(1.2, 'L')
    p.scaleTitleOffsets(1.5, axes='Y')
    c.cleanup('pdfs/MH_'+ckey+'.pdf')

    p = Plotter.Plot(LxySigHists['X'], 'baseline', 'l', 'hist')
    q = Plotter.Plot(LxySigHists[ckey], prettyCKeys[ckey], 'l', 'hist')
    if ckey == 'G':
        RT.addFlows(p)
    RT.addFlows(q)
    c = Plotter.Canvas(logy=True)
    c.addMainPlot(p)
    c.addMainPlot(q)
    p.SetLineColor(R.kRed)
    q.SetLineColor(R.kBlue)
    c.makeLegend(pos='tr', lWidth=.3)
    c.legend.resizeHeight()
    c.firstPlot.SetMaximum(5000.)
    c.cleanup('pdfs/MH_L_'+ckey+'.pdf')

# first, divide better hists by changed hists
# only then, you are free to divide changed hists by migration hists bin contents
# since bins are 1 indexed, but the states are 0 indexed, "diagonal + 1" is the right bin
# now that both changed hists and better hists are scaled down, multiply them together
# meanwhile, (0, 3) isn't scaled down for changed hists, so deal with the exceptions accordingly
for diagonal in changedHists:
    dstring = str(diagonal) if diagonal != (0, 3) else '03'
    for key in betterHists:
        for ibin in range(1, 5):
            try:
                betterHists[key][diagonal].SetBinContent(ibin, betterHists[key][diagonal].GetBinContent(ibin)/changedHists[diagonal].GetBinContent(ibin))
            except:
                pass
        p = Plotter.Plot(betterHists[key][diagonal], '', '', 'hist')
        c = Plotter.Canvas(lumi=prettyQKeys[key]+' ('+binLabels[diagonal]+')')
        c.addMainPlot(p)
        p.SetMinimum(0.)
        p.SetMaximum(1.)
        c.cleanup('pdfs/MH_B_'+dstring+'_'+key+'.pdf')

    if diagonal != (0, 3):
        for ibin in range(1, 5):
            try:
                changedHists[diagonal].SetBinContent(ibin, changedHists[diagonal].GetBinContent(ibin)/migrationHists[CKEYS[ibin]].GetBinContent(diagonal+1, diagonal+1))
            except:
                pass
    p = Plotter.Plot(changedHists[diagonal], '', '', 'hist')
    c = Plotter.Canvas(lumi='('+binLabels[diagonal]+')')
    c.addMainPlot(p)
    p.SetMinimum(0.)
    if diagonal != (0, 3):
        p.SetMaximum(1.)
    c.cleanup('pdfs/MH_C_'+dstring+'.pdf')

    for key in betterHists:
        h = betterHists[key][diagonal].Clone()
        for ibin in range(1, 5):
            h.SetBinContent(ibin, h.GetBinContent(ibin)*changedHists[diagonal].GetBinContent(ibin))
        p = Plotter.Plot(h, '', '', 'hist')
        c = Plotter.Canvas(lumi=prettyQKeys[key]+' ('+binLabels[diagonal]+')')
        c.addMainPlot(p)
        p.SetMinimum(0.)
        if diagonal != (0, 3):
            p.SetMaximum(1.)
        else:
            c.setMaximum(recompute=True)
        p.setTitles(Y='Fraction Improved Overall')
        c.cleanup('pdfs/MH_M_'+dstring+'_'+key+'.pdf')
