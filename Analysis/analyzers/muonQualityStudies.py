import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons, matchedDimuons, matchedTrigger

# slices of sigma(pT)/pT and chi2/ndof, for histograms
SLICE_EDGES = [0.2, 0.4, 0.6, 0.8, 1.0, 1.5, 2.0, 3.0, 4.0, float('inf')]

#### CLASS AND FUNCTION DEFINITIONS ####
# setup function for Analyzer class
def begin(self, PARAMS=None):
    pass

# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):

    # delta R between nearest HLT and DSA muons
    self.HistInit('dR_HLT_DSA',            ';dR; Muons',          50, 0., 1.)
    self.HistInit('dR1_HLT_DSA_BadEvent',  ';best dR; Muons',     50, 0., 1.)
    self.HistInit('dR2_HLT_DSA_BadEvent',  ';2nd best dR; Muons', 50, 0., 1.)
    self.HistInit('dR1_HLT_DSA_GoodEvent', ';best dR; Muons',     50, 0., 1.)
    self.HistInit('dR2_HLT_DSA_GoodEvent', ';2nd best dR; Muons', 50, 0., 1.)

    # number of unsuccessful and successful HLT-DSA matches
    self.HistInit('matches_HLT_DSA', '; ; Events', 5, -0.5, 4.5)

    # some diagnostics for RECO muons matched to signal GEN muons but not matched to HLT muons
    self.HistInit('unmatched_pt_res',   ';(pT(rec)-pT(gen))/pT(gen);Muons',  50, -1., 1.)
    self.HistInit('unmatched_invm_res', ';(m(rec)-m(gen))/m(gen);Dimuons',   50, -1., 1.)
    self.HistInit('unmatched_pt_rec_vs_pt_gen', ';pT(gen); pT(rec)',        100,  0., 200., 100, 0., 200.)
    self.HistInit('unmatched_pt_rec_vs_pt_gen_zoomed', ';pT(gen); pT(rec)',  50,  0., 50.,   50, 0., 50.)

    # N(CSC stations) vs N(DT stations)
    self.HistInit('CSC_vs_DT_Stations', ';N(DT stations); N(CSC stations)', 5, -0.5, 4.5, 5, -0.5, 4.5)

    # Nhits
    self.HistInit('nMuonHits',  ';N(muon hits); Muons',   55, 0., 55.)
    self.HistInit('nDTCSCHits', ';N(DT+CSC hits); Muons', 50, 0., 50.)
    self.HistInit('nDTHits',    ';N(DT hits); Muons',     50, 0., 50.)
    self.HistInit('nCSCHits',   ';N(CSC hits); Muons',    30, 0., 30.)
    self.HistInit('nRPCHits',   ';N(RPC hits); Muons',    10, 0., 10.)

    # Nhits for various Nstations
    for istat in range(1,5):
        xmax_tot = istat*15
        self.HistInit('nMuonHits_' +str(istat)+'Stat', ';N(muon hits), N(stats) = '   + str(istat) + '; Muons', xmax_tot, 0., xmax_tot)
        self.HistInit('nDTCSCHits_'+str(istat)+'Stat', ';N(DT+CSC hits), N(stats) = ' + str(istat) + '; Muons', xmax_tot, 0., xmax_tot)
        xmax_dt  = istat*13
        self.HistInit('nDTHits_'   +str(istat)+'Stat', ';N(DT hits), N(stats) = '     + str(istat) + '; Muons', xmax_dt,  0., xmax_dt)
        xmax_csc = istat*7
        self.HistInit('nCSCHits_'  +str(istat)+'Stat', ';N(CSC hits), N(stats) = '    + str(istat) + '; Muons', xmax_csc, 0., xmax_csc)
        self.HistInit('nRPCHits_'  +str(istat)+'Stat', ';N(RPC hits), N(stats) = '    + str(istat) + '; Muons',       10, 0., 10.)

        self.HistInit('nCSCHits_vs_nDTHits_'+str(istat)+'Stat', ';N(DT hits); N(CSC hits), N(stats) = ' + str(istat), xmax_dt+1, -1., xmax_dt, xmax_csc+1, -1., xmax_csc)

    # resolutions for groups of 3 DT+CSC hits
    for ihist in range(0,17):
        self.HistInit('pTres_DTCSChits_hist'+str(ihist),    ';(pT(rec)-pT(gen))/pT(gen), hist' + str(ihist) + ';',       50,  -1.,  1.)
        self.HistInit('invpTres_DTCSChits_hist'+str(ihist), ';(1/pT(rec)-1/pT(gen))/1/pT(gen), hist' + str(ihist) + ';', 50,  -1.,  1.)
        self.HistInit('qdif_DTCSChits_hist'+str(ihist),     ';q(rec)-q(gen), hist' + str(ihist) + ';',                    5, -2.5, 2.5)
        self.HistInit('d0dif_DTCSChits_hist'+str(ihist),    ';d0(rec)-d0(gen), hist' + str(ihist) + ';',                 50, -25., 25.)

        # ditto for Nstat > 1
        self.HistInit('pTres_DTCSChits_Stat234_hist'+str(ihist),    ';(pT(rec)-pT(gen))/pT(gen), N(stats) > 1, hist' + str(ihist) + ';',       50,  -1.,  1.)
        self.HistInit('invpTres_DTCSChits_Stat234_hist'+str(ihist), ';(1/pT(rec)-1/pT(gen))/1/pT(gen), N(stats) > 1, hist' + str(ihist) + ';', 50,  -1.,  1.)
        self.HistInit('qdif_DTCSChits_Stat234_hist'+str(ihist),     ';q(rec)-q(gen), N(stats) > 1, hist' + str(ihist) + ';',                    5, -2.5, 2.5)
        self.HistInit('d0dif_DTCSChits_Stat234_hist'+str(ihist),    ';d0(rec)-d0(gen), N(stats) > 1, hist' + str(ihist) + ';',                 50, -25., 25.)

    # fine resolution scan for Nstat > 1 and Nhits from 12 to 19
    for ihits in range(12,20):
        self.HistInit('pTres_Stat234_'+str(ihits)+'DTCSChits',    ';(pT(rec)-pT(gen))/pT(gen), N(stats) > 1,' + str(ihits) + ' DTCSChits;',        50, -1.,  1. )
        self.HistInit('invpTres_Stat234_'+str(ihits)+'DTCSChits', ';(1/pT(rec)-1/pT(gen))/1/pT(gen), N(stats) > 1,' + str(ihits) + ' DTCSChits;',  50, -1.,  1. )
        self.HistInit('qdif_Stat234_'+str(ihits)+'DTCSChits',     ';q(rec)-q(gen), N(stats) > 1,' + str(ihits) + ' DTCSChits;',                     5, -2.5, 2.5)

    # resolutions in barrel, endcap, and overlap
    for ihist in range(0,10):
        self.HistInit('pTres_DThits_barrel_hist'+str(ihist),     ';(pT(rec)-pT(gen))/pT(gen), barrel, hist'  + str(ihist) + ';', 50, -1., 1.)
        self.HistInit('pTres_CSChits_endcap_hist'+str(ihist),    ';(pT(rec)-pT(gen))/pT(gen), endcap, hist'  + str(ihist) + ';', 50, -1., 1.)
        self.HistInit('pTres_DTCSChits_overlap_hist'+str(ihist), ';(pT(rec)-pT(gen))/pT(gen), overlap, hist' + str(ihist) + ';', 50, -1., 1.)

        self.HistInit('d0dif_DThits_barrel_hist'+str(ihist),     ';d0(rec)-d0(gen), barrel, hist'  + str(ihist) + ';', 50, -25., 25.)
        self.HistInit('d0dif_CSChits_endcap_hist'+str(ihist),    ';d0(rec)-d0(gen), endcap, hist'  + str(ihist) + ';', 50, -25., 25.)
        self.HistInit('d0dif_DTCSChits_overlap_hist'+str(ihist), ';d0(rec)-d0(gen), overlap, hist' + str(ihist) + ';', 50, -25., 25.)

    # sigma(pT)/pT vs chi2/ndof
    self.HistInit('dpt_over_pt_vs_chi2_over_ndof', ';chi2/ndof; sigma(pT)/pT', 50, 0., 5., 50, 0., 5.)

    # sigma(pT)/pT and chi2/ndof for various Nstations
    for istat in range(1,5):
        self.HistInit('dpt_over_pt_'+str(istat)+'Stat',     ';sigma(pT)/pT, N(stats) = ' + str(istat) + '; Muons', 50, 0., 5.)
        self.HistInit('chi2_over_ndof_' +str(istat)+'Stat', ';chi2/ndof, N(stats) = ' + str(istat) + '; Muons',    50, 0., 5.)

    # sigma(pT)/pT and chi2/ndof for groups of 3 DT+CSC hits
    for ihist in range(0,17):
        self.HistInit('dpt_over_pt_DTCSChits_hist'+str(ihist),            ';sigma(pT)/pT, hist' + str(ihist) + ';',               50, 0., 5.)
        self.HistInit('chi2_over_ndof_DTCSChits_hist'+str(ihist),         ';chi2/ndof, hist' + str(ihist) + ';',                  50, 0., 5.)

        # Ditto for Nstat > 1
        self.HistInit('dpt_over_pt_DTCSChits_Stat234_hist'+str(ihist),    ';sigma(pT)/pT, N(stats) > 1, hist' + str(ihist) + ';', 50, 0., 5.)
        self.HistInit('chi2_over_ndof_DTCSChits_Stat234_hist'+str(ihist), ';chi2/ndof, N(stats) > 1, hist' + str(ihist) + ';',    50, 0., 5.)

    # pT resolution in slices of sigma(pT)/pT and chi2/ndof
    for ihist in range(len(SLICE_EDGES)):
        self.HistInit('pTres_for_dpt_over_pt_hist'+str(ihist),    ';(pT(rec)-pT(gen))/pT(gen) for sigma(pT)/pT, hist' + str(ihist) + ';', 50,  -1.,  1.)
        self.HistInit('pTres_for_chi2_over_ndof_hist'+str(ihist), ';(pT(rec)-pT(gen))/pT(gen) for chi2/ndof, hist' + str(ihist) + ';',    50,  -1.,  1.)

        self.HistInit('pTres_for_dpt_over_pt_passed_hist'+str(ihist),    ';(pT(rec)-pT(gen))/pT(gen) for sigma(pT)/pT, passed, hist' + str(ihist) + ';', 50, -1., 1.)
        self.HistInit('pTres_for_chi2_over_ndof_passed_hist'+str(ihist), ';(pT(rec)-pT(gen))/pT(gen) for chi2/ndof, passed, hist' + str(ihist) + ';',    50, -1., 1.)

        self.HistInit('pTpull_for_dpt_over_pt_hist'+str(ihist),   ';(pT(rec)-pT(gen))/sigma(pT) for sigma(pT)/pT, hist' + str(ihist) + ';', 50,  -3.,  3.)

    self.HistInit('eta_for_dpt_over_pt_gt_1',                ';eta of original muons, sigma(pT)/pT > 1',                       100, -3., 3.)
    self.HistInit('pTres_ref_for_dpt_over_pt_gt_1',          ';(pT(rec)-pT(gen))/pT(gen) of refitted muons, sigma(pT)/pT > 1',  50, -1., 1.)
    self.HistInit('dpt_over_pt_ref_for_dpt_over_pt_gt_1',    ';sigma(pT)/pT of refitted muons, sigma(pT)/pT > 1',               50,  0., 5.)
    self.HistInit('pTres_ref_for_dpt_over_pt_gt_1_ref_lt_1', ';(pT(rec)-pT(gen))/pT(gen) of refitted muons, sigma(pT)/pT > 1, sigma(pT_ref)/pT_ref < 1',  50, -1., 1.)

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):

