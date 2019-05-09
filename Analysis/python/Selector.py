import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.AnalysisTools as AnalysisTools

def SelectObjects(E, CUTS, Dimuons3, DSAmuons, PATmuons, bumpFPTE=False):

    # failed return list
    failedReturnList = None, None, None

    # decide what set of cuts to apply based on CUTS cut string
    PROMPT    = '_Prompt'   in CUTS
    NOPROMPT  = '_NoPrompt' in CUTS
    COMBINED  = '_Combined' in CUTS
    NSTATIONS = '_NS'       in CUTS
    NMUONHITS = '_NH'       in CUTS
    FPTERR    = '_FPTE'     in CUTS
    HLT       = '_HLT'      in CUTS
    REP       = '_REP'      in CUTS
    PT        = '_PT'       in CUTS
    PC        = '_PC'       in CUTS
    LXYERR    = '_LXYE'     in CUTS
    MASS      = '_MASS'     in CUTS
    CHI2      = '_CHI2'     in CUTS
    VTX       = '_VTX'      in CUTS
    COSA      = '_COSA'     in CUTS
    NPP       = '_NPP'      in CUTS
    DCA       = '_DCA'      in CUTS
    LXYSIG    = '_LXYSIG'   in CUTS

    # not (yet) used (or deprecated)
    D0SIG     = '_D0SIG'    in CUTS
    ISMEDIUM  = '_MED'      in CUTS
    NTRKLAYS  = '_NTL'      in CUTS

    # always apply PAT quality cuts when doing replacement
    # PQ1 = '_PQ1' in CUTS
    PQ1 = True

    # determine muon cut list based on string values
    def boolsToMuonCutList(NSTATIONS, NMUONHITS, FPTERR):
        cutList = []
        if NSTATIONS:
            cutList.append('q_nStations')
        if NMUONHITS:
            cutList.append('q_nMuonHits')
        if FPTERR:
            cutList.append('q_FPTE')
        return cutList

    # determine PAT muon quality cuts based on string values
    def boolsToPATMuonCutList(ISMEDIUM, NTRKLAYS):
        cutList = []
        if ISMEDIUM:
            cutList.append('p_isMedium')
        if NTRKLAYS:
            cutList.append('p_nTrkLays')
        return cutList

    # determine dimuon cut list based on string values
    def boolsToDimuonCutList(LXYERR, MASS, CHI2, COSA, DCA, LXYSIG):
        cutList = []
        if LXYERR:
            cutList.append('d_LxyErr')
        if MASS:
            cutList.append('d_mass')
        if CHI2:
            cutList.append('d_vtxChi2')
        if COSA:
            cutList.append('d_cosAlpha')
            cutList.append('d_cosAlphaO')
        #if D0SIG:
        #    cutList.append('d_d0Sig')
        if DCA:
            cutList.append('d_DCA')
        if LXYSIG:
            cutList.append('d_LxySig')
        return cutList

    # primary vertex
    if VTX:
        Filters = E.getPrimitives('FILTER')
        if not Selections.CUTS['goodVtx'].apply(Filters): return failedReturnList

    if NPP:
        nPPm, nPPp = AnalysisTools.numberOfParallelPairs(DSAmuons)
        if not Selections.CUTS['nPP'].apply(nPPm+nPPp): return failedReturnList

    # for PROMPT and NOPROMPT event selections
    if PROMPT or NOPROMPT:
        highLxySigExists = False
        for dimuon in Dimuons3:
            if dimuon.LxySig() > 3.:
                highLxySigExists = True
                break

        # return if there are LxySig > 3
        if PROMPT:
            if highLxySigExists:
                return failedReturnList
        # return if there are NO LxySig > 3 -- that's category 1
        elif NOPROMPT:
            if not highLxySigExists:
                return failedReturnList

    # initialize selected objects
    selectedDimuons = Dimuons3
    selectedMuons = {'DSA':DSAmuons, 'PAT':PATmuons}

    # DSA muon quality cuts
    if NSTATIONS or NMUONHITS or FPTERR:
        # compute all the baseline selection booleans
        DSASelections = {muon.idx:Selections.MuonSelection(muon, cutList='DSAQualityCutList') for muon in DSAmuons}

        # figure out which cuts we actually care about

        # testing bumpFPTE
        # if bumpFPTE, then move the FPTE DSA cut to after the replacement
        if not bumpFPTE:
            cutList = boolsToMuonCutList(NSTATIONS, NMUONHITS, FPTERR)
        else:
            cutList = boolsToMuonCutList(NSTATIONS, NMUONHITS, False)

        # cutList is some nonzero list, meaning keep only the muons that pass the cut keys in cutList
        if len(cutList) > 0:
            selectedMuons['DSA'] = [mu for mu in DSAmuons if DSASelections[mu.idx].allOf(*cutList)]
            selectedOIndices     = [mu.idx for mu in selectedMuons['DSA']]
            selectedDimuons      = [dim for dim in Dimuons3 if set(dim.ID).issubset(selectedOIndices) or dim.composition != 'DSA']

    # apply HLT RECO matching
    # for HLT RECO matching only, apply a pT cut and eta cut; see matchedTrigger
    # a pT cut will be applied later
    if HLT:
        HLTPaths, HLTMuons, L1TMuons = E.getPrimitives('TRIGGER')
        HLTMuonMatches = AnalysisTools.matchedTrigger(HLTMuons, selectedMuons['DSA'])
        if not any([HLTMuonMatches[ij]['matchFound'] for ij in HLTMuonMatches]): return failedReturnList

    # PAT muon replacement
    if REP:
        if PQ1:
            # compute all the PAT quality selection booleans
            # Note: the PATQualityCutList computes isGlobal, isMedium, and nTrkLays
            # A study determined that isGlobal + nTrkLays is the best combination at this stage, hence the explicit cutList
            # for standard quality cuts ONLY for disambiguating when doing the replacement
            # After replacement, we test isMedium + nTrkLays
            PATSelections = {muon.idx:Selections.MuonSelection(muon, cutList='PATQualityCutList') for muon in PATmuons}
            cutList = ['p_isGlobal', 'p_nTrkLays']
        else:
            PATSelections = None
            cutList = []
        selectedMuons['DSA'], selectedMuons['PAT'], selectedDimuons = AnalysisTools.replaceDSAMuons(selectedMuons['DSA'], selectedMuons['PAT'], selectedDimuons, PATSelections, cutList)
    else:
        selectedMuons['PAT'] = []
        selectedDimuons = [dim for dim in selectedDimuons if dim.composition == 'DSA']

    # given a selectedIndices dictionary of DSA and PAT indices and a dimuon,
    # determine if this dimuon is a selected dimuon
    def dimuonFilter(dim, selectedIndices):
        if dim.composition != 'HYBRID':
            tag1, tag2 = dim.composition, dim.composition
        else:
            tag1, tag2 = 'DSA', 'PAT'
        return dim.idx1 in selectedIndices[tag1] and dim.idx2 in selectedIndices[tag2]

    # apply post-replacement DSA cuts and filter down the selectedMuons and selectedDimuons
    # this only needs to be done right now if bumpFPTE is true
    # at the moment, DSASelections is computed already above, correctly, but if doing N-2 later, fix it!
    if bumpFPTE and FPTERR:
        cutList = boolsToMuonCutList(False, False, True)
        selectedMuons['DSA'] = [mu for mu in selectedMuons['DSA'] if DSASelections[mu.idx].allOf(*cutList)]

        selectedIndices = {'DSA':set(), 'PAT':set()}
        for tag in selectedMuons:
            selectedIndices[tag] = set([mu.idx for mu in selectedMuons[tag]])

        selectedDimuons = [dim for dim in selectedDimuons if dimuonFilter(dim, selectedIndices)]

    # apply post-replacement PAT quality cuts and filter down the selectedMuons and selectedDimuons
    # since this is PAT only, this only needs to be done if REP is true
    # also, we are currently not considering ISGLOBAL among the list of post-replacement PAT quality cuts
    # but it should be present approximately where ISMEDIUM is, if desired in the future
    if REP and (ISMEDIUM or NTRKLAYS):
        # compute all the PAT quality selection booleans
        PATSelections = {muon.idx:Selections.MuonSelection(muon, cutList='PATQualityCutList') for muon in selectedMuons['PAT']}

        # figure out which cuts we actually care about
        cutList = boolsToPATMuonCutList(ISMEDIUM, NTRKLAYS)

        # cutList is some nonzero list, meaning keep only the muons that pass the cut keys in cutList
        if len(cutList) > 0:
            selectedMuons['PAT'] = [mu for mu in selectedMuons['PAT'] if PATSelections[mu.idx].allOf(*cutList)]
            selectedIndices = {'DSA':set(), 'PAT':set()}
            for tag in selectedMuons:
                selectedIndices[tag] = set([mu.idx for mu in selectedMuons[tag]])

            selectedDimuons = [dim for dim in selectedDimuons if dimuonFilter(dim, selectedIndices)]

    # pT cut
    # there is only one cut of this type right now, but if additional cuts are applied later,
    # do a CutList as above and add it to Selections
    # for now, just apply the pT cut directly
    if PT:
        selectedIndices = {'DSA':set(), 'PAT':set()}
        for tag in selectedMuons:
            selectedMuons  [tag] = [mu for mu in selectedMuons[tag] if Selections.CUTS['m_pT'].apply(mu)]
            selectedIndices[tag] = set([mu.idx for mu in selectedMuons[tag]])

        selectedDimuons = [dim for dim in selectedDimuons if dimuonFilter(dim, selectedIndices)]

    # apply pairing criteria and transform selectedDimuons
    # pairing criteria was developed with DSA muons and DSA-DSA dimuons in mind
    # after replacement: run pairing criteria twice on the 3 semi-disjoint sets of dimuons
    # sort the resulting lists by vertex chi^2 and discard all but the lowest two
    if PC:
        # this was previously "option 3" for dealing with hybrids, now default and the only option
        # do PC on DSA, PAT, and hybrid, sort by vtx chi^2, and take the lowest 2
        objects = {'DSA':{}, 'PAT':{}, 'HYBRID':{}}
        for tag in objects:
            objects[tag]['inputMuons'] = selectedMuons[tag] if tag != 'HYBRID' else selectedMuons['DSA'] + selectedMuons['PAT']
            objects[tag]['inputDims' ] = [dim for dim in selectedDimuons if dim.composition == tag]
            objects[tag]['outputDims'] = AnalysisTools.applyPairingCriteria(objects[tag]['inputMuons'], objects[tag]['inputDims' ])

        candidateDimuons = objects['DSA']['outputDims'] + objects['PAT']['outputDims'] + objects['HYBRID']['outputDims']
        candidateDimuons.sort(key = lambda dim: dim.normChi2)

        # error: now that we have hybrids, we can't just take the two lowest chi2
        # we need the two lowest chi2, *non-overlapping*
        # selectedDimuons = candidateDimuons[:2]
        selectedIndices = {'DSA':set(), 'PAT':set()}
        selectedDimuons = []
        for dim in candidateDimuons:
            if len(selectedDimuons) == 2:
                break
            if dim.composition != 'HYBRID':
                tag1, tag2 = dim.composition, dim.composition
            else:
                tag1, tag2 = 'DSA', 'PAT'
            if dim.idx1 in selectedIndices[tag1] or dim.idx2 in selectedIndices[tag2]: continue
            selectedIndices[tag1].add(dim.idx1)
            selectedIndices[tag2].add(dim.idx2)
            selectedDimuons.append(dim)

    if True:
        # compute all the baseline selection booleans
        DimuonSelections = {(dim.ID, dim.composition):Selections.DimuonSelection(dim, cutList='DimuonCutList') for dim in selectedDimuons}

        # figure out which cuts we actually care about
        #cutList = boolsToDimuonCutList(LXYERR, MASS, CHI2, D0SIG)

        # the d0Sig cut should be applied to original muons, so comment out the "dimuon" version of the d0Sig cut
        cutList = boolsToDimuonCutList(LXYERR, MASS, CHI2, COSA, DCA, LXYSIG)

        # cutList is some nonzero list, meaning keep only the muons that pass the cut keys in cutList
        if len(cutList) > 0:
            selectedDimuons = [dim for dim in selectedDimuons if DimuonSelections[(dim.ID, dim.composition)].allOf(*cutList)]

    # d0Sig cut
    # this cut is in the MuonCutList, but it is applied later so I'm just going to recompute it
    # and apply it directly
    # note that this is a MultiCut, so it will behave differently depending on the muon type
    if D0SIG:
        selectedIndices = {'DSA':set(), 'PAT':set()}
        for tag in selectedMuons:
            selectedMuons  [tag] = [mu for mu in selectedMuons[tag] if Selections.CUTS['m_d0Sig'].apply(mu)]
            selectedIndices[tag] = set([mu.idx for mu in selectedMuons[tag]])

        selectedDimuons = [dim for dim in selectedDimuons if dimuonFilter(dim, selectedIndices)]


    # for the MC/Data events, skip events with no dimuons, but not for "no selection"
    if NSTATIONS:
        if len(selectedDimuons) == 0: return failedReturnList

    # also filter selectedMuons to only be of those indices that are in the final dimuons
    if True:
        selectedIndices = {'DSA':set(), 'PAT':set()}
        for dim in selectedDimuons:
            if dim.composition != 'HYBRID':
                tag1, tag2 = dim.composition, dim.composition
            else:
                tag1, tag2 = 'DSA', 'PAT'
            selectedIndices[tag1].add(dim.idx1)
            selectedIndices[tag2].add(dim.idx2)
        for tag in selectedMuons:
            selectedMuons[tag] = [mu for mu in selectedMuons[tag] if mu.idx in selectedIndices[tag]]

    # final return
    return selectedDimuons, selectedMuons['DSA'], selectedMuons['PAT']
