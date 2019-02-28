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


def SelectObjectsReordered(E, CUTS, Dimuons3, DSAmuons, PATmuons, keepHybrids=False, option=1):

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
        selectedMuons['DSA'], selectedMuons['PAT'], selectedDimuons = AnalysisTools.replaceDSAMuons(selectedMuons['DSA'], PATmuons, selectedDimuons, keepHybrids)
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

        def dimuonFilter(dim, selectedIndices):
            if dim.composition != 'HYBRID':
                return set(dim.ID).issubset(selectedIndices[dim.composition])
            else:
                return dim.idx1 in selectedIndices['DSA'] and dim.idx2 in selectedIndices['PAT']
        selectedDimuons = [dim for dim in selectedDimuons if dimuonFilter(dim, selectedIndices)]

    # apply pairing criteria and transform selectedDimuons
    # pairing criteria was developed with DSA muons and DSA-DSA dimuons in mind
    # after replacement: run pairing criteria twice on the disjoint sets of dimuons
    # without hybrids, sort the resulting list by vertex chi^2 and discard all but the lowest two
    # with hybrids, sort the hybrids list by vertex chi^2 and add the lowest two non-overlapping ones
    if PC:
        # option 1: do PC on DSA and PAT, and only add hybrids if necessary
        if option == 1:
            objects = {'DSA':{}, 'PAT':{}}
            for tag in objects:
                objects[tag]['inputMuons'] = selectedMuons[tag]
                objects[tag]['inputDims' ] = [dim for dim in selectedDimuons if dim.composition == tag]
                objects[tag]['outputDims'] = AnalysisTools.applyPairingCriteria(objects[tag]['inputMuons'], objects[tag]['inputDims' ])

            candidateDimuons = objects['DSA']['outputDims'] + objects['PAT']['outputDims']
            nCandidateDimuons = len(candidateDimuons)

            # more than 2: sort by vtx chi^2 and take the lowest two
            if nCandidateDimuons > 2:
                candidateDimuons.sort(key = lambda dim: dim.normChi2)
                selectedDimuons = candidateDimuons[:2]

            # exactly 2: do nothing
            elif nCandidateDimuons == 2:
                selectedDimuons = candidateDimuons

            # less than two: do nothing if without hybrids
            # with hybrids: if 0, take lowest <= 2 hybrids sorted by vtx chi^2
            # if 1, add on the first hybrid (in the sorted list) that doesn't overlap with the one found
            else:
                if keepHybrids:
                    hybridDimuons = [dim for dim in selectedDimuons if dim.composition == 'HYBRID']
                    hybridDimuons.sort(key = lambda dim: dim.normChi2)
                    if nCandidateDimuons == 0:
                        selectedDimuons = hybridDimuons[:2]
                    else:
                        alreadyFound = candidateDimuons[0]
                        bestHybrid = None
                        whichIndex = '1' if alreadyFound.composition == 'DSA' else '2'
                        for hybDim in hybridDimuons:
                            if getattr(hybDim, 'idx'+whichIndex) not in alreadyFound.ID:
                                bestHybrid = hybDim
                                break
                        if bestHybrid is not None:
                            selectedDimuons = [alreadyFound, bestHybrid]
                        else:
                            selectedDimuons = candidateDimuons
                else:
                    selectedDimuons = candidateDimuons

        # option 2: do PC on DSA and PAT, add all hybrid dimuons, sort by vtx chi^2, and take the lowest 2
        elif option == 2:
            objects = {'DSA':{}, 'PAT':{}}
            for tag in objects:
                objects[tag]['inputMuons'] = selectedMuons[tag]
                objects[tag]['inputDims' ] = [dim for dim in selectedDimuons if dim.composition == tag]
                objects[tag]['outputDims'] = AnalysisTools.applyPairingCriteria(objects[tag]['inputMuons'], objects[tag]['inputDims' ])

            candidateDimuons = objects['DSA']['outputDims'] + objects['PAT']['outputDims'] + [dim for dim in selectedDimuons if dim.composition == 'HYBRID']
            candidateDimuons.sort(key = lambda dim: dim.normChi2)

            selectedDimuons = candidateDimuons[:2]

        # option 3: do PC on DSA, PAT, and hybrid, sort by vtx chi^2, and take the lowest 2
        elif option == 3:
            objects = {'DSA':{}, 'PAT':{}}
            for tag in objects:
                objects[tag]['inputMuons'] = selectedMuons[tag]
                objects[tag]['inputDims' ] = [dim for dim in selectedDimuons if dim.composition == tag]
                objects[tag]['outputDims'] = AnalysisTools.applyPairingCriteria(objects[tag]['inputMuons'], objects[tag]['inputDims' ])

            tag = 'HYBRID'
            objects['HYBRID'] = {}
            if True:
                objects[tag]['inputMuons'] = selectedMuons['DSA'] + selectedMuons['PAT']
                objects[tag]['inputDims' ] = [dim for dim in selectedDimuons if dim.composition == tag]
                objects[tag]['outputDims'] = AnalysisTools.applyPairingCriteria(objects[tag]['inputMuons'], objects[tag]['inputDims' ])

            candidateDimuons = objects['DSA']['outputDims'] + objects['PAT']['outputDims'] + objects['HYBRID']['outputDims']
            candidateDimuons.sort(key = lambda dim: dim.normChi2)

            selectedDimuons = candidateDimuons[:2]

        # option 4: do PC on all muons and dimuons together, yielding 2 dimuons
        elif option == 4:
            selectedDimuons = AnalysisTools.applyPairingCriteria(selectedMuons['DSA'] + selectedMuons['PAT'], selectedDimuons)

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
