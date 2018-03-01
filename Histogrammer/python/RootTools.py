import ROOT as R

#### Vector Classes
# REALLY generic init and Dist functions
def genericInit(self, *args):
	if len(args) == 0:
		super(self.__class__, self).__init__()
	else:
		super(self.__class__, self).__init__(*args)
def genericDist(self, vec):
	try:
		return (self-vec).Mag()
	except:
		return (self-self.__class__(*vec)).Mag()
def genericInverse(self):
	return self.__class__(*[1./vec_i for vec_i in self])
def genericFormat(self, format_spec):
	if format_spec.endswith('p'):
		fstring = '(' + ', '.join(['{{{index}:{{fs}}}}'.format(index=i) for i in range(len(self))]) + ')'
		return fstring.format(*self, fs=format_spec[:-1]+'f')
	else:
		return self.__repr__()

# class decorator
def improve(cls):
	cls.__init__ = genericInit
	cls.Dist = genericDist
	cls.Inverse = genericInverse
	cls.__format__ = genericFormat
	return cls

@improve
class LorentzVector(R.TLorentzVector): pass
@improve
class Vector3(R.TVector3): pass
@improve
class Vector2(R.TVector2): pass

# TLorentzVector doesn't implement an iterator (for..in or *) or a length, but TVector2/3 do
LorentzVector.__len__  = lambda self : 4
LorentzVector.__iter__ = lambda self : iter([self[0], self[1], self[2], self[3]])

#### TTree Tools
# takes an ntuple tree with gen_ branches of length 8
# sets tree aliases for use in formulae
def setGenAliases(t):
	for i, particle in enumerate(('mu11', 'mu12', 'mu21', 'mu22', 'X1', 'X2', 'H', 'P')):
		for attribute in ('pdgID', 'pt', 'eta', 'phi', 'mass', 'energy', 'charge', 'x', 'y', 'z'):
			t.SetAlias(particle+'.'+attribute, 'gen_'+attribute+'['+str(i)+']')