#    print(E)

    event = E.getPrimitives('EVENT')
#    print(event)

    # require that the trigger has fired
    if not Selections.passedTrigger(E): return

    if self.SP is None:
        raise Exception('[ANALYZER ERROR]: This script runs on signal only.')
    if '4Mu' in self.NAME:
        mu11, mu12, mu21, mu22, X1, X2, H, P, extramu = E.getPrimitives('GEN')
        genMuons = (mu11, mu12, mu21, mu22)
        genMuonPairs = ((mu11, mu12), (mu21, mu22))
    elif '2Mu2J' in self.NAME:
        mu1, mu2, j1, j2, X, XP, H, P, extramu = E.getPrimitives('GEN')
        genMuons = (mu1, mu2)
        genMuonPairs = ((mu1, mu2),)

    # original DSA muons
    DSAMuons = E.getPrimitives('DSAMUON')

    # all dimuons and dimuons made of muons passing quality cuts
    allDimuons = E.getPrimitives('DIMUON')
    selectedDSAmuons  = [mu for mu in DSAMuons if mu.nDTStations+mu.nCSCStations>1 and mu.nCSCHits+mu.nDTHits>12 and mu.ptError/mu.pt<1.]
    DSAmuons_formatch = [mu for mu in DSAMuons if mu.nDTStations+mu.nCSCStations>1 and mu.nCSCHits+mu.nDTHits>12 and mu.ptError/mu.pt<1. and abs(mu.eta) < 2.0 and mu.pt > 5.]
    selectedOIndices = [mu.idx for mu in selectedDSAmuons]
    selectedDimuons  = [dim for dim in allDimuons if dim.idx1 in selectedOIndices and dim.idx2 in selectedOIndices]

    # studies of matching between HLT and DSA muons
    HLTPaths, HLTMuons, L1TMuons = E.getPrimitives('TRIGGER')
