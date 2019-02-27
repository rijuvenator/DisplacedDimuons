import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.AnalysisTools as AnalysisTools

def SelectObjects(E, CUTS, Dimuons, DSAmuons):

    # decide what set of cuts to apply based on CUTS cut string
    PROMPT    = '_Prompt'   in CUTS
    NOPROMPT  = '_NoPrompt' in CUTS
    COMBINED  = '_Combined' in CUTS
    NSTATIONS = '_NS'       in CUTS
    NMUONHITS = '_NH'       in CUTS
    FPTERR    = '_FPTE'     in CUTS
    PT        = '_PT'       in CUTS
    HLT       = '_HLT'      in CUTS
    PC        = '_PC'       in CUTS
    LXYERR    = '_LXYE'     in CUTS
    MASS      = '_M'        in CUTS

    # determine muon cut list based on string values
    def boolsToMuonCutList(NSTATIONS, NMUONHITS, FPTERR, PT):
        cutList = []
        if NSTATIONS:
            cutList.append('b_nStations')
        if NMUONHITS:
            cutList.append('b_nMuonHits')
        if FPTERR:
            cutList.append('b_FPTE')
        if PT:
            cutList.append('b_pT')
        return cutList

    # determine dimuon cut list based on string values
    def boolsToDimuonCutList(LXYERR, MASS):
        cutList = []
        if LXYERR:
            cutList.append('b_LxyErr')
        if MASS:
            cutList.append('b_mass')
        return cutList

    # for PROMPT and NOPROMPT event selections
    if PROMPT or NOPROMPT:
        highLxySigExists = False
        for dimuon in Dimuons:
            if dimuon.LxySig() > 3.:
                highLxySigExists = True
                break

        # return if there are LxySig > 3
        if PROMPT:
            if highLxySigExists:
                return None, None
        # return if there are NO LxySig > 3 -- that's category 1
        elif NOPROMPT:
            if not highLxySigExists:
                return None, None

    # muon quality cuts + pT
    if PROMPT or NOPROMPT or COMBINED:
        # compute all the baseline selection booleans
        DSASelections = [Selections.MuonSelection(muon, cutList='BaselineMuonCutList') for muon in DSAmuons]

        # figure out which cuts we actually care about
        cutList = boolsToMuonCutList(NSTATIONS, NMUONHITS, FPTERR, PT)

        # no selection
        if len(cutList) == 0:
            selectedDSAmuons = DSAmuons
            selectedDimuons  = Dimuons
        # cutList is some nonzero list, meaning keep only the muons that pass the cut keys in cutList
        else:
            selectedDSAmuons = [mu for i,mu in enumerate(DSAmuons) if DSASelections[i].allOf(*cutList)]
            selectedOIndices = [mu.idx for mu in selectedDSAmuons]
            selectedDimuons  = [dim for dim in Dimuons if dim.idx1 in selectedOIndices and dim.idx2 in selectedOIndices]

    # apply HLT RECO matching
    if HLT:
        HLTPaths, HLTMuons, L1TMuons = E.getPrimitives('TRIGGER')
        DSAMuonsForHLTMatch = [mu for mu in selectedDSAmuons if abs(mu.eta) < 2.]
        HLTMuonMatches = AnalysisTools.matchedTrigger(HLTMuons, DSAMuonsForHLTMatch)
        if not any([HLTMuonMatches[ij]['matchFound'] for ij in HLTMuonMatches]): return None, None

    # apply pairing criteria and transform selectedDimuons
    if PC:
        selectedDimuons = AnalysisTools.applyPairingCriteria(selectedDSAmuons, selectedDimuons)

    if PROMPT or NOPROMPT or COMBINED:
        # compute all the baseline selection booleans
        DimuonSelections = {dim.ID:Selections.DimuonSelection(dim, cutList='BaselineDimuonCutList') for dim in selectedDimuons}

        # figure out which cuts we actually care about
        cutList = boolsToDimuonCutList(LXYERR, MASS)

        # cutList is some nonzero list, meaning keep only the muons that pass the cut keys in cutList
        if len(cutList) > 0:
            selectedDimuons = [dim for dim in selectedDimuons if DimuonSelections[dim.ID].allOf(*cutList)]

    # for the MC/Data events, skip events with no dimuons, but not for "no selection"
    if (PROMPT or NOPROMPT or COMBINED) and NSTATIONS:
        if len(selectedDimuons) == 0: return None, None

    # also filter selectedDSAmuons to only be of those indices that are in the final dimuons
    if PROMPT or NOPROMPT or COMBINED:
        selectedOIndices = []
        for dim in selectedDimuons:
            selectedOIndices.append(dim.idx1)
            selectedOIndices.append(dim.idx2)
        selectedOIndices = list(set(selectedOIndices))
        selectedDSAmuons = [mu for mu in selectedDSAmuons if mu.idx in selectedOIndices]

    # final return
    return selectedDimuons, selectedDSAmuons


