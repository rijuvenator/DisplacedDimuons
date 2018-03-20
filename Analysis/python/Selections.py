import operator

class Cut(object):
	def __init__(self, name, expr, op, val):
		self.name = name
		self.expr = expr
		self.op   = op
		self.val  = val
	
	def apply(self, *objs):
		return self.op(self.expr(*objs), self.val)

MuonCutList = {
	'pt'        : Cut('pt'       , lambda muon: muon.pt                             , operator.gt, 26.),
	'eta'       : Cut('eta'      , lambda muon: abs(muon.eta)                       , operator.lt,  2.),
	'normChi2'  : Cut('normChi2' , lambda muon: muon.normChi2                       , operator.lt,  2.),
	'nMuonHits' : Cut('nMuonHits', lambda muon: muon.nMuonHits                      , operator.ge, 17 ),
	'nStations' : Cut('nStations', lambda muon: muon.nDTStations + muon.nCSCStations, operator.ge,  3 ),
	'd0Sig'     : Cut('d0Sig'    , lambda muon: muon.d0MVSig                        , operator.gt,  4.),
}

class MuonSelection(object):
	def __init__(self, muon):
		self.results = {}
		for cut in MuonCutList.values():
			self.results[cut.name] = cut.apply(muon)
		self.results['all'] = all(self.results.values())
	
	def __getitem__(self, key):
		return self.results[key]

	def __bool__(self):
		return self.results['all']
	__nonzero__ = __bool__
