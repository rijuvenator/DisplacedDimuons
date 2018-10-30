import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons

#### CLASS AND FUNCTION DEFINITIONS ####
# setup function for Analyzer class
def begin(self, PARAMS=None):
    pass

# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):

    # delta R between nearest HLT and DSA muons
    self.HistInit('dR_HLT_DSA', ';dR; Muons', 50, 0., 1.)

    # number of unsuccessful and successful HLT-DSA matches
    self.HistInit('matches_HLT_DSA', '; ; Muons', 2, -0.5, 1.5)

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
    for ihist in range(0,10):
        self.HistInit('pTres_for_dpt_over_pt_hist'+str(ihist),    ';(pT(rec)-pT(gen))/pT(gen) for sigma(pT)/pT, hist' + str(ihist) + ';', 50,  -1.,  1.)
        self.HistInit('pTres_for_chi2_over_ndof_hist'+str(ihist), ';(pT(rec)-pT(gen))/pT(gen) for chi2/ndof, hist' + str(ihist) + ';',    50,  -1.,  1.)

        self.HistInit('pTres_for_dpt_over_pt_passed_hist'+str(ihist),    ';(pT(rec)-pT(gen))/pT(gen) for sigma(pT)/pT, passed, hist' + str(ihist) + ';', 50, -1., 1.)
        self.HistInit('pTres_for_chi2_over_ndof_passed_hist'+str(ihist), ';(pT(rec)-pT(gen))/pT(gen) for chi2/ndof, passed, hist' + str(ihist) + ';',    50, -1., 1.)

        self.HistInit('pTpull_for_dpt_over_pt_hist'+str(ihist),   ';(pT(rec)-pT(gen))/sigma(pT) for sigma(pT)/pT, hist' + str(ihist) + ';', 50,  -3.,  3.)

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
    else:
        raise Exception('[ANALYZER ERROR]: signal sample name ' + self.Name + ' is not known')

    # original DSA muons
    DSAMuons = E.getPrimitives('DSAMUON')

    # studies of matching between HLT and DSA muons
    HLTPaths, HLTMuons, L1TMuons = E.getPrimitives('TRIGGER')
    match_found = False
    for hlt_idx1, hltmuon1 in enumerate(HLTMuons):
        # sanity check
        if hltmuon1.pt < 23. or abs(hltmuon1.eta) > 2.0:
            print "+++ Warning: found HLT muon with pT = ", hltmuon1.pt, "and eta = ", hltmuon1.eta, "+++"
        for hlt_idx2, hltmuon2 in enumerate(HLTMuons):
            if hlt_idx2 > hlt_idx1:
                # for a given pair of muons, re-calculate trigger variables and trigger decision
                hlt_dim = hltmuon1.p4 + hltmuon2.p4
                invm = hlt_dim.M()
                angle = hltmuon1.p3.Angle(hltmuon2.p3)
                # the following can happen only if there are more than two HLT muons
                if invm < 10. or angle > 2.5:
                    if len(HLTMuons) == 2:
                        print "+++ Warning: inconsistency in the trigger +++"
                    print "found online dimuon with mass = ", invm, "and angle =", angle
                    print "hlt_idxs: ", hlt_idx1, hlt_idx2, "; list of HLT muons:"
                    for hltmuon in HLTMuons:
                        print(hltmuon)
                else:
                    # found a pair of muons that fired; now look for closest DSA muons
                    matches = []
                    for recmuon in DSAMuons:
                        print(recmuon)
                        deltaR1 = hltmuon1.p4.DeltaR(recmuon.p4)
                        deltaR2 = hltmuon2.p4.DeltaR(recmuon.p4)
                        print 'deltaR1 = ', deltaR1, 'deltaR2 = ', deltaR2
                        matches.append({'hlt_idx':hlt_idx1, 'rec_idx':recmuon.idx, 'deltaR':deltaR1})
                        matches.append({'hlt_idx':hlt_idx2, 'rec_idx':recmuon.idx, 'deltaR':deltaR2})
                    matches = sorted(matches, key=lambda dic:dic['deltaR'])
                    print matches
                    idx_2nd = -999
                    for idx_match, match in enumerate(matches):
                        if match['hlt_idx'] != matches[0]['hlt_idx'] and match['rec_idx'] != matches[0]['rec_idx']:
                            idx_2nd = idx_match
                            break
    
                    # extract dR values and compare them with the threshold
                    dR1 = -999.
                    dR2 = -999.
                    if len(matches) > 0:
                        print 'best match:', matches[0]
                        dR1 = matches[0]['deltaR']
                        self.HISTS['dR_HLT_DSA'].Fill(dR1)
                    if idx_2nd > 0:
                        print '2nd best:', matches[idx_2nd]
                        dR2 = matches[idx_2nd]['deltaR']
                        self.HISTS['dR_HLT_DSA'].Fill(dR2)
                    if abs(dR1) < 0.3 and abs(dR2) < 0.3:
                        match_found = True

    # check for how many events a DSA-HLT match was found
    if match_found:
        self.HISTS['matches_HLT_DSA'].Fill(1)
    else:
        print 'match not found'
        self.HISTS['matches_HLT_DSA'].Fill(0)

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
                pt_res    = (muon.pt - genMuon.pt)/genMuon.pt
                invpt_res = (1./muon.pt - 1./genMuon.pt)/(1./genMuon.pt)
                # (rec-gen) charge and d0 
                q_dif     = muon.charge - genMuon.charge
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

                # sigma(pT)/pT and chi2/dof
                self.HISTS['dpt_over_pt_vs_chi2_over_ndof'].Fill(chi2_over_ndof, sigmapt_over_pt)
                if nStations >= 1 and nStations <= 4:
                    self.HISTS['dpt_over_pt_%dStat'%nStations].Fill(sigmapt_over_pt)
                    self.HISTS['chi2_over_ndof_%dStat'%nStations].Fill(chi2_over_ndof)

                # pT resolution in slices of sigma(pT)/pT
                if sigmapt_over_pt < 0.2:
                    ihist = 0
                elif sigmapt_over_pt >= 0.2 and sigmapt_over_pt < 0.4:
                    ihist = 1
                elif sigmapt_over_pt >= 0.4 and sigmapt_over_pt < 0.6:
                    ihist = 2
                elif sigmapt_over_pt >= 0.6 and sigmapt_over_pt < 0.8:
                    ihist = 3
                elif sigmapt_over_pt >= 0.8 and sigmapt_over_pt < 1.0:
                    ihist = 4
                elif sigmapt_over_pt >= 1.0 and sigmapt_over_pt < 1.5:
                    ihist = 5
                elif sigmapt_over_pt >= 1.5 and sigmapt_over_pt < 2.0:
                    ihist = 6
                elif sigmapt_over_pt >= 2.0 and sigmapt_over_pt < 3.0:
                    ihist = 7
                elif sigmapt_over_pt >= 3.0 and sigmapt_over_pt < 4.0:
                    ihist = 8
                elif sigmapt_over_pt >= 4.0:
                    ihist = 9
                self.HISTS['pTres_for_dpt_over_pt_hist%d'%ihist].Fill(pt_res)
                if nStations > 1 and nDTCSCHits > 12:
                    self.HISTS['pTres_for_dpt_over_pt_passed_hist%d'%ihist].Fill(pt_res)

                # pT pull in slices of sigma(pT)/pT
                pt_pull = (muon.pt - genMuon.pt)/muon.ptError
                self.HISTS['pTpull_for_dpt_over_pt_hist%d'%ihist].Fill(pt_pull)

                # pT resolution in slices of chi2/ndof
                if chi2_over_ndof < 0.2:
                    ihist = 0
                elif chi2_over_ndof >= 0.2 and chi2_over_ndof < 0.4:
                    ihist = 1
                elif chi2_over_ndof >= 0.4 and chi2_over_ndof < 0.6:
                    ihist = 2
                elif chi2_over_ndof >= 0.6 and chi2_over_ndof < 0.8:
                    ihist = 3
                elif chi2_over_ndof >= 0.8 and chi2_over_ndof < 1.0:
                    ihist = 4
                elif chi2_over_ndof >= 1.0 and chi2_over_ndof < 1.5:
                    ihist = 5
                elif chi2_over_ndof >= 1.5 and chi2_over_ndof < 2.0:
                    ihist = 6
                elif chi2_over_ndof >= 2.0 and chi2_over_ndof < 3.0:
                    ihist = 7
                elif chi2_over_ndof >= 3.0 and chi2_over_ndof < 4.0:
                    ihist = 8
                elif chi2_over_ndof >= 4.0:
                    ihist = 9
                self.HISTS['pTres_for_chi2_over_ndof_hist%d'%ihist].Fill(pt_res)
                if nStations > 1 and nDTCSCHits > 12:
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
        BRANCHKEYS  = ('EVENT', 'GEN', 'TRIGGER', 'DSAMUON', 'DIMUON',),
    )

    # write plots
    analyzer.writeHistograms('roots/muonQualityStudies{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else ''))
