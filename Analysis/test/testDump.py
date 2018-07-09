import ROOT as R
import DisplacedDimuons.Analysis.Primitives as Primitives

TESTFILE = 'test.root'

f = R.TFile.Open(TESTFILE)
t = f.Get('SimpleNTupler/DDTree')

# test tree
try:
    t.GetEntries()
    print('Successfully got tree...')
except:
    print('Failed to get tree; exiting')
    exit()
    
    
# test collections
for i, event in enumerate(t):
    if i == 10: break
    E = Primitives.ETree(t)
    print E
