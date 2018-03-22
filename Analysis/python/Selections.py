import operator

OpDict = {operator.gt:'>', operator.ge:u'\u2265', operator.lt:'<', operator.le:u'\u2264'}

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

MuonCuts = {
	'pt'        : Cut('pt'       , lambda muon: muon.pt                             , operator.gt,  26.),
	'eta'       : Cut('eta'      , lambda muon: abs(muon.eta)                       , operator.lt,   2.),
	'Lxy'       : Cut('Lxy'      , lambda muon: muon.Lxy()                          , operator.lt, 650.),
	'normChi2'  : Cut('normChi2' , lambda muon: muon.normChi2                       , operator.lt,   2.),
	'nMuonHits' : Cut('nMuonHits', lambda muon: muon.nMuonHits                      , operator.ge,  17 ),
	'nStations' : Cut('nStations', lambda muon: muon.nDTStations + muon.nCSCStations, operator.ge,   3 ),
	'd0Sig'     : Cut('d0Sig'    , lambda muon: muon.d0MVSig                        , operator.gt,   4.),
}
MuonCutList = ('pt', 'eta', 'Lxy', 'normChi2', 'nMuonHits', 'nStations', 'd0Sig')
MuonAcceptanceCutList = ('pt', 'eta', 'Lxy')
MuonCutListPlusAll = MuonCutList + ('all',)
MuonCutListPlusNone = ('none',) + MuonCutList

class MuonSelection(object):
	def __init__(self, muon, cutList=MuonCutList):
		self.results = {key:MuonCuts[key].apply(muon) for key in cutList}
		self.results['all'] = all(self.results.values())
		self.results['none'] = True
	
	def __getitem__(self, key):
		return self.results[key]

	def __bool__(self):
		return self.results['all']
	__nonzero__ = __bool__

	def IndividualIncrement(self, dictionary):
		for key in MuonCutListPlusAll:
			if key in dictionary and key in self.results:
				dictionary[key] += self.results[key]

	def SequentialIncrement(self, dictionary):
		for i, key in enumerate(MuonCutListPlusNone):
			if key in dictionary and key in self.results:
				dictionary[key] += all([self.results[cutkey] for cutkey in MuonCutListPlusNone[:i+1]])

	def passesAcceptance(self):
		return all([self.results[key] for key in MuonAcceptanceCutList])

	def allExcept(self, *omittedCutKeys):
		return all([self.results[key] for key in MuonCutList if key not in omittedCutKeys])

if __name__ == '__main__':
	for key in MuonCutList:
		print str(MuonCuts[key])