#    print "List of HLT muons:"
#    for hltmuon in HLTMuons:
#        print(hltmuon)
    for muon in DSAMuons:
        print muon

    match_found = False
    HLTDSAMatches = matchedTrigger(HLTMuons, DSAmuons_formatch, saveDeltaR=True, threshold=0.4, printAllMatches=True)
    for i, j in HLTDSAMatches:
        imatch = 0
        for match in HLTDSAMatches[(i,j)]['bestMatches']:
            if   imatch == 0: print 'best match:', i, j, match
            elif imatch == 1: print '2nd best:',   i, j, match
            imatch += 1
            dR = match['deltaR']
            self.HISTS['dR_HLT_DSA'].Fill(dR)
        if HLTDSAMatches[(i,j)]['matchFound'] == True:
            match_found = True

    # check for how many events a DSA-HLT match was found
    self.HISTS['matches_HLT_DSA'].Fill(0)
    if match_found:
        self.HISTS['matches_HLT_DSA'].Fill(1)
    else:
        self.HISTS['matches_HLT_DSA'].Fill(2)

        print 'match not found'
        print(E)

        # check if there were any matching dimuons
        for genMuonPair in genMuonPairs:
            dimuonMatches, muonMatches, exitcode = matchedDimuons(genMuonPair, allDimuons)
            if len(dimuonMatches) > 0:
                self.HISTS['matches_HLT_DSA'].Fill(3)
            else:
                for i, j in HLTDSAMatches:
                    imatch = 0
                    for match in HLTDSAMatches[(i,j)]['bestMatches']:
                        dR = match['deltaR']
                        if   imatch == 0: self.HISTS['dR1_HLT_DSA_BadEvent'].Fill(dR)
                        elif imatch == 1: self.HISTS['dR2_HLT_DSA_BadEvent'].Fill(dR)
                        imatch += 1

            # more detailed diagnostics for cases when a good-quality
            # signal dimuon is lost
            dimuonMatches, muonMatches, exitcode = matchedDimuons(genMuonPair, selectedDimuons)
            if len(dimuonMatches) > 0:
                print "Lose good event!"
                self.HISTS['matches_HLT_DSA'].Fill(4)
                for i, j in HLTDSAMatches:
                    imatch = 0
                    for match in HLTDSAMatches[(i,j)]['bestMatches']:
                        dR = match['deltaR']
                        if   imatch == 0: self.HISTS['dR1_HLT_DSA_GoodEvent'].Fill(dR)
                        elif imatch == 1: self.HISTS['dR2_HLT_DSA_GoodEvent'].Fill(dR)
                        imatch += 1

                gen_dim = genMuonPair[0].p4 + genMuonPair[1].p4
                gen_invm = gen_dim.M()
                for dimuonMatch in dimuonMatches:
                    dimuon = dimuonMatch['dim']
                    rec_invm = dimuon.p4.M()
                    print "gen_mass = ", gen_invm, "rec_mass = ", rec_invm
                    print "gen_Lxy = ", genMuonPair[0].Lxy_, "rec_Lxy = ", dimuon.Lxy(), "+/-", dimuon.LxyErr()
                    print(dimuon)
                    unmatched_invm_res = (rec_invm - gen_invm)/gen_invm
                    self.HISTS['unmatched_invm_res'].Fill(unmatched_invm_res)
                    for muonMatch in muonMatches:
                        recmu_idx = muonMatch[0]['oidx']
                        muon_found = False
                        for i, j in HLTDSAMatches:
                            for hltMatch in HLTDSAMatches[(i,j)]['bestMatches']:
                                if hltMatch['rec_idx'] == recmu_idx and hltMatch['deltaR'] < 0.4:
                                    muon_found = True
                                    break
                        if muon_found == False:
                            print "DSA muon not matched to HLT muon:", recmu_idx
                            recmu_p4 = muonMatch[0]['muon'].p4
                            recmu_pt = muonMatch[0]['muon'].pt
                            for genmu in genMuonPair:
                                genmu_p4 = genmu.p4
                                dr = recmu_p4.DeltaR(genmu_p4)
                                if dr < 0.2:
                                    genmu_pt = genmu.pt
                                    unmatched_pt_res = (recmu_pt - genmu_pt)/genmu_pt
                                    print "muon pT = ", recmu_pt, "pt of matched gen muon = ", genmu_pt, "pt_res =", unmatched_pt_res
                                    self.HISTS['unmatched_pt_res'].Fill(unmatched_pt_res)
                                    self.HISTS['unmatched_pt_rec_vs_pt_gen'].Fill(genmu_pt, recmu_pt)
                                    self.HISTS['unmatched_pt_rec_vs_pt_gen_zoomed'].Fill(genmu_pt, recmu_pt)

    # studies of single-muon variables
    # loop over genMuons and fill histograms
    # for genMuon in genMuons:
    for gen_idx, genMuon in enumerate(genMuons):