def SelectObjectsReordered(E, CUTS, Dimuons3, DSAmuons, PATmuons):

    # failed return list
    failedReturnList = None, None, None, None

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
    MASS      = '_M'        in CUTS

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

    # determine dimuon cut list based on string values
    def boolsToDimuonCutList(LXYERR, MASS):
        cutList = []
        if LXYERR:
            cutList.append('b_LxyErr')
        if MASS:
            cutList.append('b_mass')
        return cutList

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
        DSASelections = [Selections.MuonSelection(muon, cutList='DSAQualityCutList') for muon in DSAmuons]

        # figure out which cuts we actually care about
        cutList = boolsToMuonCutList(NSTATIONS, NMUONHITS, FPTERR)

        # no selection
        if len(cutList) == 0:
            selectedMuons['DSA'] = DSAmuons
            selectedDimuons      = Dimuons3
        # cutList is some nonzero list, meaning keep only the muons that pass the cut keys in cutList
        else:
            selectedMuons['DSA'] = [mu for i,mu in enumerate(DSAmuons) if DSASelections[i].allOf(*cutList)]
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
        selectedMuons['DSA'], selectedMuons['PAT'], selectedDimuons = AnalysisTools.replaceDSAMuons(selectedMuons['DSA'], PATmuons, selectedDimuons)
    else:
        selectedMuons['PAT'] = []
        selectedDimuons = [dim for dim in selectedDimuons if dim.composition == 'DSA']

    # pT cut
    # there is only one cut of this type right now, but if additional cuts are applied later,
    # do a CutList as above and add it to Selections
    # for now, just apply the pT cut directly
    if PT:
        selectedIndices = {'DSA':set(), 'PAT':set()}
        for tag in selectedMuons:
            selectedMuons  [tag] = [mu for mu in selectedMuons[tag] if Selections.CUTS['r_pT'].apply(mu)]
            selectedIndices[tag] = set([mu.idx for mu in selectedMuons[tag]])
        selectedDimuons = [dim for dim in selectedDimuons if set(dim.ID).issubset(selectedIndices['DSA']) or set(dim.ID).issubset(selectedIndices['PAT'])]

    # apply pairing criteria and transform selectedDimuons
    # pairing criteria was developed with DSA muons and DSA-DSA dimuons in mind
    # after replacement, without hybrids: run pairing criteria twice on the disjoint sets of dimuons
    # sort the resulting list by vertex chi^2 and discard all but the lowest two
    if PC:
        objects = {'DSA':{}, 'PAT':{}}
        for tag in objects:
            objects[tag]['inputMuons'] = selectedMuons[tag]
            objects[tag]['inputDims' ] = [dim for dim in selectedDimuons if dim.composition == tag]
            objects[tag]['outputDims'] = AnalysisTools.applyPairingCriteria(objects[tag]['inputMuons'], objects[tag]['inputDims' ])
        if len(objects['DSA']['outputDims']) + len(objects['PAT']['outputDims']) <= 2:
            selectedDimuons = objects['DSA']['outputDims'] + objects['PAT']['outputDims']
            debug_PC = False
        else:
            atLeastThree = objects['DSA']['outputDims'] + objects['PAT']['outputDims']
            atLeastThree.sort(key = lambda dim: dim.normChi2)
            selectedDimuons = atLeastThree[:2]
            debug_PC = True

    if True:
        # compute all the baseline selection booleans
        DimuonSelections = {dim.ID:Selections.DimuonSelection(dim, cutList='BaselineDimuonCutList') for dim in selectedDimuons}

        # figure out which cuts we actually care about
        cutList = boolsToDimuonCutList(LXYERR, MASS)

        # cutList is some nonzero list, meaning keep only the muons that pass the cut keys in cutList
        if len(cutList) > 0:
            selectedDimuons = [dim for dim in selectedDimuons if DimuonSelections[dim.ID].allOf(*cutList)]

    # for the MC/Data events, skip events with no dimuons, but not for "no selection"
    if NSTATIONS:
        if len(selectedDimuons) == 0: return failedReturnList

    # also filter selectedMuons to only be of those indices that are in the final dimuons
    if True:
        selectedIndices = {'DSA':set(), 'PAT':set()}
        for dim in selectedDimuons:
            selectedIndices[dim.composition].add(dim.idx1)
            selectedIndices[dim.composition].add(dim.idx2)
        for tag in selectedMuons:
            selectedMuons[tag] = [mu for mu in selectedMuons[tag] if mu.idx in selectedIndices[tag]]

    # final return
    return selectedDimuons, selectedMuons['DSA'], selectedMuons['PAT'], debug_PC
