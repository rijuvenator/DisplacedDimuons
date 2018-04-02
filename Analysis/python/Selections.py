import operator

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
	
	def apply(self, *objs):
		return self.op(self.expr(*objs), self.val)

	def __str__(self):
		return self.name + ' ' + OpDict[self.op].encode('utf-8') + ' ' + str(self.val)

# dictionaries of Cut objects
MuonCuts = {
	'pt'        : Cut('pt'       , lambda muon: muon.pt                             , operator.gt,  26.),
	'eta'       : Cut('eta'      , lambda muon: abs(muon.eta)                       , operator.lt,   2.),
	'Lxy'       : Cut('Lxy'      , lambda muon: muon.Lxy()                          , operator.lt, 650.),
	'normChi2'  : Cut('normChi2' , lambda muon: muon.normChi2                       , operator.lt,   2.),
	'nMuonHits' : Cut('nMuonHits', lambda muon: muon.nMuonHits                      , operator.ge,  17 ),
	'nStations' : Cut('nStations', lambda muon: muon.nDTStations + muon.nCSCStations, operator.ge,   3 ),
	'd0Sig'     : Cut('d0Sig'    , lambda muon: muon.d0MVSig                        , operator.gt,   4.),
}
DimuonCuts = {
	'vtxChi2'   : Cut('vtxChi2'  , lambda dimuon: dimuon.normChi2                   , operator.lt,  4. ),
	'deltaR'    : Cut('deltaR'   , lambda dimuon: dimuon.deltaR                     , operator.gt,  0.2),
	'mass'      : Cut('mass'     , lambda dimuon: dimuon.mass                       , operator.gt, 15. ),
}

# CutLists for access convenience (and ordering)
CutLists = {
	'MuonCutList'  : ('pt', 'eta', 'Lxy', 'normChi2', 'nMuonHits', 'nStations', 'd0Sig'),
	'DimuonCutList': ('vtxChi2', 'deltaR', 'mass'),
}

CutLists['MuonAcceptanceCutList'] = CutLists['MuonCutList'][0:3]
for prefix in ('Muon', 'Dimuon'):
	CutLists[prefix+'CutListPlusAll' ] =             CutLists[prefix+'CutList'] + ('all',)
	CutLists[prefix+'CutListPlusNone'] = ('none',) + CutLists[prefix+'CutList']

# cut name in TLatex syntax
PrettyTitles = {
	'pt'        : 'p_{T}',
	'eta'       : '#eta',
	'Lxy'       : 'L_{xy}',
	'normChi2'  : '#mu #chi^{2}/dof',
	'nMuonHits' : 'N(Hits)',
	'nStations' : 'N(Stations)',
	'd0Sig'     : '|d_{0}|/#sigma_{d_{0}}',
	'vtxChi2'   : 'vtx #chi^{2}/dof',
	'deltaR'    : '#DeltaR',
	'mass'      : 'M(#mu#mu)',
	'all'       : 'all',
	'none'      : 'none',
}

# abstract Selection object for computing and storing a list of cuts
# The cutList argument should be either a CutLists key or a list of Cut keys (e.g. from MuonCuts)
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
# and additionally defines a passesAcceptance function just for the Acceptance cuts
class MuonSelection(Selection):
	def __init__(self, muon, cutList='MuonCutList'):
		Selection.__init__(self, cutList=cutList)
		self.results.update({key:MuonCuts[key].apply(muon) for key in self.cutList})
		self.results['all'] = all([self.results[key] for key in self.cutList])

	def passesAcceptance(self):
		return all([self.results[key] for key in CutLists['MuonAcceptanceCutList'] if key in self.results])

# DimuonSelection object, derives from Selection using the DimuonCutList as default
class DimuonSelection(Selection):
	def __init__(self, dimuon, cutList='DimuonCutList'):
		Selection.__init__(self, cutList=cutList)
		self.results.update({key:DimuonCuts[key].apply(dimuon) for key in self.cutList})
		self.results['all'] = all([self.results[key] for key in self.cutList])

# Print full cut list as strings
if __name__ == '__main__':
	for key in CutLists['MuonCutList']:
		print str(MuonCuts[key])
	for key in CutLists['DimuonCutList']:
		print str(DimuonCuts[key])
