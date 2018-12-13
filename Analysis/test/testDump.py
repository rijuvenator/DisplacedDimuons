import ROOT as R
import DisplacedDimuons.Analysis.Primitives as Primitives
import DisplacedDimuons.Common.Constants as Constants
import os

Primitives.COLORON = True


# test files
# if not on lxplus, add a root protocol
if not 'lxplus' in os.environ['HOSTNAME']:
    PREFIX = Constants.PREFIX_CERN
else:
    PREFIX = ''
F_NTUPLE = PREFIX+Constants.DIR_EOS+'NTuples/ntuple_HTo2XTo4Mu_125_20_13.root'

def tprint(msg):
    print '\033[32mPRIMITIVES TEST: ' + msg + '\033[m'
def eprint(msg):
    print '\033[31mPRIMITIVES TEST: ' + msg + '\033[m'

f = R.TFile.Open(F_NTUPLE)
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
    if i == 3: break
    E = Primitives.ETree(t)
    print E
