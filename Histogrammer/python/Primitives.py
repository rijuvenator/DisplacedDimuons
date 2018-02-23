import re
import collections
import math

##########
# This file defines the Primitives classes for ease of access and idiomatic analysis code.
# Seriously, life is much better once you have a list of objects that are actual objects.
# Line breaks are meta-computation -- things you can't get directly from the trees.
##########

BRANCHPREFIXES = {
	'EVENT'    : 'evt_' ,
	'TRIGGER'  : 'trig_',
	'BEAMSPOT' : 'bs_'  ,
	'VERTEX'   : 'vtx_' ,
	'GEN'      : 'gen_' ,
	'MUON'     : 'mu_'  ,
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
			muons   = [Muon    (self, i, 'GEN' ) for i in range(4)              ]
			mothers = [Particle(self, i, 'gen_') for i in range(4, 8)           ]
			return muons + mothers
		if KEY == 'VERTEX':
			return    [Vertex  (self, i        ) for i in range(len(self.vtx_x))]
		if KEY == 'MUON':
			return    [Muon    (self, i, 'AOD' ) for i in range(len(self.mu_pt))]

# Useful Point class for vector addition (+), dot product or scalar multiplication (*), distance
PointTuple = collections.namedtuple('PointTuple', ['x', 'y', 'z'])
class Point(PointTuple):
	def __init__(self, x, y, z):
		PointTuple.__init__(x, y, z)
	
	def __format__(self, format_spec):
		if format_spec.endswith('p'):
			return '({x:{fs}}, {y:{fs}}, {z:{fs}})'.format(fs=format_spec[:-1]+'f', x=self.x, y=self.y, z=self.z)
		else:
			return self.__repr__()

	def __sub__(self, point):
		return Point(self.x - point.x, self.y - point.y, self.z - point.z)
	
	def __rsub__(self, point):
		return Point(point[0] - self.x, point[1] - self.y, point[2] - self.z)

	def __add__(self, point):
		return Point(self.x + point.x, self.y + point.y, self.z + point.z)
	
	def __radd__(self, point):
		return Point(point[0] + self.x, point[1] + self.y, point[2] + self.z)

	def __mul__(self, multiplier):
		try:
			point = multiplier
			return self.x * point[0] + self.y * point[1] + self.z * point[2]
		except:
			scalar = multiplier
			return Point(self.x * scalar, self.y * scalar, self.z * scalar)
	
	def __rmul__(self, multiplier):
		return self * multiplier

	def __rdiv__(self, scalar):
		return Point(scalar/self.x, scalar/self.y, scalar/self.z)

	def norm(self):
		return (self.x**2 + self.y**2 + self.z**2)**0.5

	@staticmethod
	def dist(a, b):
		return (a-b).norm()

# The Primitives Classes: take in an ETree and an index, produces an object.
class Primitive(object):
	def __init__(self):
		pass

	def set(self, attr, E, E_attr, i):
		setattr(self, attr, getattr(E, E_attr)[i])

class Particle(Primitive):
	def __init__(self, E, i, prefix):
		Primitive.__init__(self)
		for attr in ('pdgID', 'pt', 'eta', 'phi', 'mass', 'energy', 'charge', 'x', 'y', 'z'):
			self.set(attr, E, prefix+attr, i)
		self.pos = Point(self.x, self.y, self.z)
		try:
			self.p3  = Point(self.pt * math.cos(self.phi), self.pt * math.sin(self.phi), self.pt * math.sinh(self.eta))
		except:
			self.p3  = Point(-999., -999., -999.)

class Muon(Particle):
	def __init__(self, E, i, source=None):
		self.source = source
		if   self.source == 'AOD': prefix = 'mu_'
		elif self.source == 'GEN': prefix = 'gen_'
		elif self.source == 'SUB': prefix = 'mu_gen_'
		Particle.__init__(self, E, i, prefix)

		if self.source == 'AOD':
			self.gen = Muon(E, i, source='SUB')
			self.set('isSlim', E, 'mu_isSlim', i)

class Vertex(Primitive):
	def __init__(self, E, i):
		Primitive.__init__(self)
		for attr in ('x', 'y', 'z', 'chi2', 'ndof'):
			self.set(attr, E, 'vtx_'+attr, i)

		self.pos = Point(self.x, self.y, self.z)