#        print(genMuon)
        matches = matchedMuons(genMuon, DSAMuons, vertex='BS')
        if len(matches) > 0:
            for match in matches:

                muon = match['muon']

                # number of hits
                nDTCSCHits = muon.nDTHits + muon.nCSCHits
                nRPCHits   = muon.nMuonHits - nDTCSCHits
                self.HISTS['nMuonHits'].Fill(muon.nMuonHits)
                self.HISTS['nDTCSCHits'].Fill(nDTCSCHits)
                self.HISTS['nDTHits'].Fill(muon.nDTHits)
                self.HISTS['nCSCHits'].Fill(muon.nCSCHits)
                self.HISTS['nRPCHits'].Fill(nRPCHits)

                # number of hits for various numbers of stations
                nStations = muon.nDTStations + muon.nCSCStations
                self.HISTS['CSC_vs_DT_Stations'].Fill(muon.nDTStations, muon.nCSCStations)
                if nStations >= 1 and nStations <= 4:
                    self.HISTS['nMuonHits_%dStat'%nStations]. Fill(muon.nMuonHits)
                    self.HISTS['nDTCSCHits_%dStat'%nStations].Fill(nDTCSCHits)
                    if muon.nDTHits > 0:
                        self.HISTS['nDTHits_%dStat'%nStations]. Fill(muon.nDTHits)
                    if muon.nCSCHits > 0:
                        self.HISTS['nCSCHits_%dStat'%nStations].Fill(muon.nCSCHits)
                    self.HISTS['nRPCHits_%dStat'%nStations].  Fill(nRPCHits)
                    self.HISTS['nCSCHits_vs_nDTHits_%dStat'%nStations].Fill(muon.nDTHits, muon.nCSCHits)
                elif nStations < 1 or nStations > 4:
                    print '+++ Warning: no histo filled; N(stat) = ', nStations

                # pT and 1/pT resolutions
                pt_res    = (muon.pt - genMuon.BS.pt)/genMuon.BS.pt
                invpt_res = (1./muon.pt - 1./genMuon.BS.pt)/(1./genMuon.BS.pt)
                # (rec-gen) charge and d0
                q_dif     = muon.charge - genMuon.BS.charge
                d0_dif    = muon.d0(extrap=None) - genMuon.d0(extrap=None)
