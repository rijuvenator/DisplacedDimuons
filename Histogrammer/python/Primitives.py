import re
import collections
import math
import DisplacedDimuons.Histogrammer.RootTools as RT

##########
# This file defines the Primitives classes for ease of access and idiomatic analysis code.
# Seriously, life is much better once you have a list of objects that are actual objects.
# Line breaks are meta-computation -- things you can't get directly from the trees.
##########

BRANCHPREFIXES = {
	'EVENT'    : 'evt_'  ,
	'TRIGGER'  : 'trig_' ,
	'BEAMSPOT' : 'bs_'   ,
	'VERTEX'   : 'vtx_'  ,
	'GEN'      : 'gen_'  ,
	'MUON'     : 'mu_'   ,
	'DSAMUON'  : 'dsamu_',
}
BRANCHKEYS = tuple(BRANCHPREFIXES.keys())

# Select Branches: 2-5x speedup
def SelectBranches(t, DecList=(), branches=()):
	t.SetBranchStatus('*', 0)
	Branches = [br for br in branches]
	BranchList = [str(br.GetName()) for br in list(t.GetListOfBranches())]
	for KEY in DecList:
		Branches.extend([br for br in BranchList if re.match(BRANCHPREFIXES[KEY], br)])
	for branch in Branches:
		t.SetBranchStatus(branch, 1)

# "EventTree", purely for speed purposes. Making lists from ROOT vectors is slow.
# It should only be done once per event, not once per object! So create this,
# then pass it to the classes (which used to take addressed trees; they now take this)
# DecList is for turning on or off some declarations. No need to declare everything
# if we're not going to use them.
class ETree(object):
	def __init__(self, t, DecList=BRANCHKEYS):
		BranchList = [str(br.GetName()) for br in list(t.GetListOfBranches())]
		for KEY in DecList:
			for br in BranchList:
				if re.match(BRANCHPREFIXES[KEY], br):
					self.copyBranch(t, br)
	
	def copyBranch(self, t, branch):
		if 'vector' in type(getattr(t, branch)).__name__:
			setattr(self, branch, list(getattr(t, branch)))
		else:
			setattr(self, branch, getattr(t, branch))
	
	def getPrimitives(self, KEY):
		if KEY == 'GEN':
			muons   = [Muon    (self, i, 'GEN' ) for i in range(4)                 ]
			mothers = [Particle(self, i, 'gen_') for i in range(4, 8)              ]
			return muons + mothers
		if KEY == 'VERTEX':
			return    [Vertex  (self, i        ) for i in range(len(self.vtx_x   ))]
		if KEY == 'MUON':
			return    [Muon    (self, i, 'AOD' ) for i in range(len(self.mu_pt   ))]
		if KEY == 'DSAMUON':
			return    [Muon    (self, i, 'DSA' ) for i in range(len(self.dsamu_pt))]

# The Primitives Classes: take in an ETree and an index, produces an object.
# Base class for primitives
# just provides a wrapper for setting attributes
class Primitive(object):
	def __init__(self):
		pass

	def set(self, attr, E, E_attr, i):
		setattr(self, attr, getattr(E, E_attr)[i])

# Particle class
# sets all the variables, also sets pos, p4, and p3 vectors
class Particle(Primitive):
	def __init__(self, E, i, prefix):
		Primitive.__init__(self)
		for attr in ('pdgID', 'pt', 'eta', 'phi', 'mass', 'energy', 'charge', 'x', 'y', 'z'):
			self.set(attr, E, prefix+attr, i)
		self.pos = RT.Vector3(self.x, self.y, self.z)

		self.p4 = RT.LorentzVector()
		self.p4.SetPtEtaPhiE(self.pt, self.eta, self.phi, self.energy)

		# this is an XYZ 3-vector!
		self.p3 = RT.Vector3(*self.p4.Vect())

# Muon class
# sets all the particle variables
# distinguishes three "kinds" of muons:
# reco AOD muon, GEN muon, and the GEN particle attached to the reco AOD muon
# the last one is called "SUB"
class Muon(Particle):
	def __init__(self, E, i, source=None):
		self.source = source
		if   self.source == 'AOD': prefix = 'mu_'
		elif self.source == 'GEN': prefix = 'gen_'
		elif self.source == 'SUB': prefix = 'mu_gen_'
		elif self.source == 'DSA': prefix = 'dsamu_'
		Particle.__init__(self, E, i, prefix)

		if self.source == 'AOD':
			self.gen = Muon(E, i, source='SUB')
			self.set('isSlim', E, 'mu_isSlim', i)

		if self.source == 'GEN' or self.source == 'DSA':
			self.set('d0', E, prefix+'d0', i)

		if self.source == 'GEN':
			self.set('d00', E, prefix+'d00', i)

		if self.source == 'DSA':
			for attr in ('normChi2', 'nMuonHits', 'nDTStations', 'nCSCStations', 'd0Sig', 'd0MVSig', 'd0MV'):
				self.set(attr, E, prefix+attr, i)

# Vertex class
# nothing too unusual here
class Vertex(Primitive):
	def __init__(self, E, i):
		Primitive.__init__(self)
		for attr in ('x', 'y', 'z', 'chi2', 'ndof'):
			self.set(attr, E, 'vtx_'+attr, i)

		self.pos = RT.Vector3(self.x, self.y, self.z)
