import math
import itertools
import operator
import numpy as np
import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Analysis.Primitives as Primitives
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons

# toggle the creation of histograms related to turn-on curves
DO_CREATE_SIMPLE_HISTS = True
DO_CREATE_RESOLUTION_HISTS = True
DO_CREATE_TURNON_HISTS = True

# this will be used as a fallback if the option --HLTfilter is NOT explicitly given
accepted_HLTpaths_fallback = ["HLT_L2Mu10_NoVertex_pp"]

# define single muon cuts
SINGLEMU_SELECTION = {
    "nStations": Selections.Cut(
        "nStations", lambda muon: muon.nDTStations + muon.nCSCStations, operator.gt, 1
    ),
    "nCSCDTHits": Selections.Cut(
        "nCSCDTHits", lambda muon: muon.nCSCHits + muon.nDTHits, operator.gt, 12
    ),
    "pTSig": Selections.Cut(
        "pTSig", lambda muon: muon.ptError / muon.pt, operator.lt, 1.0
    ),
    # 'pT': Selections.Cut('pT',
    #     lambda muon: muon.pt,
    #     operator.gt, 20.),
    "eta": Selections.Cut("eta", lambda muon: abs(muon.eta), operator.lt, 1.2),
}

# define muon pair cuts
MUONPAIR_SELECTION = {
    # "alpha": Selections.Cut(
    #     "alpha", lambda (m1, m2): m1.p4.Angle(m2.p4.Vect()), operator.gt, 2.9
    # )
}

# define dimuon cuts
DIMUON_SELECTION = {
    # 'vtxChiSqu': Selections.Cut('vtxChiSqu',
    #     lambda dim: dim.normChi2,
    #     operator.lt, 50.),
}

# pT cuts applied to muon pairs ("L1 seed emulation"):
# (the first muon has to pass the first cut and the second muon has to pass the
# second cut) OR (the first muon has to pass the second cut and the second muon
# has to pass the first cut)
L1_pairthresholds = (0.0, 0.0)

DO_SELECT_LARGEST_ALPHA_PAIR = False
DO_REQUIRE_OPPOSITE_HEMISPHERES = False
DO_REQUIRE_ONE_LEG_MATCHED = True
DO_REQUIRE_BOTH_LEGS_MATCHED = False
DO_REQUIRE_DIMUON_VERTEX = False

# deltaR matching threshold for reco-HLT matches
MATCHING_THRESHOLD_HLT = 0.2

# L2 pT threshold values for matched HLT objects, applied to the turn-on curves
L2THRESHOLDS = [23.0, 25.0, 28.0]

# additional L1 pT cuts applied consecutively to the sets of turn-on curves
L1THRESHOLDS = (0.0, 4.0, 5.0, 7.0, 11.0, 12.0, 15.0)

# different dimuon populations, defined by their alpha(mu,mu) values
# define tuples of (min,max,name), corresponding to min<alpha<max and the name
# tag for the corresponding histograms.
# "(None,None,'')" is the alpha-inclusive case.
ALPHA_CATEGORIES = (
    (None, None, ""),
    # (2.8, math.pi, "__2p8alphaPi"),
    # (2.8, math.pi, "__SSpairs_2p8alphaPi"),
    # (2.8, math.pi, "__goodQuality_2p8alphaPi"),
    # (0.3, 2.8, "__0p3alpha2p8"),
    # (0., 0.3, "__0p0alpha0p3"),
    # (0., 2.8, "__noOppositeMuonMatch_0p0alpha2p8"),
)

# list of d0 intervals to process, "(None, None)" gives the d0-inclusive results
D0INTERVALS = [(None, None)]
# 2.5-cm steps for small d0
# D0INTERVALS += ([(i,i+2.5) for i in np.arange(0., 30., 2.5)])
# 5-cm steps for small d0
# D0INTERVALS += ([(i,i+5.0) for i in np.arange(0., 30., 5.)])
# 10-cm steps for the entire d0 range
# D0INTERVALS += ([(i,i+10.) for i in np.arange(0., 500., 10.)])
# custom d0 bins
# D0INTERVALS += [(0, 5), (5, 10), (10, 15), (15, 20), (20, 25), (25, 30)]
D0INTERVALS += [
    (0, 10),
    (10, 50),
    (0, 50),
    (50, 100),
    (100, 150),
    (150, 250),
    (250, 350),
    (250, 1000),
    (350, 1000),
]

# make sure that all of the values are actually floats
D0INTERVALS = [
    (float(l), float(h)) if l is not None and h is not None else (l, h)
    for l, h in D0INTERVALS
]

SINGLEMUVARIABLES = [
    "pT",
    "eta",
    "phi",
    "charge",
    "d0",
    "x_fhit",
    "y_fhit",
    "z_fhit",
    "nStations",
    "nCSCDTHits",
    "pTSig",
    "chi2",
]
PAIRVARIABLES = [
    "pTdiff",
    "deltaR",
    "mass",
    "cosAlpha",
    "alpha",
    "dimuonPTOverM",
    "pairPT",
    "chargeprod",
    "dNStations",
    "dNCSCDTHits",
    "dEta",
    "dPhi",
    "dD0",
    "dChi2",
]
DIMUONVARIABLES = ["dimLxy", "dimMass", "dimVtxChi2", "dimCosAlpha", "dimLxySig"]
L1RESOLUTIONVARIABLES = ["L1pTres"]
L2RESOLUTIONVARIABLES = ["L2pTres"]

