import operator
import math
import DisplacedDimuons.Analysis.Primitives as Primitives

# for signal samples, whether or not this event passed the trigger
# E is the whole ETree, contingent on adding TRIGGER to the DecList
# This is wasteful since it calls getPrimitives, but probably okay
# because this will only be called once per event
def passedTrigger(E):
    HLTPaths, HLTMuons, L1TMuons = E.getPrimitives('TRIGGER')
    if len(HLTPaths) > 0:
        return True
    return False

# for printing purposes, mapping operators to strings
OpDict = {operator.gt:'>', operator.ge:u'\u2265', operator.lt:'<', operator.le:u'\u2264', operator.eq:'='}

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

# MultiCut derives from Cut, specifying a set of closely related cuts
# the values are given in a dictionary (val), and the key to access the right value
# is given by keyExpr. Everything else is the same
class MultiCut(Cut):
    def __init__(self, name, expr, op, val, keyExpr):
        Cut.__init__(self, name, expr, op, val)
        self.keyExpr = keyExpr

    def apply(self, *objs):
        return self.op(self.expr(*objs), self.val[self.keyExpr(*objs)])

    def __str__(self):
        valString = ' '.join(['{} ({})'.format(val, key) for key, val in self.val.iteritems()])
        return self.name + ' ' + OpDict[self.op].encode('utf-8') + ' ' + valString

# a special class for a special purpose
# This is a MultiCut that applies its cuts to the constituent muons in a dimuon
# So everything -- expr, op, val, keyExpr -- should work on a constituent muon
# and not on the encapsulating dimuon
class DimMuCut(MultiCut):
    def __init__(self, name, expr, op, val, keyExpr):
        MultiCut.__init__(self, name, expr, op, val, keyExpr)

    def apply(self, dim):
        return all([MultiCut.apply(self, mu) for mu in (dim.mu1, dim.mu2)])

# dictionaries of Cut objects
CUTS = {

### GEN ACCEPTANCE CUTS ###
    'a_pT'       :      Cut('pT'       , lambda mu : mu.pt                          , operator.gt,         25.      ),
    'a_eta'      :      Cut('eta'      , lambda mu : abs(mu.eta)                    , operator.lt,          2.      ),
    'a_Lxy'      :      Cut('Lxy'      , lambda mu : mu.Lxy()                       , operator.lt,        500.      ),

### DSA MUON QUALITY CUTS ###
    'q_nStations':      Cut('nStations', lambda mu : mu.nCSCStations+mu.nDTStations , operator.gt,          1       ),
    'q_nMuonHits':      Cut('nMuonHits', lambda mu : mu.nCSCHits+mu.nDTHits         , operator.gt,         12       ),
    'q_FPTE'     :      Cut('FPTE'     , lambda mu : mu.ptError/mu.pt               , operator.lt,          1.      ),

### PAT MUON QUALITY CUTS ###
    'p_isGlobal' :      Cut('isGlobal' , lambda mu : mu.isGlobal                    , operator.eq,       True       ),
    'p_isMedium' :      Cut('isMedium' , lambda mu : mu.isMedium                    , operator.eq,       True       ),
    'p_nTrkLays' :      Cut('nTrkLays' , lambda mu : mu.nTrackerLayers              , operator.gt,          6       ),

### MUON CUTS ###
    'm_pT'       :      Cut('pT'       , lambda mu : mu.pt                          , operator.gt,         10.      ),
    'm_d0Sig'    : MultiCut('d0Sig'    , lambda mu : mu.d0Sig()                     , operator.gt, {'DSA':  3.       ,
                                                                                                    'PAT': 10.      }, lambda mu: mu.tag              ),

### DIMUON CUTS ###
    'd_LxyErr'   :      Cut('LxyErr'   , lambda dim: dim.LxyErr()                   , operator.lt,         99.      ),
    'd_mass'     :      Cut('mass'     , lambda dim: dim.mass                       , operator.gt,         10.      ),
    'd_vtxChi2'  : MultiCut('vtxChi2'  , lambda dim: dim.normChi2                   , operator.lt, {'DSA': 50.       ,
                                                                                                    'PAT': 50.       ,
                                                                                                    'HYB': 50.      }, lambda dim: dim.composition[:3]),
    'd_d0Sig'    : DimMuCut('d0Sig'    , lambda ref: ref.d0Sig()                    , operator.gt, {'DSA':  3.       ,
                                                                                                    'PAT': 10.      }, lambda ref: ref.tag[4:7]       ),

### RUN 1 RECO MUON CUTS ###
    '8_pT'       :      Cut('pT'       , lambda mu : mu.pt                          , operator.gt,         30.      ),
    '8_eta'      :      Cut('eta'      , lambda mu : abs(mu.eta)                    , operator.lt,          2.      ),
    '8_normChi2' :      Cut('normChi2' , lambda mu : mu.normChi2                    , operator.lt,          2.      ),
    '8_nMuonHits':      Cut('nMuonHits', lambda mu : mu.nMuonHits                   , operator.ge,         17       ),
    '8_nStations':      Cut('nStations', lambda mu : mu.nCSCStations+mu.nDTStations , operator.ge,          3       ),
    '8_d0Sig'    :      Cut('d0Sig'    , lambda mu : mu.d0Sig()                     , operator.gt,          4.      ),

### RUN 1 DIMUON CUTS ###
    '8_vtxChi2'  :      Cut('vtxChi2'  , lambda dim: dim.normChi2                   , operator.lt,          4.      ),
    '8_deltaR'   :      Cut('deltaR'   , lambda dim: dim.deltaR                     , operator.gt,          0.2     ),
    '8_mass'     :      Cut('mass'     , lambda dim: dim.mass                       , operator.gt,         15.      ),
    '8_deltaPhi' :      Cut('deltaPhi' , lambda dim: dim.deltaPhi                   , operator.lt,        math.pi/2.),
    '8_cosAlpha' :      Cut('cosAlpha' , lambda dim: dim.cosAlpha                   , operator.gt,         -0.75    ),
    '8_LxySig'   :      Cut('LxySig'   , lambda dim: dim.LxySig()                   , operator.gt,         12.      ),

}

