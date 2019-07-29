# weights dictionary for reweighting to pileup
WEIGHTS = {i:{'None':1., 'Nom':1., 'High':1., 'Low':1.} for i in xrange(100)}
with open('text/pileupWeights.txt') as f:
    for line in f:
        cols = line.strip('\n').split()
        nTruePV = int(cols[0])
        for key, val in zip(('Nom', 'Low', 'High'), tuple(map(float, cols[2:]))):
            WEIGHTS[nTruePV][key] = val

# wrapper function for actually getting the event weight
def PileupWeight(nTruePV, variation='Nom'):
    return WEIGHTS[int(nTruePV)][variation]
