import operator
import math

# for printing purposes, mapping operators to strings
OpDict = {operator.gt:'>', operator.ge:u'\u2265', operator.lt:'<', operator.le:u'\u2264'}

# abstract cut object: name string, lambda expression to evaluate, comparison operator, and cut value
# apply returns a bool of the applied cut given an object (or list of objects)
# lambda expression will evaluate on the given objects in apply, so it should expect, for example, a Primitives class
class Cut(object):
    def __init__(self, name, expr, op, val):
        self.name = name
        self.expr = expr
        self.op   = op
        self.val  = val
        if self.op in (operator.gt, operator.ge):
            self.mfunc = min
        elif self.op in (operator.lt, operator.le):
            self.mfunc = max

    def apply(self, *objs):
        return self.op(self.expr(*objs), self.val)

    def __str__(self):
        return self.name + ' ' + OpDict[self.op].encode('utf-8') + ' ' + str(self.val)

# dictionaries of Cut objects
CUTS = {

### RECO MUON CUTS ###
    'pt'        : Cut('pt'       , lambda muon: muon.pt                             , operator.gt,  28.      ),
    'eta'       : Cut('eta'      , lambda muon: abs(muon.eta)                       , operator.lt,   2.      ),
    'normChi2'  : Cut('normChi2' , lambda muon: muon.normChi2                       , operator.lt,   2.      ),
    'nMuonHits' : Cut('nMuonHits', lambda muon: muon.nMuonHits                      , operator.ge,  17       ),
    'nStations' : Cut('nStations', lambda muon: muon.nDTStations + muon.nCSCStations, operator.ge,   3       ),
    'd0Sig'     : Cut('d0Sig'    , lambda muon: muon.d0Sig()                        , operator.gt,   4.      ),

### DIMUON CUTS ###
    'vtxChi2'   : Cut('vtxChi2'  , lambda dimuon: dimuon.normChi2                   , operator.lt,  4.       ),
    'deltaR'    : Cut('deltaR'   , lambda dimuon: dimuon.deltaR                     , operator.gt,  0.2      ),
    'mass'      : Cut('mass'     , lambda dimuon: dimuon.mass                       , operator.gt, 15.       ),
    'deltaPhi'  : Cut('deltaPhi' , lambda dimuon: dimuon.deltaPhi                   , operator.lt, math.pi/2.),
    'cosAlpha'  : Cut('cosAlpha' , lambda dimuon: dimuon.cosAlpha                   , operator.gt, -0.75     ),
#   'LxySig'    : Cut('LxySig'   , lambda dimuon: dimuon.LxySig                     , operator.gt, 12.       ),

### ACCEPTANCE CUTS ###
    'a_pt'      : Cut('a_pt'      , lambda muon: muon.pt                            , operator.gt,  28.      ),
    'a_eta'     : Cut('a_eta'     , lambda muon: abs(muon.eta)                      , operator.lt,   2.      ),
    'a_Lxy'     : Cut('a_Lxy'     , lambda muon: muon.LXY()                         , operator.lt, 500.      ),
}

# CutLists for access convenience (and ordering)
CutLists = {
    'MuonCutList'      : ('pt', 'eta', 'normChi2', 'nMuonHits', 'nStations', 'd0Sig'),
    'DimuonCutList'    : ('vtxChi2', 'deltaR', 'mass', 'deltaPhi', 'cosAlpha'),
#   'DimuonCutList'    : ('vtxChi2', 'deltaR', 'mass', 'deltaPhi', 'cosAlpha', 'LxySig'),
    'AcceptanceCutList': ('a_pt', 'a_eta', 'a_Lxy'),
}
for prefix in ('Muon', 'Dimuon'):
    CutLists[prefix+'CutListPlusAll' ] =             CutLists[prefix+'CutList'] + ('all',)
    CutLists[prefix+'CutListPlusNone'] = ('none',) + CutLists[prefix+'CutList']