HEADERS = ("XTITLE", "AXES", "LAMBDA", "PRETTY")
VALUES = (
    ("pT", "p_{T} [GeV]", (1000, 0.0, 500.0), lambda muon: muon.pt, "p_{T}"),
    ("eta", "#eta", (1000, -3.0, 3.0), lambda muon: muon.eta, "#eta"),
    ("phi", "#phi", (1000, -math.pi, math.pi), lambda muon: muon.phi, "#phi"),
    # ("charge", "q(#mu)", (4, -2, 2), lambda muon: muon.charge, "q(#mu)"),
    ("d0", "d_{0} [cm]", (1000, 0.0, 1100.0), lambda muon: abs(muon.d0()), "d_{0}"),
    # (
    #     "x_fhit",
    #     "x_{innermost hit}",
    #     (1000, -800.0, 800.0),
    #     lambda muon: muon.x_fhit,
    #     "x_{innermost hit}",
    # ),
    # (
    #     "y_fhit",
    #     "y_{innermost hit}",
    #     (1000, -800.0, 800.0),
    #     lambda muon: muon.y_fhit,
    #     "y_{innermost hit}",
    # ),
    # (
    #     "z_fhit",
    #     "z_{innermost hit}",
    #     (1000, -1100.0, 1100.0),
    #     lambda muon: muon.z_fhit,
    #     "z_{innermost hit}",
    # ),
    (
        "chi2",
        "muon #chi^{2}/ndof",
        (1000, -1.0, 100.0),
        lambda muon: muon.chi2 / muon.ndof if muon.ndof != 0 else -1.0,
        "muon #chi^{2}/ndof",
    ),
    (
        "nStations",
        "nStations",
        (20, 0.0, 20.0),
        lambda muon: muon.nDTStations + muon.nCSCStations,
        "nStations",
    ),
    (
        "nCSCDTHits",
        "nCSC+DTHits",
        (100, 0.0, 100.0),
        lambda muon: muon.nCSCHits + muon.nDTHits,
        "nCSC+DTHits",
    ),
    (
        "pTSig",
        "#sigma_{p_{T}} / p_{T}",
        (1000, 0.0, 10.0),
        lambda muon: muon.ptError / muon.pt,
        "#sigma_{p_{T}} / p_{T}",
    ),
    # (
    #     "pTdiff",
    #     "(p_{T}^{upper}-p_{T}^{lower})/p_{T}^{lower}",
    #     (1000, -10.0, 100.0),
    #     lambda (m1, m2): (m1.pt - m2.pt) / m2.pt,
    #     "p_{T}^{upper}-p_{T}^{lower}/p_{T}^{lower}",
    # ),
    (
        "deltaR",
        "#Delta R",
        (1000, 0.0, 5.0),
        lambda (m1, m2): m1.p4.DeltaR(m2.p4),
        "#DeltaR(#mu#mu)",
    ),
    (
        "mass",
        "M_{#mu#mu}",
        (1000, 0.0, 500.0),
        lambda (m1, m2): (m1.p4 + m2.p4).M(),
        "M(#mu#mu) [GeV]",
    ),
    (
        "cosAlpha",
        "cos#alpha",
        (1000, -1.0, 1.0),
        lambda (m1, m2): m1.p4.Vect().Dot(m2.p4.Vect()) / m1.p4.P() / m2.p4.P(),
        "cos(#alpha)",
    ),
    (
        "alpha",
        "#alpha",
        (1000, 0.0, math.pi),
        lambda (m1, m2): m1.p4.Angle(m2.p4.Vect()),
        "cos(#alpha)",
    ),
    # (
    #     "dimuonPTOverM",
    #     "dimuon p_{T} / M",
    #     (1000, 0.0, 20.0),
    #     lambda (m1, m2): (m1.p4 + m2.p4).Pt() / (m1.p4 + m2.p4).M(),
    #     "p_{T} / M",
    # ),
    # (
    #     "pairPT",
    #     "pair p_{T}",
    #     (1000, 0.0, 1000.0),
    #     lambda (m1, m2): (m1.p4 + m2.p4).Pt(),
    #     "pair p_{T}",
    # ),
    (
        "chargeprod",
        "q(#mu_{1})#times q(#mu_{2})",
        (4, -2.0, 2.0),
        lambda (m1, m2): m1.charge * m2.charge,
        "q(#mu_{1},#mu_{2})",
    ),
    # (
    #     "dNStations",
    #     "|nStations(#mu_{1}) - nStations(#mu_{2})|",
    #     (10, 0.0, 10.0),
    #     lambda (m1, m2): abs(
    #         m1.nDTStations + m1.nCSCStations - m2.nDTStations - m2.nCSCStations
    #     ),
    #     "|nStations(#mu_{1}) - nStations(#mu_{2})|",
    # ),
    # (
    #     "dNCSCDTHits",
    #     "|nCSC+DTHits(#mu_{1}) - nCSC+DTHits(#mu_{2})|",
    #     (50, 0.0, 50.0),
    #     lambda (m1, m2): abs(m1.nCSCHits + m1.nDTHits - m2.nCSCHits - m2.nDTHits),
    #     "|nCSC+DTHits(#mu_{1}) - nCSC+DTHits(#mu_{2})|",
    # ),
    # (
    #     "dEta",
    #     "|#eta(#mu_{1}) - #eta(#mu_{2})|",
    #     (1000, 0.0, 3.0),
    #     lambda (m1, m2): abs(m1.eta - m2.eta),
    #     "|#eta(#mu_{1}) - #eta(#mu_{2})|",
    # ),
    # (
    #     "dPhi",
    #     "|#phi(#mu_{1}) - #phi(#mu_{2})|",
    #     (1000, 0.0, 2 * math.pi),
    #     lambda (m1, m2): abs(m1.phi - m2.phi),
    #     "|#phi(#mu_{1}) - #phi(#mu_{2})|",
    # ),
    # (
    #     "dChi2",
    #     "|#chi^{2}/ndof(#mu_{1}) - #chi^{2}/ndof(#mu_{2})|",
    #     (1000, -1.0, 30.0),
    #     lambda (m1, m2): abs(m1.chi2 / m1.ndof - m2.chi2 / m2.ndof)
    #     if m1.ndof != 0 and m2.ndof != 0
    #     else -1.0,
    #     "|#chi^{2}(#mu_{1}) - #chi^{2}(#mu_{2})|",
    # ),
    (
        "dimLxy",
        "dim. L_{xy} [cm]",
        (1000, 0.0, 500.0),
        lambda dimuon: dimuon.Lxy(),
        "dim. L_{xy}",
    ),
    # (
    #     "dimMass",
    #     "dim. mass",
    #     (1000, 0.0, 500.0),
    #     lambda dimuon: (dimuon.mu1.p4 + dimuon.mu2.p4).M(),
    #     "dim. mass",
    # ),
    (
        "dimVtxChi2",
        "vertex #chi^{2}/dof",
        (1000, 0.0, 200.0),
        lambda dimuon: dimuon.normChi2,
        "vertex #chi^{2}/dof",
    ),
    (
        "dimCosAlpha",
        "dim. cos(#alpha)",
        (1000, -1.0, 1.0),
        lambda dimuon: dimuon.cosAlpha,
        "dim. cos(#alpha)",
    ),
    (
        "dimLxySig",
        "dim. L_{xy}/#sigma_{L_{xy}}",
        (1000, 0.0, 300.0),
        lambda dimuon: dimuon.LxySig(),
        "dim. L_{xy}/#sigma_{L_{xy}}",
    ),
    (
        "L1pTres",
        "(p_{T}^{L1}-p_{T}^{DSA})/p_{T}^{DSA}",
        (1000, -1.0, 20.0),
        lambda (dsamu, l1mu): (l1mu.pt - dsamu.pt) / dsamu.pt,
        "(p_{T}^{L1}-p_{T}^{DSA})/p_{T}^{DSA}",
    ),
    (
        "L2pTres",
        "(p_{T}^{L2}-p_{T}^{DSA})/p_{T}^{DSA}",
        (1000, -1.0, 20.0),
        lambda (dsamu, l2mu): (l2mu.pt - dsamu.pt) / dsamu.pt,
        "(p_{T}^{L2}-p_{T}^{DSA})/p_{T}^{DSA}",
    ),
)
CONFIG = {}
for VAL in VALUES:
    KEY, VALS = VAL[0], VAL[1:]
    CONFIG[KEY] = dict(zip(HEADERS, VALS))