#                print 'gen idx', gen_idx, 'muon idx = ', muon.idx, ' pT res = ', pt_res, 'd0 dif = ', d0_dif

                # sigma(pT)/pT and chi2/dof
                sigmapt_over_pt = muon.ptError/muon.pt
                chi2_over_ndof  = muon.chi2/muon.ndof

                # resolutions for groups of 3 DT+CSC hits
                ihist = nDTCSCHits//3
                self.HISTS['pTres_DTCSChits_hist%d'%ihist].Fill(pt_res)
                self.HISTS['invpTres_DTCSChits_hist%d'%ihist].Fill(invpt_res)
                self.HISTS['qdif_DTCSChits_hist%d'%ihist].Fill(q_dif)
                self.HISTS['d0dif_DTCSChits_hist%d'%ihist].Fill(d0_dif)

                # ditto for Nstat > 1
                if nStations > 1:
                    self.HISTS['pTres_DTCSChits_Stat234_hist%d'%ihist].Fill(pt_res)
                    self.HISTS['invpTres_DTCSChits_Stat234_hist%d'%ihist].Fill(invpt_res)
                    self.HISTS['qdif_DTCSChits_Stat234_hist%d'%ihist].Fill(q_dif)
                    self.HISTS['d0dif_DTCSChits_Stat234_hist%d'%ihist].Fill(d0_dif)

                    # fine scan for Nhits between 12 and 19
                    if nDTCSCHits >= 12 and nDTCSCHits <= 19:
                        self.HISTS['pTres_Stat234_%dDTCSChits'%nDTCSCHits].Fill(pt_res)
                        self.HISTS['invpTres_Stat234_%dDTCSChits'%nDTCSCHits].Fill(pt_res)
                        self.HISTS['qdif_Stat234_%dDTCSChits'%nDTCSCHits].Fill(q_dif)

                # sigma(pT)/pT and chi2/dof for groups of 3 DT+CSC hits
                self.HISTS['dpt_over_pt_DTCSChits_hist%d'%ihist].Fill(sigmapt_over_pt)
                self.HISTS['chi2_over_ndof_DTCSChits_hist%d'%ihist].Fill(chi2_over_ndof)

                # ditto for Nstat > 1
                if nStations > 1:
                    self.HISTS['dpt_over_pt_DTCSChits_Stat234_hist%d'%ihist].Fill(sigmapt_over_pt)
                    self.HISTS['chi2_over_ndof_DTCSChits_Stat234_hist%d'%ihist].Fill(chi2_over_ndof)

                # resolutions in barrel, endcap, and overlap
                if muon.nDTStations > 0 and muon.nCSCStations == 0:
                    ihist = muon.nDTHits//6
