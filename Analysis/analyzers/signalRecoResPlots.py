import math
import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons, matchedDimuons

HEADERS = ('PRETTY', 'EXTRA', 'AXES', 'RESAXES', 'GENLAMBDA', 'RECOLAMBDA', 'RESLAMBDA', 'ISDIF')
VALUES  = (
    ('pT'   , 'p_{T}'       , ' [GeV]', (1500, 0.,1500.), (1000,-1.  ,9.  ), lambda gm:gm.pt                  , lambda muon:muon.pt              , lambda rq, gq:(rq-gq)/gq, False),
    ('Lxy'  , 'L_{xy}'      , ' [cm]' , (1000, 0., 800.), (1000,-100.,100.), lambda gm:gm.Lxy()               , lambda dim :dim.Lxy()            , lambda rq, gq:(rq-gq)   , True ),
    ('d0'   , 'd_{0}'       , ' [cm]' , (2000, 0.,1000.), (1000,-50. ,50. ), lambda gm:gm.d0(extrap=None)     , lambda muon:muon.d0()            , lambda rq, gq:(rq-gq)   , True ),
    ('dz'   , 'd_{z}'       , ' [cm]' , (2000, 0.,1000.), (1000,-50. ,50. ), lambda gm:gm.dz(extrap=None)     , lambda muon:muon.dz()            , lambda rq, gq:(rq-gq)   , True ),
    ('d0Lin', 'lin d_{0}'   , ' [cm]' , (2000, 0.,1000.), (1000,-50. ,50. ), lambda gm:gm.d0()                , lambda muon:muon.d0(extrap='LIN'), lambda rq, gq:(rq-gq)   , True ),
    ('dzLin', 'lin d_{z}'   , ' [cm]' , (2000, 0.,1000.), (1000,-50. ,50. ), lambda gm:gm.dz()                , lambda muon:muon.dz(extrap='LIN'), lambda rq, gq:(rq-gq)   , True ),
    ('eta'  , '#eta'        , ''      , (1000,-4.,   4.), (1000,-.2  ,.2  ), lambda gm:gm.eta                 , lambda muon:muon.eta             , lambda rq, gq:(rq-gq)   , True ),
    ('qm'   , 'charge match', ''      , (2   , 0.,   2.), None             , lambda r, g: r.charge == g.charge, None                             , None                    , None ),
)
QUANTITIES = {}
for VAL in VALUES:
    QUANTITIES[VAL[0]] = dict(zip(HEADERS, VAL[1:]))

FULLMUONLIST      = ('DSA', 'RSA', 'REF', 'DSADim')
RECOMUONLIST      = ('DSA', 'RSA', 'DSADim')
SHORTRECOMUONLIST = ('DSA', 'RSA')
REFMUONLIST       = ('REF',)

Q2LIST = ('pT', 'Lxy', 'd0', 'qm')

def HTITLE(Q, MUON, MODE, Q2=None):
    # PString and DenString are for conditionally controlling () and / in eff. title
    PString   = '' if QUANTITIES[Q]['ISDIF'] else '('
    DenString = QUANTITIES[Q]['EXTRA'] if QUANTITIES[Q]['ISDIF'] else ') / gen {P}'
    ResString = PString+'{M} {P} #minus gen {P}'+DenString
    if MODE == 'Res':
        # X = <q> Resolution/Dif
        fstring = ';'+ResString+';Counts'
    elif MODE == 'VS':
        # X = gen <q> ; Y = reco <q>
        fstring = ';gen {X};{M} {X};Counts'
    elif MODE== 'VSRes':
        # X = gen <q2> ; Y = <q> Resolution/Dif
        fstring = ';gen {X2};'+ResString+';Counts'
    return fstring.format(
        X =QUANTITIES[Q]['PRETTY']+QUANTITIES[Q]['EXTRA'],
        M =MUON,
        P =QUANTITIES[Q]['PRETTY'],
        X2=None if Q2 is None else QUANTITIES[Q2]['PRETTY']+QUANTITIES[Q2]['EXTRA']
    )

# every Q gets a Q Res plot and a reco Q vs gen Q plot except:
#  - any QM (because QM is not a real number)
#  - DSA, RSA Lxy (because Lxy is undefined for individual muons)
# every Q gets paired with every other Q (Q2) for a Q Res vs gen Q2 plot
HCONFIG = {}
for MUON in FULLMUONLIST:
    for Q in QUANTITIES:
        if Q == 'qm': continue
        if Q == 'Lxy' and MUON in RECOMUONLIST: continue
        if True:
            HCONFIG['{M}_{Q}Res'      .format(M=MUON, Q=Q       )] = {'TITLE':HTITLE(Q, MUON, 'Res'      ), 'AXES':QUANTITIES[Q] ['RESAXES']                         }
            HCONFIG['{M}_{Q}VS{Q}'    .format(M=MUON, Q=Q       )] = {'TITLE':HTITLE(Q, MUON, 'VS'       ), 'AXES':QUANTITIES[Q] ['AXES'   ]+QUANTITIES[Q]['AXES'   ]}
        for Q2 in Q2LIST:
            HCONFIG['{M}_{Q}ResVS{Q2}'.format(M=MUON, Q=Q, Q2=Q2)] = {'TITLE':HTITLE(Q, MUON, 'VSRes', Q2), 'AXES':QUANTITIES[Q2]['AXES'   ]+QUANTITIES[Q]['RESAXES']}