###############################################################################
# some consistency checks

if DO_REQUIRE_BOTH_LEGS_MATCHED and not DO_REQUIRE_ONE_LEG_MATCHED:
    raise Exception(
        "If DO_REQUIRE_BOTH_LEGS_MATCHED should be True, also "
        "DO_REQUIRE_ONE_LEG_MATCHED has to be True"
    )

if (
    any([threshold > 0.0 for threshold in L1_pairthresholds])
    and not DO_REQUIRE_BOTH_LEGS_MATCHED
):
    raise Exception(
        "If L1 pair thresholds are >0, both legs must be required to match a L2 muon"
    )

if len(L1_pairthresholds) != 2:
    raise Exception("'L1_pairthresholds' must hold exactly two values")


# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):

    # # Define strings that identify different bins and categories. Histograms will be
    # # created for all combinations of them.
    d0intervals, alpha_categories = parseIdentifiers(
        D0INTERVALS, [a for __, __, a in ALPHA_CATEGORIES]
    )

    # initialize histograms for all combinations of the above categories/intervals
    for d0intervals_str in d0intervals:
        for alpha_categories_str in alpha_categories:

            identifier = d0intervals_str + alpha_categories_str

            self.HistInit(
                "cutFlow" + identifier,
                ";applied cuts; number of passing events",
                30,
                0,
                30,
            )
            self.HistInit(
                "L1TObjectsPerHLTObject_noSelections" + identifier,
                ";number of L1 objects per HLT muon;Yield",
                40,
                0,
                10,
            )
            self.HistInit(
                "L1TObjectsPerHLTObject" + identifier,
                ";number of L1 objects per HLT muon;Yield",
                40,
                0,
                10,
            )
            self.HistInit(
                "DSAmuonMultiplicity_noSelections" + identifier,
                ";DSA muon multiplicity (no selection);Yield",
                29,
                1,
                30,
            )
            self.HistInit(
                "DSAmuonMultiplicity" + identifier,
                ";DSA muon multiplicity (selected muons);Yield",
                29,
                1,
                30,
            )
            self.HistInit(
                "dimuonMultiplicity" + identifier, ";dimuon multiplicity;Yield", 10, 0, 10
            )

            if DO_CREATE_SIMPLE_HISTS:
                # define a list of histogram name templates

                # define histograms for single muon variables
                HISTNAME_TEMPLATES_SIMPLE_SINGLEMUVARIABLES = []

                # make histograms for lower, upper and for both legs
                for leg in ("_lowerLeg", "_upperLeg", ""):
                    histname = "DSA{leg}__{{}}VAR{identifier}".format(
                        leg=leg, identifier=identifier
                    )
                    HISTNAME_TEMPLATES_SIMPLE_SINGLEMUVARIABLES.append(histname)

                    # for each leg, additionally distinguish between track charges
                    for charge in ("_posCharge", "_negCharge"):
                        histname = "DSA{leg}{charge}__{{}}VAR{identifier}".format(
                            leg=leg, charge=charge, identifier=identifier
                        )
                        HISTNAME_TEMPLATES_SIMPLE_SINGLEMUVARIABLES.append(histname)

                # define histograms for pair variables
                HISTNAME_TEMPLATES_SIMPLE_PAIRVARIABLES = []

                # in addition to the default case, distinguish between oppositely and
                # equally charged muon pairs
                for paircharge in ("_oppositeCharges", "_equalCharges", ""):
                    histname = "DSA{paircharge}__{{}}VAR{identifier}".format(
                        paircharge=paircharge, identifier=identifier
                    )
                    HISTNAME_TEMPLATES_SIMPLE_PAIRVARIABLES.append(histname)

                # define histograms for dimuon variables
                HISTNAME_TEMPLATES_SIMPLE_DIMUONVARIABLES = []
                histname = "DSA__{{}}VAR{identifier}".format(identifier=identifier)
                HISTNAME_TEMPLATES_SIMPLE_DIMUONVARIABLES.append(histname)

                # initialize the "simple" histograms
                for name in HISTNAME_TEMPLATES_SIMPLE_SINGLEMUVARIABLES:
                    for KEY in CONFIG:
                        if KEY not in SINGLEMUVARIABLES:
                            continue
                        BASETITLE = ";" + CONFIG[KEY]["XTITLE"] + ";DSA "
                        self.HistInit(
                            name.format(KEY), BASETITLE + "Yield", *CONFIG[KEY]["AXES"]
                        )

                for name in HISTNAME_TEMPLATES_SIMPLE_PAIRVARIABLES:
                    for KEY in CONFIG:
                        if KEY not in PAIRVARIABLES:
                            continue
                        BASETITLE = ";" + CONFIG[KEY]["XTITLE"] + ";DSA "
                        self.HistInit(
                            name.format(KEY), BASETITLE + "Yield", *CONFIG[KEY]["AXES"]
                        )

                for name in HISTNAME_TEMPLATES_SIMPLE_DIMUONVARIABLES:
                    for KEY in CONFIG:
                        if KEY not in DIMUONVARIABLES:
                            continue
                        BASETITLE = ";" + CONFIG[KEY]["XTITLE"] + ";DSA "
                        self.HistInit(
                            name.format(KEY), BASETITLE + "Yield", *CONFIG[KEY]["AXES"]
                        )

            # for KEY in CONFIG:
            #     BASETITLE = ";" + CONFIG[KEY]["XTITLE"] + ";DSA "
            #     for name in HISTNAME_TEMPLATES_SIMPLE_SINGLEMUVARIABLES:
            #         print("Initializing histograms: {}".format(name.format(KEY)))
            #         self.HistInit(name.format(KEY),
            #                 BASETITLE + "Yield",
            #                 *CONFIG[KEY]["AXES"])

            #     for name in HISTNAME_TEMPLATES_SIMPLE_PAIRVARIABLES:
            #         print("Initializing histograms: {}".format(name.format(KEY)))
            #         self.HistInit(name.format(KEY),
            #                 BASETITLE + "Yield",
            #                 *CONFIG[KEY]["AXES"])

            #     for name in HISTNAME_TEMPLATES_SIMPLE_DIMUONVARIABLES:
            #         print("Initializing histograms: {}".format(name.format(KEY)))
            #         self.HistInit(name.format(KEY),
            #                 BASETITLE + "Yield",
            #                 *CONFIG[KEY]["AXES"])

            if DO_CREATE_RESOLUTION_HISTS:
                # define a list of resolution histogram name templates
                HISTNAME_TEMPLATES_RESOLUTIONVARIABLES = []
                for leg in ("_lowerLeg", "_upperLeg"):
                    histname = "DSA{leg}__{{}}VAR{identifier}".format(
                        leg=leg, identifier=identifier
                    )
                    HISTNAME_TEMPLATES_RESOLUTIONVARIABLES.append(histname)

                # initialize the resolution histograms
                for name in HISTNAME_TEMPLATES_RESOLUTIONVARIABLES:
                    for KEY in CONFIG:
                        if (
                            KEY not in L2RESOLUTIONVARIABLES
                            and KEY not in L1RESOLUTIONVARIABLES
                        ):
                            continue
                        BASETITLE = ";" + CONFIG[KEY]["XTITLE"] + ";DSA "
                        self.HistInit(
                            name.format(KEY), BASETITLE + "Yield", *CONFIG[KEY]["AXES"]
                        )

            if DO_CREATE_TURNON_HISTS:
                # define a list of turn-on histogram name templates
                HISTNAME_TEMPLATES_TURNON = []
                for leg in ("_lowerLeg", "_upperLeg", ""):
                    histname = "DSA{leg}__{{}}VAREffDen{identifier}".format(
                        leg=leg, identifier=identifier
                    )

                    HISTNAME_TEMPLATES_TURNON.append(histname)

                    for L2threshold in L2THRESHOLDS:
                        for L1threshold in L1THRESHOLDS:
                            histname = "DSA{leg}_L2pTGT{L2threshold}_L1pTGT{L1threshold}__{{}}VAREffNum{identifier}".format(
                                leg=leg,
                                L2threshold=str(L2threshold).replace(".", "p"),
                                L1threshold=str(L1threshold).replace(".", "p"),
                                identifier=identifier,
                            )

                            HISTNAME_TEMPLATES_TURNON.append(histname)

                # initialize the turn-on histograms
                for KEY in CONFIG:
                    BASETITLE = ";" + CONFIG[KEY]["XTITLE"] + ";" + "DSA "
                    for name in HISTNAME_TEMPLATES_TURNON:
                        self.HistInit(
                            name.format(KEY),
                            BASETITLE + ("Efficiency" if "EffNum" in name else "Yield"),
                            *CONFIG[KEY]["AXES"]
                        )

    # summary of booked histograms
    print ("\n[ANALYZER INFO] Number of booked histograms: {}".format(len(self.HISTS)))


# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):

    event = E.getPrimitives("EVENT")

    # # enforce a custom set of runs/lumisections for a direct comparison of
    # # NoBPTX vs. Cosmics samples
    # custom_JSON = {
    #     # using the StoppedPtls_json_subset JSON
    #     276563: range(11, 35),
    #     276567: range(10, 61),
    #     276570: range(11, 91),
    #     276577: range(11, 176),
    #     276910: range(20, 180),
    #     276919: range(11, 39),
    #     276921: range(10, 29),
    #     276936: range(11, 90),

    #     # # using the CosmicJSON_E_D_firstClean
    #     # 276563: range(1, 35),
    #     # 276567: range(1, 62),
    #     # 276570: range(1, 99),
    #     # 276577: range(1, 177),
    #     # 276910: range(20, 188),
    #     # 276919: range(1, 47),
    #     # 276921: range(1, 34),
    #     # 276936: range(1, 91) + range(161, 176),

    #     # # using the CosmicJSON_E_D_UGMT_base_and_bottomOnly JSON
    #     # 276336: range(10,27),
    #     # 276337: range(10,91),
    #     # 276459: range(11,109),
    #     # 276467: range(11,61),
    #     # 276529: range(10,51),
    #     # 276563: range(1, 35),
    #     # 276567: range(1, 62),
    #     # 276568: range(12,31),
    #     # 276570: range(1, 99),
    #     # 276577: range(1, 177),
    #     # 276735: range(11,60),
    #     # 276758: range(11,177),
    #     # 276872: range(11,27),
    #     # 276910: range(20, 188),
    #     # 276919: range(1, 47),
    #     # 276921: range(1, 34),
    #     # 276936: range(1, 91) + range(161, 176),
    # }
    # if event.run not in custom_JSON.keys(): return
    # # if event.lumi not in custom_JSON[event.run]: return

    HLTpaths, HLTmuons, L1Tmuons = E.getPrimitives("TRIGGER")
    DSAmuons = E.getPrimitives("DSAMUON")
    DIMUONS3 = E.getPrimitives("DIMUON")
    # restore "old" (pre-January-2019) dimuon behavior
    DIMUONS = [dim for dim in DIMUONS3 if dim.composition == "DSA"]

    # override HLT path filter if the option has been passed
    if ARGS.HLTFILTER is not None:
        accepted_HLTpaths = [ARGS.HLTFILTER]
    else:
        accepted_HLTpaths = accepted_HLTpaths_fallback

    d0intervals, alpha_categories = parseIdentifiers(
        D0INTERVALS, [a for __, __, a in ALPHA_CATEGORIES]
    )

    for d0minmax, d0intervals_str in zip(D0INTERVALS, d0intervals):
        d0min = d0minmax[0]
        d0max = d0minmax[1]

        for alpha_minmaxname, alpha_category_str in zip(
            ALPHA_CATEGORIES, alpha_categories
        ):
            alpha_min = alpha_minmaxname[0]
            alpha_max = alpha_minmaxname[1]

            identifier = d0intervals_str + alpha_category_str

            # count DSA muons before any selections
            self.HISTS["DSAmuonMultiplicity_noSelections" + identifier].Fill(
                len(DSAmuons)
            )

            # count events without any selections
            self.HISTS["cutFlow" + identifier].Fill(0)

            do_skip_event = False

            # Accept only events that pass the following HLT triggers
            HLTpaths_list = [path.name for path in HLTpaths]
            if not any(
                [
                    any(
                        [
                            (accepted_path in HLTpath)
                            for accepted_path in accepted_HLTpaths
                        ]
                    )
                    for HLTpath in HLTpaths_list
                ]
            ):
                do_skip_event = True

            if do_skip_event:
                return
            else:
                # count events that pass the HLT paths filter
                self.HISTS["cutFlow" + identifier].Fill(1)

            # count L1 objects per HLT object
            for HLTmuon in HLTmuons:
                nL1Tmuons = len([m for m in L1Tmuons if m.idx == HLTmuon.idx])
                self.HISTS["L1TObjectsPerHLTObject_noSelections" + identifier].Fill(
                    nL1Tmuons
                )

            # discard events with too few DSA muons
            if len(DSAmuons) < 2:
                continue
            else:
                # count events with at least two DSA muons
                self.HISTS["cutFlow" + identifier].Fill(2)

            accepted_DSAmuons = []
            accepted_DSAmuons_HLTmatched = []
            accepted_HLTmuons = []

            # check if there are any HLT-matched muons in the event (but do
            # nothing else at the moment - everything else will be taken
            # care of later on)
            cnt_DSAmuons_HLTmatched = 0
            for muon in DSAmuons:
                muonMatches = matchedMuons(
                    muon, HLTmuons, threshold=MATCHING_THRESHOLD_HLT
                )
                if len(muonMatches) > 0:
                    self.HISTS["cutFlow" + identifier].Fill(3)
                    break

            for muon in DSAmuons:
                # count all muons in the events that have been selected so far
                self.HISTS["cutFlow" + identifier].Fill(4)

                # apply single muon cuts
                do_skip_muon = False
                for var in SINGLEMU_SELECTION.keys():
                    if not SINGLEMU_SELECTION[var].apply(muon):
                        do_skip_muon = True

                # apply additional d0 cuts
                if d0min is not None and d0max is not None:
                    if not (d0min <= abs(muon.d0()) < d0max):
                        do_skip_muon = True

                if do_skip_muon:
                    continue
                else:
                    # count muons remaining after single muon cuts
                    self.HISTS["cutFlow" + identifier].Fill(5)

                # store muon
                accepted_DSAmuons.append(muon)

                # store muon if HLT-matched
                muonMatches = matchedMuons(
                    muon, HLTmuons, threshold=MATCHING_THRESHOLD_HLT
                )
                if len(muonMatches) > 0:
                    accepted_DSAmuons_HLTmatched.append(muon)
                    accepted_HLTmuons.append(muonMatches[0]["muon"])

            # skip event if there are no HLT-matched muons at all
            if len(accepted_DSAmuons_HLTmatched) == 0:
                continue
            else:
                # count events with at least one HLT matched muons
                self.HISTS["cutFlow" + identifier].Fill(6)

            temp_maxalpha = -1
            selected_muonpairs = []
            selected_muonpairs_HLTmatched = None

            for m1, m2 in list(itertools.combinations(accepted_DSAmuons, 2)):
                # count all muon pairs that have passed all selections so far
                self.HISTS["cutFlow" + identifier].Fill(7)

                if DO_REQUIRE_ONE_LEG_MATCHED:
                    # require at least one muon to match an HLT object
                    if all([m not in accepted_DSAmuons_HLTmatched for m in (m1, m2)]):
                        continue
                    else:
                        # count all muon pairs with >=1 HLT-matched leg
                        self.HISTS["cutFlow" + identifier].Fill(8)

                if DO_REQUIRE_OPPOSITE_HEMISPHERES:
                    # require muons to be in different detector hemispheres
                    if ([hemisphere(m1), hemisphere(m2)]).count("lower") != 1:
                        continue
                    else:
                        # count muon pairs with legs in different hemispheres
                        self.HISTS["cutFlow" + identifier].Fill(9)

                if DO_SELECT_LARGEST_ALPHA_PAIR:
                    # find the muon with the largest alpha(mu,mu)
                    temp_alpha = CONFIG["alpha"]["LAMBDA"]((m1, m2))
                    if temp_alpha > temp_maxalpha:
                        if alpha_min is not None and alpha_max is not None:
                            # apply simple alpha cuts here, if applicable
                            # treatment of some special cases for certain
                            # alpha bins will be done further below
                            if alpha_min < temp_alpha < alpha_max:
                                temp_maxalpha = temp_alpha
                                selected_muonpairs = [(m1, m2)]

                        else:
                            temp_maxalpha = temp_alpha
                            selected_muonpairs = [(m1, m2)]

                else:
                    if alpha_min is not None and alpha_max is not None:
                        # apply simple alpha cuts here, if applicable
                        # treatment of some special cases for certain
                        # alpha bins will be done further below
                        if alpha_min < CONFIG["alpha"]["LAMBDA"]((m1, m2)) < alpha_max:
                            selected_muonpairs.append((m1, m2))

                    else:
                        selected_muonpairs.append((m1, m2))

            # skip events without any selected muon pairs
            if len(selected_muonpairs) == 0:
                continue
            else:
                # count events with >=1 selected muon pair
                self.HISTS["cutFlow" + identifier].Fill(10)

            # store the next subset of muon pairs which pass further pair selections
            buffer_selected_muonpairs = []
            buffer_selected_muonpairs_HLTmatched = []

            for m1, m2 in selected_muonpairs:
                # count all muons selected so far
                self.HISTS["cutFlow" + identifier].Fill(11)

                # apply muon par cuts
                do_skip_muonpair = False
                for var in MUONPAIR_SELECTION.keys():
                    if not MUONPAIR_SELECTION[var].apply((m1, m2)):
                        do_skip_muonpair = True

                if do_skip_muonpair:
                    continue
                else:
                    # count muon pairs that pass the muon pairs selection
                    self.HISTS["cutFlow" + identifier].Fill(12)

                do_skip_muonpair = False
                if DO_REQUIRE_BOTH_LEGS_MATCHED:
                    # require both DSA muon to match HLT objects
                    muonMatches_m1 = matchedMuons(
                        m1, HLTmuons, threshold=MATCHING_THRESHOLD_HLT
                    )
                    muonMatches_m2 = matchedMuons(
                        m2, HLTmuons, threshold=MATCHING_THRESHOLD_HLT
                    )
                    if not (len(muonMatches_m1) > 0 and len(muonMatches_m2) > 0):
                        do_skip_muonpair = True

                    # require matches to different HLT objects
                    if (
                        len(muonMatches_m1) > 0
                        and len(muonMatches_m2) > 0
                        and muonMatches_m1[0]["muon"] == muonMatches_m2[0]["muon"]
                    ):
                        do_skip_muonpair = True

                if do_skip_muonpair:
                    continue
                else:
                    # count muon pairs that have HLT matches for both legs
                    self.HISTS["cutFlow" + identifier].Fill(13)

                # store all muon pairs that have passed the selections
                buffer_selected_muonpairs.append((m1, m2))
                if DO_REQUIRE_BOTH_LEGS_MATCHED:
                    buffer_selected_muonpairs_HLTmatched.append(
                        (muonMatches_m1[0]["muon"], muonMatches_m2[0]["muon"])
                    )

            selected_muonpairs = buffer_selected_muonpairs
            selected_muonpairs_HLTmatched = buffer_selected_muonpairs_HLTmatched

            # count the number of L1T objects per HLT muon for all HLT muons in the event
            for HLTmuon in HLTmuons:
                cnt_L1Tmuons = len([m for m in L1Tmuons if m.idx == HLTmuon.idx])
                self.HISTS["L1TObjectsPerHLTObject" + identifier].Fill(cnt_L1Tmuons)

            dimuon_multiplicity = 0
            accepted_muons_finalSelection = []
            cnt_position_muonpairs = -1

            for m1, m2 in selected_muonpairs:
                # count all muon pairs selected so far
                self.HISTS["cutFlow" + identifier].Fill(14)
                cnt_position_muonpairs += 1

                # apply pT cuts on L1 muon pairs ("L1 seed emulation") of both legs
                # are required to match HLT objects
                if DO_REQUIRE_BOTH_LEGS_MATCHED:
                    m1_passes_first_cut = any(
                        [
                            mu.pt >= L1_pairthresholds[0]
                            for mu in L1Tmuons
                            if mu.idx
                            == selected_muonpairs_HLTmatched[cnt_position_muonpairs][
                                0
                            ].idx
                        ]
                    )
                    m1_passes_second_cut = any(
                        [
                            mu.pt >= L1_pairthresholds[1]
                            for mu in L1Tmuons
                            if mu.idx
                            == selected_muonpairs_HLTmatched[cnt_position_muonpairs][
                                0
                            ].idx
                        ]
                    )
                    m2_passes_first_cut = any(
                        [
                            mu.pt >= L1_pairthresholds[0]
                            for mu in L1Tmuons
                            if mu.idx
                            == selected_muonpairs_HLTmatched[cnt_position_muonpairs][
                                1
                            ].idx
                        ]
                    )
                    m2_passes_second_cut = any(
                        [
                            mu.pt >= L1_pairthresholds[1]
                            for mu in L1Tmuons
                            if mu.idx
                            == selected_muonpairs_HLTmatched[cnt_position_muonpairs][
                                1
                            ].idx
                        ]
                    )

                    if not (m1_passes_first_cut and m2_passes_second_cut) and not (
                        m1_passes_second_cut and m2_passes_first_cut
                    ):
                        continue
                    else:
                        # count all muon pars that pass the L1 trigger cuts
                        self.HISTS["cutFlow" + identifier].Fill(15)

                # check whether the selected two muons belong to a dimuon (i.e, have
                # a dimuon vertex
                for dimuon in DIMUONS:
                    if (
                        dimuon.idx1 == m1.idx
                        and dimuon.idx2 == m2.idx
                        or dimuon.idx1 == m2.idx
                        and dimuon.idx2 == m1.idx
                    ):
                        is_dimuon = True
                        selected_dimuon = dimuon

                        # count selected dimuons
                        self.HISTS["cutFlow" + identifier].Fill(16)
                        break
                else:
                    is_dimuon = False
                    selected_dimuon = None

                if DO_REQUIRE_DIMUON_VERTEX and not is_dimuon:
                    continue

                # apply dimuon cuts
                do_skip_dimuon = False
                if DO_REQUIRE_DIMUON_VERTEX:
                    for var in DIMUON_SELECTION.keys():
                        if not DIMUON_SELECTION[var].apply(selected_dimuon):
                            do_skip_dimuon = True

                if do_skip_dimuon:
                    continue
                else:
                    # count dimuons passing the dimuon selection
                    self.HISTS["cutFlow" + identifier].Fill(17)

                # special treatment of some alpha categories
                if (
                    "noOppositeMuonMatch" in alpha_category_str
                    and not DO_SELECT_LARGEST_ALPHA_PAIR
                ):

                    do_skip_muonpair_duplicate = False
                    # remove those dimuons which have a back-to-back muon
                    # in the same event for at least one of their muons
                    othermuons = [
                        (om1, om2)
                        for om1, om2 in selected_muonpairs
                        if (om1, om2) != (m1, m2)
                    ]
                    for thismuon in (m1, m2):
                        alphas_with_othermuons = [
                            CONFIG["alpha"]["LAMBDA"]((thismuon, othermuon))
                            for othermuon, __ in othermuons
                        ]
                        alphas_with_othermuons += [
                            CONFIG["alpha"]["LAMBDA"]((thismuon, othermuon))
                            for __, othermuon in othermuons
                        ]

                    if not any([a > 2.8 for a in alphas_with_othermuons]):
                        do_skip_muonpair_duplicate = True

                    if do_skip_muonpair_duplicate:
                        continue
                    else:
                        # count selected non-duplicate muon pairs
                        self.HISTS["cutFlow" + identifier].Fill(18)

                if "SSpairs" in alpha_category_str:
                    if m1.charge * m2.charge < 0:
                        continue
                    else:
                        # count selected same-sign pairs
                        self.HISTS["cutFlow" + identifier].Fill(19)

                if "goodQuality" in alpha_category_str:
                    if DO_REQUIRE_DIMUON_VERTEX:
                        if selected_dimuon.normChi2 > 4.0:
                            continue
                        else:
                            # count dimuons with good-quality fit
                            self.HISTS["cutFlow" + identifier].Fill(20)

                if is_dimuon:
                    dimuon_multiplicity += 1

                # collect all selected muons in order to calculate the
                # multiplicity of the selected DSA muons
                if m1 not in accepted_muons_finalSelection:
                    accepted_muons_finalSelection.append(m1)
                if m2 not in accepted_muons_finalSelection:
                    accepted_muons_finalSelection.append(m2)

                ###############################################################
                ##################### fill the histograms #####################
                ###############################################################

                if DO_CREATE_SIMPLE_HISTS:
                    for KEY in CONFIG:
                        F = CONFIG[KEY]["LAMBDA"]

                        if KEY in SINGLEMUVARIABLES:

                            for muon in (m1, m2):
                                # add up muons of all hemispheres
                                self.HISTS["DSA__" + KEY + "VAR" + identifier].Fill(
                                    F(muon)
                                )

                                if muon.charge > 0:
                                    self.HISTS[
                                        "DSA_posCharge__" + KEY + "VAR" + identifier
                                    ].Fill(F(muon))
                                else:
                                    self.HISTS[
                                        "DSA_negCharge__" + KEY + "VAR" + identifier
                                    ].Fill(F(muon))

                                # distinguish between upper and lower muon legs
                                for hs, leg in (
                                    ("lower", "_lowerLeg"),
                                    ("upper", "_upperLeg"),
                                ):

                                    if DO_REQUIRE_ONE_LEG_MATCHED:
                                        muonMatches = matchedMuons(
                                            muon,
                                            HLTmuons,
                                            threshold=MATCHING_THRESHOLD_HLT,
                                        )
                                        if len(muonMatches) == 0:
                                            continue

                                    if hemisphere(muon) == hs:
                                        self.HISTS[
                                            "DSA" + leg + "__" + KEY + "VAR" + identifier
                                        ].Fill(F(muon))

                                        if muon.charge > 0:
                                            self.HISTS[
                                                "DSA"
                                                + leg
                                                + "_posCharge"
                                                + "__"
                                                + KEY
                                                + "VAR"
                                                + identifier
                                            ].Fill(F(muon))
                                        else:
                                            self.HISTS[
                                                "DSA"
                                                + leg
                                                + "_negCharge"
                                                + "__"
                                                + KEY
                                                + "VAR"
                                                + identifier
                                            ].Fill(F(muon))

                        elif KEY in PAIRVARIABLES:

                            # ignore muon charges altogether
                            self.HISTS["DSA__" + KEY + "VAR" + identifier].Fill(
                                F((m1, m2))
                            )

                            # differentiate pair charges
                            if m1.charge * m2.charge < 0:
                                self.HISTS[
                                    "DSA_oppositeCharges"
                                    + "__"
                                    + KEY
                                    + "VAR"
                                    + identifier
                                ].Fill(F((m1, m2)))
                            else:
                                self.HISTS[
                                    "DSA_equalCharges" + "__" + KEY + "VAR" + identifier
                                ].Fill(F((m1, m2)))

                        elif KEY in DIMUONVARIABLES:
                            for dimuon in DIMUONS:
                                # find the actual dimuon object belonging to m1 and m2 first
                                if (dimuon.idx1 == m1.idx and dimuon.idx2 == m2.idx) or (
                                    dimuon.idx1 == m2.idx and dimuon.idx2 == m1.idx
                                ):
                                    self.HISTS["DSA__" + KEY + "VAR" + identifier].Fill(
                                        F(dimuon)
                                    )

                        elif KEY in L2RESOLUTIONVARIABLES or KEY in L1RESOLUTIONVARIABLES:
                            # resolution variables will be processed a few lines down
                            pass

                        else:
                            print ("[ANALYZER WARNING] Key {} not processed".format(KEY))

                if DO_CREATE_RESOLUTION_HISTS:

                    for referenceLeg, otherLeg in (
                        ("upper", "lower"),
                        ("lower", "upper"),
                    ):
                        referenceMuon = m1 if hemisphere(m1) == referenceLeg else m2
                        otherMuon = m1 if hemisphere(m1) == otherLeg else m2

                        # match reference muon leg
                        muonMatches = matchedMuons(
                            referenceMuon, HLTmuons, threshold=MATCHING_THRESHOLD_HLT
                        )
                        if len(muonMatches) > 0:
                            # is_matched_referenceLeg = True

                            # identify the closest matching HLT muon
                            matching_HLTmuon_referenceLeg = muonMatches[0]["muon"]

                            # find the associated L1 muon(s)
                            # there can be more than one L1 object for a given HLT muon
                            referenceMuon_L1muons = [
                                L1Tmuon
                                for L1Tmuon in L1Tmuons
                                if L1Tmuon.idx == matching_HLTmuon_referenceLeg.idx
                            ]
                            if len(referenceMuon_L1muons) == 0:
                                print("\t[DATA ERROR] No L1 muons found for HLT muon")

                            # create L2 resolution histograms
                            for KEY in L2RESOLUTIONVARIABLES:
                                self.HISTS[
                                    "DSA_"
                                    + referenceLeg
                                    + "Leg"
                                    + "__"
                                    + KEY
                                    + "VAR"
                                    + identifier
                                ].Fill(
                                    CONFIG[KEY]["LAMBDA"](
                                        (referenceMuon, matching_HLTmuon_referenceLeg)
                                    )
                                )

                            # create L1 resolution histograms, fill repeatedly in case
                            # of multiple L1 objects
                            if len(referenceMuon_L1muons) > 0:
                                for L1Tmuon in referenceMuon_L1muons:
                                    for KEY in L1RESOLUTIONVARIABLES:
                                        self.HISTS[
                                            "DSA_"
                                            + referenceLeg
                                            + "Leg"
                                            + "__"
                                            + KEY
                                            + "VAR"
                                            + identifier
                                        ].Fill(
                                            CONFIG[KEY]["LAMBDA"](
                                                (referenceMuon, L1Tmuon)
                                            )
                                        )

                if DO_CREATE_TURNON_HISTS:

                    for referenceLeg, otherLeg in (
                        ("upper", "lower"),
                        ("lower", "upper"),
                    ):
                        referenceMuon = m1 if hemisphere(m1) == referenceLeg else m2
                        otherMuon = m1 if hemisphere(m1) == otherLeg else m2

                        # match reference muon leg
                        muonMatches = matchedMuons(
                            referenceMuon, HLTmuons, threshold=MATCHING_THRESHOLD_HLT
                        )
                        if len(muonMatches) > 0:
                            # is_matched_referenceLeg = True

                            # identify the closest matching HLT muon
                            matching_HLTmuon_referenceLeg = muonMatches[0]["muon"]

                            # find the associated L1 muon(s)
                            # there can be more than one L1 object for a given HLT muon
                            referenceMuon_L1muons = [
                                L1Tmuon
                                for L1Tmuon in L1Tmuons
                                if L1Tmuon.idx == matching_HLTmuon_referenceLeg.idx
                            ]
                            if len(referenceMuon_L1muons) == 0:
                                print("\t[DATA ERROR] No L1 muons found for HLT muon")

                            for KEY in CONFIG:
                                if KEY in SINGLEMUVARIABLES:
                                    F = CONFIG[KEY]["LAMBDA"]
                                    for referenceMuon_L1muon in referenceMuon_L1muons:
                                        self.HISTS[
                                            "DSA_"
                                            + referenceLeg
                                            + "Leg"
                                            + "__"
                                            + KEY
                                            + "VAR"
                                            + "EffDen"
                                            + identifier
                                        ].Fill(F(referenceMuon))

                                        for L2threshold in L2THRESHOLDS:
                                            for L1threshold in L1THRESHOLDS:
                                                if (
                                                    matching_HLTmuon_referenceLeg.pt
                                                    > L2threshold
                                                ):
                                                    passed_HLT = True
                                                else:
                                                    passed_HLT = False

                                                if referenceMuon_L1muon.pt > L1threshold:
                                                    passed_L1 = True
                                                else:
                                                    passed_L1 = False

                                                if passed_HLT and passed_L1:
                                                    self.HISTS[
                                                        "DSA_"
                                                        + referenceLeg
                                                        + "Leg"
                                                        + "_L2pTGT{}".format(
                                                            str(L2threshold).replace(
                                                                ".", "p"
                                                            )
                                                        )
                                                        + "_L1pTGT{}".format(
                                                            str(L1threshold).replace(
                                                                ".", "p"
                                                            )
                                                        )
                                                        + "__"
                                                        + KEY
                                                        + "VAR"
                                                        + "EffNum"
                                                        + identifier
                                                    ].Fill(F(referenceMuon))

            self.HISTS["dimuonMultiplicity" + identifier].Fill(dimuon_multiplicity)
            if len(accepted_muons_finalSelection) > 0:
                self.HISTS["DSAmuonMultiplicity" + identifier].Fill(
                    len(accepted_muons_finalSelection)
                )


