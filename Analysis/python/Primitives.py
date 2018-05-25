import re
import math
import ROOT as R
import DisplacedDimuons.Analysis.RootTools

##########
# This file defines the Primitives classes for ease of access and idiomatic analysis code.
# Seriously, life is much better once you have a list of objects that are actual objects.
# Line breaks are meta-computation -- things you can't get directly from the trees.
##########

BRANCHPREFIXES = {
    'EVENT'    : 'evt_'  ,
    'TRIGGER'  : 'trig_' ,
    'MET'      : 'met_'  ,
    'BEAMSPOT' : 'bs_'   ,
    'VERTEX'   : 'vtx_'  ,
    'GEN'      : 'gen_'  ,
    'MUON'     : 'mu_'   ,
    'DSAMUON'  : 'dsamu_',
    'RSAMUON'  : 'rsamu_',
    'DIMUON'   : 'dim_'  ,
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
 
    def getPrimitives(self, KEY, MCTYPE=None):
        if KEY == 'GEN':
            if MCTYPE == 'HTo2XTo4Mu':
                muons   =             [GenMuon (self, i        ) for i in range(4)                  ]
                mothers =             [Particle(self, i, 'gen_') for i in range(4, 8)               ]
                return muons + mothers
            elif MCTYPE == 'HTo2XTo2Mu2J':
                muons   =             [GenMuon (self, i        ) for i in range(2)                  ]
                jets    =             [GenMuon (self, i        ) for i in range(2, 4)               ]
                mothers =             [Particle(self, i, 'gen_') for i in range(4, 8)               ]
                return muons + jets + mothers
            else:
                return                [Particle(self, i, 'gen_') for i in range(len(self.gen_eta  ))]
        if KEY == 'MUON'     : return [AODMuon (self, i        ) for i in range(len(self.mu_eta   ))]
        if KEY == 'DSAMUON'  : return [RecoMuon(self, i, 'DSA' ) for i in range(len(self.dsamu_eta))]
        if KEY == 'RSAMUON'  : return [RecoMuon(self, i, 'RSA' ) for i in range(len(self.rsamu_eta))]
        if KEY == 'DIMUON'   : return [Dimuon  (self, i        ) for i in range(len(self.dim_eta  ))]
        if KEY == 'VERTEX'   : return Vertex(self)
        if KEY == 'BEAMSPOT' : return Beamspot(self)
        if KEY == 'MET'      : return (self.met_pt, self.met_phi, self.met_gen_pt)
        if KEY == 'EVENT'    : return (self.evt_run, self.evt_lumi, self.evt_event, self.evt_bx)
        raise Exception('Unknown Primitives key '+KEY)

    def get(self, attr, index=None):
        if index is None:
            return getattr(self, attr)
        else:
            return getattr(self, attr)[index]

# The Primitives Classes: take in an ETree and an index, produces an object.
# Base class for primitives
# just provides a wrapper for setting attributes
class Primitive(object):
    def __init__(self):
        pass

    def set(self, attr, E, E_attr, i):
        setattr(self, attr, E.get(E_attr, i))

# Particle class
# sets all the variables, also sets pos, p4, and p3 vectors
class Particle(Primitive):
    def __init__(self, E, i, prefix):
        Primitive.__init__(self)

        # set basic particle variables; see getMissingValues below
        missing = self.getMissingValues(E, i, prefix)
        for attr in ('pt', 'eta', 'phi', 'mass', 'energy', 'charge', 'x', 'y', 'z'):
            if attr in missing:
                setattr(self, attr, missing[attr])
            else:
                self.set(attr, E, prefix+attr, i)

        # set pdgID for gen particles
        if prefix == 'gen_':
            self.set(attr, E, prefix+'pdgID', i)

        # set position TVector3
        self.pos = R.TVector3(self.x, self.y, self.z)

        # set TLorentzVector
        self.p4 = R.TLorentzVector()
        self.p4.SetPtEtaPhiE(self.pt, self.eta, self.phi, self.energy)

        # this is an XYZ 3-vector!
        self.p3 = R.TVector3(*self.p4.Vect())

    # Since the nTuples are no longer guaranteed to have all of the
    # 9 basic particle variables above, so
    # I have to compute them myself from what exists in the tree
    # currently:
    #  - dsamu and rsamu do not have pt, mass, energy, but have px, py, pz
    #  - dim does not have energy, charge, but has mass and p
    def getMissingValues(self, E, i, prefix):
        missing = {}
        if not hasattr(E, prefix+'pt'):
            missing['pt'] = math.sqrt(sum((E.get(prefix+'p'+ii, i)**2. for ii in ('x', 'y'))))
        if not hasattr(E, prefix+'mass'):
            if 'mu' in prefix:
                missing['mass'] = .105658375
            else:
                raise Exception('Mass for prefix '+prefix+' unavailable.')
        if not hasattr(E, prefix+'energy'):
            if hasattr(E, prefix+'p'):
                momentum = E.get(prefix+'p', i)
            else:
                momentum = math.sqrt(sum((E.get(prefix+'p'+ii, i)**2. for ii in ('x', 'y', 'z'))))
            if hasattr(E, prefix+'mass'):
                mass = E.get(prefix+'mass', i)
            else:
                if 'mu' in prefix:
                    mass = missing['mass']
                else:
                    raise Exception('Mass for prefix '+prefix+' unavailable.')
            missing['energy'] = math.sqrt(mass**2. + momentum**2.)
        if not hasattr(E, prefix+'charge'):
            if 'dim' in prefix:
                missing['charge'] = 0.
            else:
                raise Exception('Charge for prefix '+prefix+' unavailable.')
        return missing


# Muon classes
# sets all the particle variables
# base class for several "kinds" of muons, each with different additional branches
# AODMuon     : reco AOD muons from the reco::Muon collection (mu_)
#   .gen      : gen muon matched/attached to the AOD muon     (mu_gen_)
# GenMuon     : gen muons from the GenParticle collection     (gen_)
# RecoMuon    : reco muons from a reco::Track collection
#   ("DSA")   : reco DSA muons from displacedStandAloneMuons  (dsamu_)
#   ("RSA")   : reco RSA muons from refittedStandAloneMuons   (rsamu_)
class Muon(Particle):
    def __init__(self, E, i, prefix):
        Particle.__init__(self, E, i, prefix)

# AODMuon: see above
# note that the gen muon attached to it is of type Muon
class AODMuon(Muon):
    def __init__(self, E, i):
        Muon.__init__(self, E, i, 'mu_')
        self.gen = Muon(E, i, 'mu_gen_')
        for attr in ('isSlim',):
            self.set(attr, E, 'mu_'+attr, i)

# GenMuon: see above
class GenMuon(Muon):
    def __init__(self, E, i):
        Muon.__init__(self, E, i, 'gen_')
        for attr in ('d0', 'd00', 'cosAlpha', 'pairDeltaR'):
            self.set(attr, E, 'gen_'+attr, i)

        # genMuons and dimuons get Lxy with Lxy()
        # so make sure that the name doesn't collide
        self.set('Lxy_', E, 'gen_Lxy', i)

    def Lxy(self):
        return self.Lxy_

# RecoMuon: see above
# the ImpactParameter is a member variable allowing easy access to d0, dz
# and the associated quantities. allow accessing its methods directly on the muon.
class RecoMuon(Muon):
    def __init__(self, E, i, tag):
        if tag == 'DSA':
            prefix = 'dsamu_'
        elif tag == 'RSA':
            prefix = 'rsamu_'
        Muon.__init__(self, E, i, prefix)
        for attr in ('nMuonHits', 'nDTHits', 'nCSCHits', 'nDTStations', 'nCSCStations', 'chi2', 'ndof'):
            self.set(attr, E, prefix+attr, i)
        self.IP = ImpactParameter(E, i, prefix)
        self.normChi2 = self.chi2/self.ndof if self.ndof != 0 else float('inf')

    def __getattr__(self, name):
        if name in ('d0', 'dz', 'd0Sig', 'dzSig'):
            return getattr(self.IP, name)
        raise AttributeError('\'RecoMuon\' object has no attribute \''+name+'\'')

# impact parameter wrapper class for
# d0 and dz, their significances,
# and wrt PV or BS, with LIN extrapolation or default
class ImpactParameter(Primitive):
    def __init__(self, E, i, prefix):
        Primitive.__init__(self)
        for axis in ('d0', 'dz'):
            for val in ('_', 'sig_'):
                for vertex in ('pv', 'bs'):
                    for extrap in ('', '_lin'):
                        attr = axis+val+vertex+extrap
                        self.set(attr, E, prefix+attr, i)

    # axis should be either d0 or dz
    # val should be either None or SIG
    # vertex should be either PV/pv or BS/bs
    # extrap should be either LIN/lin or None
    def getValue(self, axis, val, vertex, extrap):
        if axis not in ('d0', 'dz'):
            raise Exception('"axis" argument should be either d0 or dz')
        if val is None:
            val = '_'
        else:
            val = val.lower() + '_'
        if val not in ('_', 'sig_'):
            raise Exception('"val" argument should be either None or LIN')
        vertex = vertex.lower()
        if vertex not in ('pv', 'bs'):
            raise Exception('"vertex" argument should be either PV or BS')
        if extrap is None:
            extrap = ''
        else:
            extrap = '_' + extrap.lower()
        if extrap not in ('', '_lin'):
            raise Exception('"extrap" argument should be either None or LIN')
        return getattr(self, axis+val+vertex+extrap)

    def d0   (self, vertex='PV', extrap=None): return self.getValue('d0', None , vertex, extrap)
    def dz   (self, vertex='PV', extrap=None): return self.getValue('dz', None , vertex, extrap)
    def d0Sig(self, vertex='PV', extrap=None): return self.getValue('d0', 'SIG', vertex, extrap)
    def dzSig(self, vertex='PV', extrap=None): return self.getValue('dz', 'SIG', vertex, extrap)

# Dimuon class
class Dimuon(Particle):
    def __init__(self, E, i):
        Particle.__init__(self, E, i, 'dim_')
        for attr in ('idx1', 'idx2', 'normChi2', 'deltaR', 'deltaPhi', 'cosAlpha'):
            self.set(attr, E, 'dim_'+attr, i)
        self.Lxy_ = TransverseDecayLength(E, i, 'dim_')

    def __getattr__(self, name):
        if name in ('Lxy', 'LxySig'):
            return getattr(self.Lxy_, name)
        raise AttributeError('\'Dimuon\' object has no attribute \''+name+'\'')

# Lxy wrapper class for Lxy and its significance
# and wrt PV or BS
class TransverseDecayLength(Primitive):
    def __init__(self, E, i, prefix):
        Primitive.__init__(self)
        for val in ('_', 'Sig_'):
            for vertex in ('pv', 'bs'):
                attr = 'Lxy'+val+vertex
                self.set(attr, E, prefix+attr, i)

    # val should be either None or SIG
    # vertex should be either PV/pv or BS/bs
    def getValue(self, val, vertex):
        if val is None:
            val = '_'
        else:
            val = val.title() + '_'
        if val not in ('_', 'Sig_'):
            raise Exception('"val" argument should be either None or SIG')
        vertex = vertex.lower()
        if vertex not in ('pv', 'bs'):
            raise Exception('"vertex" argument should be either PV or BS')
        return getattr(self, 'Lxy'+val+vertex)

    def Lxy   (self, vertex='PV'): return self.getValue(None , vertex)
    def LxySig(self, vertex='PV'): return self.getValue('SIG', vertex)

# Vertex class
# tree only saves primary vertex and nVtx
class Vertex(Primitive):
    def __init__(self, E):
        Primitive.__init__(self)
        for attr in ('x', 'y', 'z', 'dx', 'dy', 'dz', 'chi2', 'ndof', 'ntrk'):
            setattr(self, attr, E.get('vtx_pv_'+attr))
        setattr(self, 'nvtx', E.get('vtx_nvtx'))

        self.pos = R.TVector3(self.x , self.y , self.z )
        self.err = R.TVector3(self.dx, self.dy, self.dz)

# Beamspot class
class Beamspot(Primitive):
    def __init__(self, E):
        Primitive.__init__(self)
        for attr in ('x', 'y', 'z', 'dx', 'dy', 'dz'):
            setattr(self, attr, E.get('bs_'+attr))

        self.pos = R.TVector3(self.x , self.y , self.z )
        self.err = R.TVector3(self.dx, self.dy, self.dz)
