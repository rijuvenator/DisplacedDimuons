import os
import ROOT as R
import DisplacedDimuons.Analysis.Primitives as Primitives
import DisplacedDimuons.Common.Constants as Constants

# test files
# if not on lxplus, add a root protocol
if not 'lxplus' in os.environ['HOSTNAME']:
    PREFIX = Constants.PREFIX_CERN
else:
    PREFIX = ''
F_NTUPLE = PREFIX+'/eos/cms/store/user/adasgupt/DisplacedDimuons/NTuples/ntuple_DY100to200.root'
F_SIGNAL = PREFIX+'/eos/cms/store/user/adasgupt/DisplacedDimuons/NTuples/aodOnly_ntuple_HTo2XTo4Mu_125_20_13.root'

def tprint(msg):
    print '\033[32mPRIMITIVES TEST: ' + msg + '\033[m'
def eprint(msg):
    print '\033[31mPRIMITIVES TEST: ' + msg + '\033[m'

f = R.TFile.Open(F_NTUPLE)
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
        'TRIGGER' : [-1, False],
        'MET'     : [-1, False],
        'FILTER'  : [-1, False],
        'VERTEX'  : [-1, False],
        'BEAMSPOT': [-1, False],
        'GEN'     : [-1, False],
        'MUON'    : [-1, False],
        'DSAMUON' : [-1, False],
        'RSAMUON' : [-1, False],
        'DIMUON'  : [-1, False],
}

ErrorMessages = []

LxyTest = []
d0Test  = []

# test collections
for i, event in enumerate(t):
    if i == 100: break
    E = Primitives.ETree(t)
    for KEY in KEYS:
        try:
            Collection = E.getPrimitives(KEY)
            try:
                if len(Collection) > 0:
                    obj = Collection[0]
                    if obj.__class__.__name__ == 'Dimuon':
                        try:
                            x = obj.Lxy()
                        except Exception as e:
                            if e.message not in ErrorMessages:
                                ErrorMessages.append(e.message)
                            if KEY not in LxyTest:
                                LxyTest.append(KEY)
                    if obj.__class__.__name__ == 'RecoMuon':
                        try:
                            x = obj.d0(extrap='LIN')
                            s = obj.d0Sig(vertex='BS')
                        except Exception as e:
                            if e.message not in ErrorMessages:
                                ErrorMessages.append(e.message)
                            if KEY not in d0Test:
                                d0Test.append(KEY)
            except:
                pass
        except Exception as e:
            if e.message not in ErrorMessages:
                ErrorMessages.append(e.message)
            KEYS[KEY][0] = i
            KEYS[KEY][1] = True

if len(ErrorMessages) > 0:
    eprint('Encountered the following error messages:')
    for msg in ErrorMessages:
        eprint('  '+msg)
for KEY in KEYS:
    if not KEYS[KEY][1]:
        tprint('Successfully got all '+KEY+' ...')
    else:
        eprint('Problem getting '+KEY+', see e.g. event '+str(KEYS[KEY][0]))

if len(d0Test) > 0:
    eprint('d0() or d0Sig() failed for: '+' '.join(d0Test))
else:
    tprint('d0() or d0Sig() succeeded for all collections...')

# test signal gen particles
f = R.TFile.Open(F_SIGNAL)
t = f.Get('SimpleNTupler/DDTree')
Primitives.SelectBranches(t, DecList=('GEN',))

Erred = False

for i, event in enumerate(t):
    if i == 10: break
    E = Primitives.ETree(t, DecList=('GEN',))
    mu11 = None
    try:
        mu11, mu12, mu21, mu22, X1, X2, H, P, extramu = E.getPrimitives('GEN', 'HTo2XTo4Mu')
    except:
        Erred = True

    if mu11 is not None:
        obj = mu11
        if obj.__class__.__name__ == 'GenMuon':
            try:
                x = obj.Lxy()
            except Exception as e:
                if e.message not in ErrorMessages:
                    ErrorMessages.append(e.message)
                if KEY not in LxyTest:
                    LxyTest.append(KEY)

if len(LxyTest) > 0:
    eprint('Lxy() failed for: '+' '.join(LxyTest))
else:
    tprint('Lxy() succeeded for all collections...')

if not Erred:
    tprint('Successfully got all 4Mu gen particles...')
else:
    eprint('Problem getting 4Mu gen particles')

tprint('Done.')