def parseIdentifiers(d0intervals, alpha_categories):
    d0 = []
    alpha = []

    d0_template = "__d0GT{}__d0LT{}"
    for d0min, d0max in d0intervals:
        if d0min is not None and d0max is not None:
            d0.append(
                d0_template.format(
                    str(d0min).replace(".", "p"), str(d0max).replace(".", "p")
                )
            )
        elif d0min is None and d0max is None:
            d0.append("")
        else:
            raise Exception("Only one of d0min and d0max being 'None' is not supported")

    for a in alpha_categories:
        alpha.append(a)

    return d0, alpha


def hemisphere(muon):
    if 0 <= muon.phi <= math.pi:
        return "upper"
    else:
        return "lower"


def parse_filename(path="roots/", prefix="", suffix="", fext=".root"):
    OpStr_as_FStr = {">": "GT", "<": "LT", u"\u2265": "GE", u"\u2264": "LE"}

    cut_variables = {}
    for CUT_SET in (SINGLEMU_SELECTION, MUONPAIR_SELECTION, DIMUON_SELECTION):
        for var in CUT_SET.keys():
            cut_str = CUT_SET[var].__str__().split(" ")
            cut_variables[var] = {
                "operator": OpStr_as_FStr[cut_str[1]],
                "value": cut_str[2],
            }

    # sort keys alphabetically
    orderedKeys = sorted(cut_variables.keys(), key=lambda k: k.lower())

    if path[-1] != "/":
        path += "/"
    filename = path + prefix
    for cut in orderedKeys:
        filename += "_" + cut
        filename += cut_variables[cut]["operator"]
        filename += cut_variables[cut]["value"].replace(".", "p")

    if any([val > 0.0 for val in L1_pairthresholds]):
        filename += "_pairL1pT{}AND{}".format(
            str(L1_pairthresholds[0]).replace(".", "p"),
            str(L1_pairthresholds[1]).replace(".", "p"),
        )

    if DO_SELECT_LARGEST_ALPHA_PAIR:
        filename += "_largestAlphaPair"
    if DO_REQUIRE_OPPOSITE_HEMISPHERES:
        filename += "_oppositeHS"
    if DO_REQUIRE_ONE_LEG_MATCHED and not DO_REQUIRE_BOTH_LEGS_MATCHED:
        filename += "_oneLegMatched"
    if DO_REQUIRE_BOTH_LEGS_MATCHED:
        filename += "_bothLegsMatched"
    if DO_REQUIRE_DIMUON_VERTEX:
        filename += "_requireDimVtx"

    if not DO_CREATE_SIMPLE_HISTS:
        filename += "_noSimpleHists"
    if not DO_CREATE_TURNON_HISTS:
        filename += "_noTurnOnHists"

    filename += suffix
    filename += "_{}"  # will be replaced by the signal point string later on
    filename += fext
    return filename