# cut name in TLatex syntax
PrettyTitles = {
    'pt'        : 'p_{T}',
    'eta'       : '#eta',
    'normChi2'  : '#mu #chi^{2}/dof',
    'nMuonHits' : 'N(Hits)',
    'nStations' : 'N(Stations)',
    'd0Sig'     : '|d_{0}|/#sigma_{d_{0}}',
    'vtxChi2'   : 'vtx #chi^{2}/dof',
    'deltaR'    : '#DeltaR',
    'mass'      : 'M(#mu#mu)',
    'deltaPhi'  : '|#Delta#Phi|',
    'cosAlpha'  : 'cos(#alpha)',
    'a_pt'      : 'p_{T}',
    'a_eta'     : '#eta',
    'a_Lxy'     : 'L_{xy}',
    'all'       : 'all',
    'none'      : 'none',
}

# abstract Selection object for computing and storing a list of cuts
# The cutList argument should be either a CutLists key or a list of Cut keys (i.e. from CUTS)
# This will set self.cutList to be the list, and self.cutListKey to be the CutLists key if it exists
# Then initialize a results dictionary
# The object acts as a bool, returning the full AND of cuts, or can be accessed with [] for a particular cut
# The object can also update a dictionary of counts that is passed to it with IndividualIncrement or SequentialIncrement
# The former just increments everything in the results dictionary, as well as all
# The latter applies the cuts sequentially, including everything before it, starting with none
# Finally, in case one would like all the cuts except some subset, an allExcept function is provided
class Selection(object):
    def __init__(self, cutList):
        try:
            self.cutList = CutLists[cutList]
            self.cutListKey = cutList
        except:
            self.cutList = cutList
        self.results = {'all':False, 'none':True}

    def __getitem__(self, key):
        return self.results[key]

    def __bool__(self):
        return self.results['all']
    __nonzero__ = __bool__

    def IndividualIncrement(self, dictionary):
        try:
            cutList = CutLists[self.cutListKey+'PlusAll']
        except:
            cutList = self.cutList + ('all',)

        for key in cutList:
            if key in dictionary and key in self.results:
                dictionary[key] += self.results[key]

    def SequentialIncrement(self, dictionary):
        try:
            cutList = CutLists[self.cutListKey+'PlusNone']
        except:
            cutList = ('none',) + self.cutList

        for i, key in enumerate(cutList):
            if key in dictionary and key in self.results:
                dictionary[key] += all([self.results[cutkey] for cutkey in cutList[:i+1]])

    def allExcept(self, *omittedCutKeys):
        return all([self.results[key] for key in self.cutList if key not in omittedCutKeys])

# MuonSelection object, derives from Selection using the MuonCutList as default
# input is a RecoMuon
class MuonSelection(Selection):
    def __init__(self, muon, cutList='MuonCutList'):
        Selection.__init__(self, cutList=cutList)
        self.results.update({key:CUTS[key].apply(muon) for key in self.cutList})
        self.results['all'] = all([self.results[key] for key in self.cutList])

# DimuonSelection object, derives from Selection using the DimuonCutList as default
# input is a Dimuon
class DimuonSelection(Selection):
    def __init__(self, dimuon, cutList='DimuonCutList'):
        Selection.__init__(self, cutList=cutList)
        self.results.update({key:CUTS[key].apply(dimuon) for key in self.cutList})
        self.results['all'] = all([self.results[key] for key in self.cutList])

# AcceptanceSelection object, derives from Selection using the AcceptanceCutList as default
# input is either one or a pair of GenMuons
class AcceptanceSelection(Selection):
    def __init__(self, genMuon, cutList='AcceptanceCutList'):
        Selection.__init__(self, cutList=cutList)
        try:
            self.results.update({key:CUTS[key].apply(genMuon[0]) and
                                     CUTS[key].apply(genMuon[1]) for key in self.cutList})
        except:
            self.results.update({key:CUTS[key].apply(genMuon) for key in self.cutList})
        self.results['all'] = all([self.results[key] for key in self.cutList])

# Print full cut list as strings
if __name__ == '__main__':
    for key in CUTS:
        print str(CUTS[key])