#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    for KEY in HCONFIG:
        self.HistInit(KEY, HCONFIG[KEY]['TITLE'], *HCONFIG[KEY]['AXES'])

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    if self.SP is None:
        raise Exception('[ANALYZER ERROR]: This script runs on signal only.')
    if self.TRIGGER:
        if not Selections.passedTrigger(E): return
    if '4Mu' in self.NAME:
        mu11, mu12, mu21, mu22, X1, X2, H, P, extramu = E.getPrimitives('GEN')
        genMuons = (mu11, mu12, mu21, mu22)
        genMuonPairs = ((mu11, mu12), (mu21, mu22))
    elif '2Mu2J' in self.NAME:
        mu1, mu2, j1, j2, X, XP, H, P, extramu = E.getPrimitives('GEN')
        genMuons = (mu1, mu2)
        genMuonPairs = ((mu1, mu2),)
    Event    = E.getPrimitives('EVENT'  )
    DSAmuons = E.getPrimitives('DSAMUON')
    RSAmuons = E.getPrimitives('RSAMUON')
    Dimuons  = E.getPrimitives('DIMUON' )

    ALL = True if 'All' in self.CUTS else False
    # require dimuons and muons to pass all selections
    if ALL:
        DSASelections    = [Selections.MuonSelection  (muon)   for muon   in DSAmuons]
        RSASelections    = [Selections.MuonSelection  (muon)   for muon   in RSAmuons]
        DimuonSelections = [Selections.DimuonSelection(dimuon) for dimuon in Dimuons ]

        selectedDSAmuons = [mu  for idx,mu  in enumerate(DSAmuons) if DSASelections   [idx]]
        selectedRSAmuons = [mu  for idx,mu  in enumerate(RSAmuons) if RSASelections   [idx]]
        selectedDimuons  = [dim for idx,dim in enumerate(Dimuons ) if DimuonSelections[idx] and DSASelections[dim.idx1] and DSASelections[dim.idx2]]

    # don't require dimuons and muons to pass all selections
    else:
        selectedDSAmuons = DSAmuons
        selectedRSAmuons = RSAmuons
        selectedDimuons  = Dimuons

    for genMuonPair in genMuonPairs:
        # no acceptance selection for now
        # genMuonSelection = Selections.AcceptanceSelection(genMuonPair)
        # if not genMuonSelection: continue

        # genMuonMatches are a dictionary of the return tuple of length 3
        # DSA and RSA get a doDimuons=False argument so that no dimuon matching will be done
        genMuonMatches = {'DSA':None, 'RSA':None, 'REF':None}
        for MUON, recoMuons in zip(SHORTRECOMUONLIST, (selectedDSAmuons, selectedRSAmuons)):
            genMuonMatches[MUON] = matchedDimuons(genMuonPair, selectedDimuons, recoMuons, vertex='BS', doDimuons=False)
        for MUON in REFMUONLIST:
            genMuonMatches[MUON] = matchedDimuons(genMuonPair, selectedDimuons)

        # now figure out the closest match, or None if they overlap
        # exitcode helps to make sure that both gen muons never match the same reco muon
        genMuonMatch = [{MUON:None for MUON in FULLMUONLIST}, {MUON:None for MUON in FULLMUONLIST}]
        for MUON in SHORTRECOMUONLIST:
            dimuonMatches, muonMatches, exitcode = genMuonMatches[MUON]
            genMuonMatch[0][MUON], genMuonMatch[1][MUON] = exitcode.getBestGenMuonMatches(muonMatches)

        fillDSADim = False

        # matched refitted muons if there was at least one dimuon
        for MUON in REFMUONLIST:
            dimuonMatches, muonMatches, exitcode = genMuonMatches['REF']
            if len(dimuonMatches) > 0:
                genMuonMatch[0]['REF'] = muonMatches[0][0]
                genMuonMatch[1]['REF'] = muonMatches[1][0]

                # when there's a dimuon match, pick out the original DSA muons
                # muonMatches[whichGenMuon][0=closest] is a dictionary with oidx as a field
                # This is the position in DSAmuons (NOT selectedDSAmuons!), so we can get the original DSA muon from that
                fillDSADim = True
                genMuonMatch[0]['DSADim'] = {'muon':DSAmuons[muonMatches[0][0]['oidx']]}
                genMuonMatch[1]['DSADim'] = {'muon':DSAmuons[muonMatches[1][0]['oidx']]}

        # loop over muon types, over quantities, compute the quantities, fill
        for MUON in FULLMUONLIST:
            # DSADim is only filled when REF is
            if MUON == 'DSADim' and not fillDSADim: continue
            for Q in QUANTITIES:
                if Q == 'qm': continue
                if Q == 'Lxy' and MUON in RECOMUONLIST: continue

                # gen, reco, and res functions
                GF   = QUANTITIES[Q]['GENLAMBDA' ]
                RF   = QUANTITIES[Q]['RECOLAMBDA']
                RESF = QUANTITIES[Q]['RESLAMBDA' ]

                # gen, reco, res, and gen2 quantities
                # if the code below succeeds, these should all be lists of length 2
                # corresponding to g0 and g1 exactly
                # gq2[0] will additionally be a dictionary storing the q2 values
                GQ   = []
                RQ   = []
                RESQ = []
                GQ2  = [{}, {}]

                # loop over gen muons individually
                # if there was a match
                # if this is a muon quantity use the closest muon
                # if this is a dimuon quantity (e.g. Lxy) use the dimuon
                # compute the gen, reco, and res quantities
                # loop over Q2, get the function, apply it
                # if Q2 is QM, need recoMuon to be passed to it
                for which, genMuon in enumerate(genMuonPair):
                    # in case we decide later that Lxy should only be filled once
                    # make sure the logic for QM below this loop is changed as well
                    # if Q == 'Lxy' and which == 1: continue

                    # handle gen pT and eta quantity in a somewhat unnatural way
                    if Q in ('pT','eta') and MUON in RECOMUONLIST:
                        genObj = genMuon.BS
                    else:
                        genObj = genMuon

                    if genMuonMatch[which][MUON] is not None:
                        # 'dim' does not exist for DSADim, but this shouldn't matter
                        # because Lxy is skipped for DSADim anyway
                        if Q == 'Lxy':
                            recoObj  = genMuonMatches[MUON][0][0]['dim']
                            recoMuon = genMuonMatch[which][MUON]['muon']
                        else:
                            recoObj  = genMuonMatch[which][MUON]['muon']
                            recoMuon = genMuonMatch[which][MUON]['muon']
                        GQ.append(GF(genObj ))
                        RQ.append(RF(recoObj))
                        # in a few pathological cases, REF matches to genSV, but
                        # when we try to compute the res for the corresponding DSA wrt genBS
                        # the genBS quantity is 0. Set the res to inf in these cases.
                        try:
                            RESQ.append(RESF(RF(recoObj), GF(genObj)))
                        except:
                            print 'Haha {} {} {} in {} {} {} {}, you\'re not crashing me! {} = inf'.format(Event.run, Event.lumi, Event.event, '4Mu' if '4Mu' in self.NAME else '2Mu2J', self.SP.mH, self.SP.mX, self.SP.cTau, GF(genObj))
                            RESQ.append(float('inf'                 ))
                        for Q2 in Q2LIST:
                            G2F = QUANTITIES[Q2]['GENLAMBDA']
                            if Q2 != 'qm':
                                # again, handle gen pT and eta quantity in a somewhat unnatural way
                                if Q2 in ('pT','eta') and MUON in RECOMUONLIST:
                                    GQ2[which][Q2] = G2F(genMuon.BS)
                                else:
                                    GQ2[which][Q2] = G2F(genMuon)
                            else:
                                GQ2[which][Q2] = G2F(recoMuon, genMuon)
                    else:
                        GQ  .append(None)
                        RQ  .append(None)
                        RESQ.append(None)
                        for Q2 in Q2LIST:
                            GQ2[which][Q2] = None

                # for QM, define for Lxy as the && of the two. This will result in either True, False, or None
                if Q == 'Lxy':
                    realChargeMatchBool = GQ2[0]['qm'] and GQ2[1]['qm']
                    GQ2[0]['qm'], GQ2[1]['qm'] = realChargeMatchBool, realChargeMatchBool

                # now all the quantities are computed (or are None). this loop of is length 2, one for each gen muon
                for which, (gq, rq, resq, gq2) in enumerate(zip(GQ, RQ, RESQ, GQ2)):
                    if True:
                        if resq is not None:
                            self.HISTS['{M}_{Q}Res'      .format(M=MUON, Q=Q       )].Fill(resq        )
                        if gq is not None and rq is not None:
                            self.HISTS['{M}_{Q}VS{Q}'    .format(M=MUON, Q=Q       )].Fill(gq, rq      )
                    for Q2 in gq2:
                        gq2val = gq2[Q2]
                        if gq2val is not None:
                            self.HISTS['{M}_{Q}ResVS{Q2}'.format(M=MUON, Q=Q, Q2=Q2)].Fill(gq2val, resq)

#### RUN ANALYSIS ####
if __name__ == '__main__':
    ARGS = Analyzer.PARSER.parse_args()
    Analyzer.setSample(ARGS)
    for METHOD in ('declareHistograms', 'analyze'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('GEN', 'DSAMUON', 'RSAMUON', 'DIMUON', 'TRIGGER', 'EVENT'),
    )
    analyzer.writeHistograms('roots/SignalRecoResPlots{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else ''))