#### RUN ANALYSIS ####
if __name__ == "__main__":

    Analyzer.PARSER.add_argument(
        "--HLTfilter",
        help="Specify the name (or a substring) of the HLT path to filter by",
        dest="HLTFILTER",
        type=str,
        default=None,
    )
    Analyzer.PARSER.add_argument(
        "--output-prefix",
        help="Define an optional prefix for all output files",
        dest="OUTPUTPREFIX",
        type=str,
        default=None,
    )
    # Analyzer.PARSER.add_argument(
    #     "--reference-leg",
    #     help="Define which muon leg to use as reference leg (default: 'lower')",
    #     dest="REFLEG",
    #     type=str,
    #     default="lower",
    # )

    ARGS = Analyzer.PARSER.parse_args()
    Analyzer.setSample(ARGS)

    # if ARGS.REFLEG not in ("lower", "upper"):
    #     raise Exception("Invalid value of reference-leg (allowed: 'lower', 'upper'")

    if ARGS.HLTFILTER is None:
        print (
            "Warning: '--HLTfilter' not given, will use {}".format(
                accepted_HLTpaths_fallback
            )
        )
    else:
        print ("HLT path(s) to filter by: {}".format(ARGS.HLTFILTER))

    for METHOD in ("declareHistograms", "analyze"):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])

    analyzer = Analyzer.Analyzer(
        ARGS=ARGS, BRANCHKEYS=("DSAMUON", "DIMUON", "TRIGGER", "EVENT")
    )

    outputname = parse_filename(
        # path="roots/",
        path="/afs/cern.ch/work/s/stempl/private/DDM/analyzer_roots/testcommit/",
        prefix=ARGS.OUTPUTPREFIX if ARGS.OUTPUTPREFIX is not None else "test",
    )

    analyzer.writeHistograms(outputname)
