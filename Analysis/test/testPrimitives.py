import ROOT as R
import DisplacedDimuons.Analysis.Primitives as Primitives

def tprint(msg):
    print '\033[32mPRIMITIVES TEST: ' + msg + '\033[m'
def eprint(msg):
    print '\033[31mPRIMITIVES TEST: ' + msg + '\033[m'

f = R.TFile.Open('~/eos/DisplacedDimuons/NTuples/ntuple_DY100to200.root')
t = f.Get('SimpleNTupler/DDTree')

# test tree
try:
    t.GetEntries()
    tprint('Successfully got tree...')
except:
    eprint('Failed to get tree; exiting')
    exit()

# containers for storing error information
KEYS = {
        'EVENT'   : [-1, False],
        'MET'     : [-1, False],
        'VERTEX'  : [-1, False],
        'BEAMSPOT': [-1, False],
        'GEN'     : [-1, False],
        'MUON'    : [-1, False],
        'DSAMUON' : [-1, False],
        'RSAMUON' : [-1, False],
        'DIMUON'  : [-1, False],
}

LXYTest = []
d0Test  = []

# test collections
for i, event in enumerate(t):
    if i == 10: break
    E = Primitives.ETree(t)
    for KEY in KEYS:
        try:
            Collection = E.getPrimitives(KEY)
            try:
                if len(Collection) > 0:
                    obj = Collection[0]
                    if issubclass(obj.__class__, Primitives.Muon):
                        try:
                            x = obj.LXY()
                        except:
                            if KEY not in LXYTest:
                                LXYTest.append(KEY)
                    if isinstance(obj.__class__, Primitives.RecoMuon):
                        try:
                            x = obj.d0(extrap='LIN')
                            s = obj.d0Sig(vertex='BS')
                        except:
                            if KEY not in d0Test:
                                d0Test.append(KEY)
            except:
                pass
        except:
            KEYS[KEY][0] = i
            KEYS[KEY][1] = True

for KEY in KEYS:
    if not KEYS[KEY][1]:
        tprint('Successfully got all '+KEY+' ...')
    else:
        eprint('Problem getting '+KEY+', see e.g. event '+str(KEYS[KEY][0]))
if len(LXYTest) > 0:
    eprint('Lxy() failed for: '+' '.join(LXYTest))
else:
    tprint('Lxy() succeeded for all collections...')
if len(d0Test) > 0:
    eprint('d0() or d0Sig() failed for: '+' '.join(d0Test))
else:
    tprint('d0() or d0Sig() succeeded for all collections...')

# test signal gen particles
f = R.TFile.Open('~/eos/DisplacedDimuons/NTuples/aodOnly_ntuple_HTo2XTo4Mu_125_20_13.root')
t = f.Get('SimpleNTupler/DDTree')
Primitives.SelectBranches(t, DecList=('GEN',))

Erred = False

for i, event in enumerate(t):
    if i == 10: break
    E = Primitives.ETree(t, DecList=('GEN',))
    try:
        mu11, mu12, mu21, mu22, X1, X2, H, P = E.getPrimitives('GEN', 'HTo2XTo4Mu')
    except:
        Erred = True

if not Erred:
    tprint('Successfully got all 4Mu gen particles...')
else:
    eprint('Problem getting 4Mu gen particles')

tprint('Done.')