# CutLists for access convenience (and ordering)
CutLists = {
    'AcceptanceCutList'     : ('a_pT', 'a_eta', 'a_Lxy'),
    'DSAQualityCutList'     : ('q_nStations', 'q_nMuonHits', 'q_FPTE'),
    'PATQualityCutList'     : ('p_isGlobal', 'p_isMedium', 'p_nTrkLays'),
    'AllMuonCutList'        : ('m_pT', 'm_d0Sig'),
    'DimuonCutList'         : ('d_LxyErr', 'd_mass', 'd_vtxChi2', 'd_d0Sig'),
    'Run1MuonCutList'       : ('8_pT', '8_eta', '8_normChi2', '8_nMuonHits', '8_nStations', '8_d0Sig'),
    'Run1DimuonCutList'     : ('8_vtxChi2', '8_deltaR', '8_mass', '8_deltaPhi', '8_cosAlpha', '8_LxySig'),
}

# cut name in TLatex syntax
PrettyTitles = {
    'pT'        : 'p_{T}',
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
    'LxySig'    : 'L_{xy}/#sigma_{L_{xy}}',
    'Lxy'       : 'L_{xy}',
    'd0'        : 'd_{0}',
    'all'       : 'all',
    'none'      : 'none',
}

# abstract Selection object for computing and storing a list of cuts
# The cutList argument should be either a CutLists key or a list of Cut keys (i.e. from CUTS)
# This will set self.cutList to be the list, and self.cutListKey to be the CutLists key if it exists
# Then initialize a results dictionary
# The object acts as a bool, returning the full AND of cuts, or can be accessed with [] for a particular cut
# In case one would like the AND of a list of cuts, an allOf function is provided
# In case one would like all the cuts except some subset, an allExcept function is provided
# The object can also update a dictionary of counts that is passed to it with the *Increment functions
#   IndividualIncrement increments everything in the results dictionary, as well as all
#   SequentialIncrement increments the cuts sequentially, including everything before it, starting with none
#   NMinusOneIncrement  increments each cut by its allExcept value
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

    def allExcept(self, *omittedCutKeys):
        return all([self.results[key] for key in self.cutList if key not in omittedCutKeys])

    def allOf(self, *requiredCutKeys):
        return all([self.results[key] for key in requiredCutKeys])

# MuonSelection object, derives from Selection using the AllMuonCutList as default
# input is a RecoMuon
class MuonSelection(Selection):
    def __init__(self, muon, cutList='AllMuonCutList'):
        Selection.__init__(self, cutList=cutList)
        EnsureInstances(muon, Primitives.RecoMuon)
        self.results.update({key:CUTS[key].apply(muon) for key in self.cutList})
        self.results['all'] = all([self.results[key] for key in self.cutList])

# DimuonSelection object, derives from Selection using the DimuonCutList as default
# input is a Dimuon
class DimuonSelection(Selection):
    def __init__(self, dimuon, cutList='DimuonCutList'):
        Selection.__init__(self, cutList=cutList)
        EnsureInstances(dimuon, Primitives.Dimuon)
        self.results.update({key:CUTS[key].apply(dimuon) for key in self.cutList})
        self.results['all'] = all([self.results[key] for key in self.cutList])

# AcceptanceSelection object, derives from Selection using the AcceptanceCutList as default
# input is either one or a pair of GenMuons
class AcceptanceSelection(Selection):
    def __init__(self, genMuon, cutList='AcceptanceCutList'):
        Selection.__init__(self, cutList=cutList)
        EnsureInstances(genMuon, Primitives.GenMuon)
        try:
            self.results.update({key:CUTS[key].apply(genMuon[0]) and
                                     CUTS[key].apply(genMuon[1]) for key in self.cutList})
        except:
            self.results.update({key:CUTS[key].apply(genMuon) for key in self.cutList})
        self.results['all'] = all([self.results[key] for key in self.cutList])

# EnsureInstances: make sure that the object passed to Selection is the one expected
def EnsureInstances(OBJ, CLASS):
    try:
        for obj in OBJ:
            if not obj.__class__.__name__ == CLASS.__name__:
                raise Exception('Object is not an instance of class "'+CLASS.__name__+'"')
    except:
        if not OBJ.__class__.__name__ == CLASS.__name__:
            raise Exception('Object is not an instance of class "'+CLASS.__name__+'"')

# Print full cut list as strings
if __name__ == '__main__':
    for cutkey in ('AcceptanceCutList', 'DSAQualityCutList', 'PATQualityCutList', 'AllMuonCutList', 'DimuonCutList'):
        print '\033[1m{cutkey}\033[m'.format(cutkey=cutkey)
        for key in CutLists[cutkey]:
            print ' ', str(CUTS[key])
        print ''