#                    print 'barrel: ', muon.nDTHits, ihist
                    self.HISTS['pTres_DThits_barrel_hist%d'%ihist].Fill(pt_res)
                    self.HISTS['d0dif_DThits_barrel_hist%d'%ihist].Fill(d0_dif)
                elif muon.nDTStations == 0 and muon.nCSCStations > 0:
                    ihist = muon.nCSCHits//3
                    # overlapping chambers?
                    if ihist > 9:
                        print "CSCs: > 29 hits", muon.nCSCHits
                        ihist = 8
#                    print 'endcap: ', muon.nCSCHits, ihist
                    self.HISTS['pTres_CSChits_endcap_hist%d'%ihist].Fill(pt_res)
                    self.HISTS['d0dif_CSChits_endcap_hist%d'%ihist].Fill(d0_dif)
                elif muon.nDTStations > 0 and muon.nCSCStations > 0:
                    ihist = nDTCSCHits//6
#                    print 'overlap: ', nDTCSCHits, ihist
                    self.HISTS['pTres_DTCSChits_overlap_hist%d'%ihist].Fill(pt_res)
                    self.HISTS['d0dif_DTCSChits_overlap_hist%d'%ihist].Fill(d0_dif)

                # make sure that the nDTCSCHits > 12 cut supersedes the nStations > 1 one
                if nDTCSCHits > 12 and nStations <= 1:
                    print "+++ Mismatch between nStations and nHits: nStations = ", nStations, "nDTCSCHits = ", nDTCSCHits, "+++"

                # sigma(pT)/pT and chi2/dof
                self.HISTS['dpt_over_pt_vs_chi2_over_ndof'].Fill(chi2_over_ndof, sigmapt_over_pt)
                if nStations >= 1 and nStations <= 4:
                    self.HISTS['dpt_over_pt_%dStat'%nStations].Fill(sigmapt_over_pt)
                    self.HISTS['chi2_over_ndof_%dStat'%nStations].Fill(chi2_over_ndof)

                # pT resolution in slices of sigma(pT)/pT
                ihist = 0
                while sigmapt_over_pt >= SLICE_EDGES[ihist]: ihist += 1
                self.HISTS['pTres_for_dpt_over_pt_hist%d'%ihist].Fill(pt_res)
                if nDTCSCHits > 12:
                    self.HISTS['pTres_for_dpt_over_pt_passed_hist%d'%ihist].Fill(pt_res)

                # pT pull in slices of sigma(pT)/pT
                pt_pull = (muon.pt - genMuon.BS.pt)/muon.ptError
                self.HISTS['pTpull_for_dpt_over_pt_hist%d'%ihist].Fill(pt_pull)

                # Refitted muons for DSA muons failing dpT/pT cut
                if sigmapt_over_pt > 1.:
                    self.HISTS['eta_for_dpt_over_pt_gt_1'].Fill(muon.eta)
                    for genMuonPair in genMuonPairs:
                        dimuonMatches, muonMatches, exitcode = matchedDimuons(genMuonPair, allDimuons)
                        for match in dimuonMatches:
                            dimuon = match['dim']
                            for refmu in (dimuon.mu1, dimuon.mu2):
                                if refmu.idx == muon.idx:
