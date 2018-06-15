import os
import ROOT as R
import DisplacedDimuons.Analysis.Primitives as Primitives
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Common.Constants as Constants

# if not on lxplus, add a root protocol
if not 'lxplus' in os.environ['HOSTNAME']:
    PREFIX = Constants.PREFIX_CERN
else:
    PREFIX = ''
F_SIGNAL = PREFIX+'/eos/cms/store/user/adasgupt/DisplacedDimuons/NTuples/aodOnly_ntuple_HTo2XTo4Mu_125_20_13.root'

def tprint(msg):
    print '\033[32mSELECTIONS TEST: ' + msg + '\033[m'
def eprint(msg):
    print '\033[31mSELECTIONS TEST: ' + msg + '\033[m'

f = R.TFile.Open(F_SIGNAL)
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
    'ACCEPTANCE' : False,
    'MUON'       : False,
    'DIMUON'     : False,
}

ErrorMessages = []

# test collections
for i, event in enumerate(t):
    if i == 10: break
    E = Primitives.ETree(t, DecList=('GEN', 'DSAMUON', 'DIMUON'))

    Gens     = E.getPrimitives('GEN', 'HTo2XTo4Mu')
    DSAMuons = E.getPrimitives('DSAMUON')
    Dimuons  = E.getPrimitives('DIMUON')

    mu11, mu12 = Gens[0], Gens[1]

    try:
        accSel = Selections.AcceptanceSelection(mu11)
        accSel = Selections.AcceptanceSelection((mu11, mu12))
    except Exception as e:
        if e.message not in ErrorMessages:
            ErrorMessages.append(e.message)
        KEYS['ACCEPTANCE'] = True

    if len(Dimuons) > 0:
        dim = Dimuons[0]
        mu1, mu2 = DSAMuons[dim.idx1], DSAMuons[dim.idx2]
        try:
            dimSel = Selections.DimuonSelection(dim)
        except Exception as e:
            if e.message not in ErrorMessages:
                ErrorMessages.append(e.message)
            KEYS['DIMUON'] = True
        try:
            mu1Sel = Selections.MuonSelection(mu1)
            mu2Sel = Selections.MuonSelection(mu2)
        except Exception as e:
            if e.message not in ErrorMessages:
                ErrorMessages.append(e.message)
            KEYS['MUON'] = True

if len(ErrorMessages) > 0:
    eprint('Encountered the following error messages:')
    for msg in ErrorMessages:
        eprint('  '+msg)

for KEY in KEYS:
    if not KEYS[KEY]:
        tprint('Successfully selected all '+KEY+' ...')
    else:
        eprint('Problem selecting '+KEY)
tprint('Done.')
