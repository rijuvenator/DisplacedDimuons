import ROOT as R

# takes an ntuple tree with gen_ branches of length 8
# sets tree aliases for use in formulae
def setGenAliases(t):
	for i, particle in enumerate(('mu11', 'mu12', 'mu21', 'mu22', 'X1', 'X2', 'H', 'P')):
		for attribute in ('pdgID', 'pt', 'eta', 'phi', 'mass', 'energy', 'charge', 'x', 'y', 'z'):
			t.SetAlias(particle+'.'+attribute, 'gen_'+attribute+'['+str(i)+']')