#                                    print "Found refitted muon", refmu.idx, refmu.pt
                                    pt_res_ref          = (refmu.pt - genMuon.pt)/genMuon.pt
                                    sigmapt_over_pt_ref = refmu.ptError/refmu.pt
                                    self.HISTS['pTres_ref_for_dpt_over_pt_gt_1'].Fill(pt_res_ref)
                                    self.HISTS['dpt_over_pt_ref_for_dpt_over_pt_gt_1'].Fill(sigmapt_over_pt_ref)
                                    if sigmapt_over_pt_ref < 1:
                                        self.HISTS['pTres_ref_for_dpt_over_pt_gt_1_ref_lt_1'].Fill(pt_res_ref)


                # pT resolution in slices of chi2/ndof
                ihist = 0
                while chi2_over_ndof >= SLICE_EDGES[ihist]: ihist += 1
                self.HISTS['pTres_for_chi2_over_ndof_hist%d'%ihist].Fill(pt_res)
                if nDTCSCHits > 12:
                    self.HISTS['pTres_for_chi2_over_ndof_passed_hist%d'%ihist].Fill(pt_res)

    # get dimuons
    # Dimuons = E.getPrimitives('DIMUON')

    # loop over dimuons and fill if they pass their selection
    # for dimuon in Dimuons:
    #    print(dimuon)
    #    if Selections.DimuonSelection(dimuon):
    #        self.HISTS['pT'].Fill(dimuon.pt)

# cleanup function for Analyzer class
def end(self, PARAMS=None):
    pass

#### RUN ANALYSIS ####
if __name__ == '__main__':
    # get arguments
    ARGS = Analyzer.PARSER.parse_args()

    # set sample object based on arguments
    Analyzer.setSample(ARGS)

    # define Analyzer methods
    for METHOD in ('begin', 'declareHistograms', 'analyze', 'end'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])

    # declare analyzer
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('EVENT', 'GEN', 'TRIGGER', 'DSAMUON', 'RSAMUON', 'DIMUON',),
    )

    # write plots
    analyzer.writeHistograms('roots/muonQualityStudies{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else ''))
