import re
import math
import ROOT as R
import DisplacedDimuons.Analysis.RootTools
import DisplacedDimuons.Common.Constants as Constants

#COLORON = True
COLORON = False

##########
# This file defines the Primitives classes for ease of access and idiomatic analysis code.
# Life is much better once you have a list of objects that are actual objects.
##########

# Print strings
def colorText(text, color=95):
    if not COLORON:
        return text
    if color == 'red':
        color = 91
    elif color == 'green':
        color = 92
    elif color == 'blue':
        color = 94
    elif color == 'pink':
        color = 95
    return '\033[1m\033[{COLOR}m{TEXT}\033[0m:'.format(COLOR=color, TEXT=text)

# Branch keys and corresponding prefixes
# Stored as a tuple of tuples so that the order can be preserved
BRANCHCONFIG = (
    ('EVENT'    , 'evt_'  ),
    ('TRIGGER'  , 'trig_' ),
    ('MET'      , 'met_'  ),
    ('FILTER'   , 'flag_' ),
    ('BEAMSPOT' , 'bs_'   ),
    ('VERTEX'   , 'vtx_'  ),
    ('GEN'      , 'gen_'  ),
    ('PATMUON'  , 'patmu_'),
    ('DSAMUON'  , 'dsamu_'),
    ('RSAMUON'  , 'rsamu_'),
    ('DIMUON'   , 'dim_'  ),
)
BRANCHPREFIXES = dict(BRANCHCONFIG)
BRANCHKEYS = tuple([key for key,val in BRANCHCONFIG])

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
    # initialize the ETree: copy all branches from the tree
    def __init__(self, t, DecList=BRANCHKEYS):
        # save the DecList and the TTree just in case
        # DecList is a list comprehension so as to preserve the same order as BRANCHKEYS
        self.DecList = [key for key in BRANCHKEYS if key in DecList]
        self.TTree   = t

        BranchList = [str(br.GetName()) for br in list(t.GetListOfBranches())]
        for KEY in DecList:
            for br in BranchList:
                if re.match(BRANCHPREFIXES[KEY], br):
                    self.copyBranch(br)

    # this function copies the contents of t into the ETree
    # and makes a Python list from a vector if appropriate
    def copyBranch(self, branch):
        name = type(getattr(self.TTree, branch)).__name__
        if 'vector' in name:
            if 'vector<vector<' in name:
                setattr(self, branch, [list(subvector) for subvector in list(getattr(self.TTree, branch))])
            else:
                setattr(self, branch, list(getattr(self.TTree, branch)))
        else:
            setattr(self, branch, getattr(self.TTree, branch))

    # this function creates a list of Primitives objects given a tag
    # it should be called for each analysis object, once per event (after the ETree is declared)
    def getPrimitives(self, KEY):
        if not KEY in self.DecList:
            raise Exception('Branch key "{}" not found in ETree; did you forget to add it to the DecList?'.format(KEY))

        if KEY == 'EVENT'    : return Event       (self)
        if KEY == 'TRIGGER'  :
            if not hasattr(self, 'trig_hlt_idx'):
                raise Exception('Sample does not contain Trigger branches; tree must be made from PAT Tuple')
            HLTPaths =                [HLTPath    (self, i)                for i in range(len(self.trig_hlt_idx  ))]
            HLTMuons =                [TriggerMuon(self, i, 'trig_hltmu_') for i in range(len(self.trig_hltmu_idx))]
            L1TMuons =                [TriggerMuon(self, i, 'trig_l1tmu_') for i in range(len(self.trig_l1tmu_idx))]
            return                    HLTPaths, HLTMuons, L1TMuons
        if KEY == 'MET'      :
            if not hasattr(self, 'met_pt'):
                raise Exception('Sample does not contain MET branches; tree must be made from PAT Tuple')
            return                    MET         (self)
        if KEY == 'FILTER'   :
            if not hasattr(self, 'flag_PhysicsDeclared'):
                raise Exception('Sample does not contain MET Filters; tree must be made from PAT Tuple')
            return                    Filters     (self)
        if KEY == 'BEAMSPOT' : return Beamspot    (self)
        if KEY == 'VERTEX'   : return Vertex      (self)
        if KEY == 'GEN':
            if not hasattr(self, 'gen_eta'):
                raise Exception('Sample does not contain GenParticle branches; cannot get GenParticle primitives for Data')
            # automatically detect whether this sample is HTo2XTo2Mu2J, HTo2XTo4Mu, or Background
            # if the LLX pdgID is in the list of pdg IDs, it's a signal sample
            # then check if the third element is a muon: if it is, then it's 4Mu, otherwise it's 2Mu2J
            # otherwise, it's a background sample
            # Signal
            if Constants.LLX_PDGID in self.gen_pdgID:
                # 2Mu2J
                if abs(self.gen_pdgID[2]) != Constants.ABS_MUON_PDGID:
                    muons   =         [GenMuon    (self, i, True  )        for i in range(2)                       ]
                    jets    =         [GenMuon    (self, i        )        for i in range(2, 4)                    ]
                    mothers =         [GenParticle(self, i        )        for i in range(4, 8)                    ]
                    extramu =         []
                    if len(self.gen_eta) > 8:
                        extramu =     [GenMuon    (self, i        )        for i in range(8, len(self.gen_eta    ))]
                    return muons + jets + mothers + [extramu]
                # 4Mu
                else:
                    muons   =         [GenMuon    (self, i, True  )        for i in range(4)                       ]
                    mothers =         [GenParticle(self, i        )        for i in range(4, 8)                    ]
                    extramu =         []
                    if len(self.gen_eta) > 8:
                        extramu =     [GenMuon    (self, i        )        for i in range(8, len(self.gen_eta    ))]
                    return muons + mothers + [extramu]
            # Background
            else:
                return                [GenParticle(self, i        )        for i in range(len(self.gen_eta       ))]
        if KEY == 'PATMUON'  : return [RecoMuon   (self, i, 'PAT' )        for i in range(len(self.patmu_eta     ))]
        if KEY == 'DSAMUON'  : return [RecoMuon   (self, i, 'DSA' )        for i in range(len(self.dsamu_eta     ))]
        if KEY == 'RSAMUON'  : return [RecoMuon   (self, i, 'RSA' )        for i in range(len(self.rsamu_eta     ))]
        if KEY == 'DIMUON'   : return [Dimuon     (self, i        )        for i in range(len(self.dim_eta       ))]
        raise Exception('Unknown Primitives key '+KEY)

    # this function is syntactic sugar:
    # E.get('evt_event') instead of getattr(E, 'evt_event'), and
    # E.get('gen_pt', i) instead of getattr(E, 'gen_pt')[i]
    def get(self, attr, index=None):
        if index is None:
            return getattr(self, attr)
        else:
            return getattr(self, attr)[index]

    # ETree print function
    # gets all of the Primitives, loops over them, and prints out their individual information
    # For Primitives that are lists, printing the header is handled specially, so that it only prints once per event
    # instead of once per object
    def __str__(self):
        outstr = '\n=======================================================\n'

        for key in self.DecList:

            primitives = self.getPrimitives(key)

            if key == 'TRIGGER':
                HLTPaths, HLTMuons, L1TMuons = primitives
                outstr += colorText('HLT Paths') + '\n'
                for hltpath in HLTPaths: outstr += str(hltpath)

                outstr += '\n'

                outstr += colorText('Trigger Muons') + '\n'
                if len(L1TMuons) + len(HLTMuons) > 0:
                    outstr += TriggerMuon.headerstr()
                    if len(L1TMuons) > 0:
                        outstr += colorText('L1T Muons', color='blue') + '\n'
                        for trigmuon in L1TMuons: outstr += trigmuon.datastr()
                    if len(HLTMuons) > 0:
                        outstr += colorText('HLT Muons', color='blue') + '\n'
                        for trigmuon in HLTMuons: outstr += trigmuon.datastr()

                outstr += '\n'

            elif key == 'GEN':
                outstr += colorText('Gen Particles') + '\n'
                outstr += GenMuon.headerstr()
                for particle in primitives:
                    if isinstance(particle, list):
                        outstr += '{} Extra Muons in event\n'.format(len(particle))
                        for mu in particle:
                            outstr += mu.datastr()
                    else:
                        outstr += particle.datastr()
                outstr +='\n'

            elif key == 'PATMUON':
                outstr += colorText('PAT Muons') + '\n'
                if len(primitives) > 0:
                    outstr += PATMuon.headerstr()
                    for particle in primitives:
                        outstr += particle.datastr()
                outstr +='\n'

            elif key == 'DSAMUON' or key == 'RSAMUON':
                outstr += colorText(key[:3] + ' Muons') + '\n'
                if len(primitives) > 0:
                    for i in (1, 2, 3):
                        outstr += RecoMuon.headerstr(i)
                        for particle in primitives:
                            outstr += particle.datastr(i)
                outstr += '\n'

            elif key == 'DIMUON':
                outstr += colorText('Dimuons') + '\n'
                if len(primitives) > 0:
                    for particle in primitives:
                        outstr += str(particle)
                outstr += '\n'

            else:
                # is iterable
                # this probably does not occur because all of the iterable keys
                # are explicitly handled above
                try:
                    for primitive in primitives:
                        outstr += str(primitive) + '\n'
                # isn't iterable
                except TypeError:
                    outstr += str(primitives)  + '\n'
        return outstr

# The Primitives Classes: take in an ETree and an index, produces an object.
# Base class for primitives
# set() just provides a wrapper for setting attributes
# I am choosing not to pass an extra "cast" parameter to it, wrapping cast(E.get)
# for any chosen target function (int, bool, etc.), even though it would
# simplify the declaration of the Filters object, because I don't want yet another
# function call that is never used except in that one case
class Primitive(object):
    def __init__(self):
        pass

    def set(self, attr, E, E_attr, index=None):
        setattr(self, attr, E.get(E_attr, index))

    def __str__(self):
        outstr = colorText(self.__class__.__name__) + '\n'
        maxAttrLen = max([len(attr) for attr in self.__dict__.keys()])
        for attr in self.__dict__.keys():
            data = self.__dict__[attr]

            # format booleans in a nice way
            if isinstance(data, bool):
                # print in green
                if data:
                    data = colorText(str(data), color='green').replace(':', '')
                # print in red
                else:
                    data = colorText(str(data), color='red').replace(':', '')
            else:
                data = str(data)

            outstr += '{ATTR:{W}s}: {DATA} \n'.format(ATTR=attr, W=maxAttrLen, DATA=data)
        return outstr

# Event class
class Event(Primitive):
    def __init__(self, E):
        Primitive.__init__(self)
        for attr in ('run', 'lumi', 'event', 'bx'):
            self.set(attr, E, 'evt_'+attr)
        # for simplicity reasons the gen_weight and gen_tnpv branches
        # are stored with prefix gen_, but they are per event so should be stored here
        if hasattr(E, 'gen_weight'):
            self.set('weight', E, 'gen_weight')
        if hasattr(E, 'gen_tnpv'):
            self.set('nTruePV', E, 'gen_tnpv')

    def __str__(self):
        outstr = colorText(self.__class__.__name__) + '\n'
        maxAttrLen = max([len(attr) for attr in self.__dict__.keys()])
        for attr in ('run', 'lumi', 'event', 'bx', 'weight', 'nTruePV'):
            data = self.__dict__[attr]

            # format booleans in a nice way
            if isinstance(data, bool):
                # print in green
                if data:
                    data = colorText(str(data), color='green').replace(':', '')
                # print in red
                else:
                    data = colorText(str(data), color='red').replace(':', '')
            else:
                data = str(data)

            outstr += '{ATTR:{W}s}: {DATA} '.format(ATTR=attr, W=maxAttrLen, DATA=data)

        outstr += '\n'
        return outstr

# MET class
class MET(Primitive):
    def __init__(self, E):
        Primitive.__init__(self)
        for attr in ('pt', 'phi', 'gen_pt'):
            self.set(attr, E, 'met_'+attr)

    def __str__(self):
        outstr = colorText(self.__class__.__name__) + '   '
        for attr in ('pt', 'phi', 'gen_pt'):
            outstr += '{}: {:3.3f}    '.format(attr, self.__dict__[attr])
        outstr += '\n'
        return outstr

# MET filter class
class Filters(Primitive):
    def __init__(self, E):
        Primitive.__init__(self)
        for attr in Filters.FILTERLIST:
            self.set(attr, E, 'flag_'+attr)
            setattr(self, attr, bool(getattr(self, attr)))

    FILTERLIST = (
        'PhysicsDeclared',
        'PrimaryVertexFilter',
        'AllMETFilters',
        'HBHENoiseFilter',
        'HBHEIsoNoiseFilter',
        'CSCTightHaloFilter',
        'EcalTPFilter',
        'EeBadScFilter',
        'BadPFMuonFilter',
        'BadChargedCandidateFilter'
    )

    def __str__(self):
        outstr = colorText(self.__class__.__name__) + '\n'
        maxAttrLen = max([len(attr) for attr in self.__dict__.keys()])
        for attr in Filters.FILTERLIST:
            data = self.__dict__[attr]

            # format booleans in a nice way
            if isinstance(data, bool):
                # print in green
                if data:
                    data = colorText(str(data), color='green').replace(':', '')
                # print in red
                else:
                    data = colorText(str(data), color='red').replace(':', '')
            else:
                data = str(data)

            outstr += '{ATTR:{W}s}: {DATA} \n'.format(ATTR=attr, W=maxAttrLen, DATA=data)
        return outstr

# Trigger classes
# There are 3 distinct objects:
#  - the list of HLT paths, HLT and L1T prescales
#  - the list of HLT muons
#  - the list of L1T muons
# Define an HLTPath object, and a TriggerMuon object
# The TriggerMuon will not derive from Particle; it is too different
# But it can have a fairly similar interface

# HLTPath class
class HLTPath(Primitive):
    def __init__(self, E, i):
        Primitive.__init__(self)
        for prettyattr, attr in zip(('idx', 'name', 'HLTPrescale', 'L1TPrescale'), ('hlt_idx', 'hlt_path', 'hlt_prescale', 'l1t_prescale')):
            self.set(prettyattr, E, 'trig_'+attr, i)

# TriggerMuon class
class TriggerMuon(Primitive):
    def __init__(self, E, i, prefix):
        Primitive.__init__(self)
        if 'l1tmu' in prefix:
            self.trigger = 'L1T'
        elif 'hltmu' in prefix:
            self.trigger = 'HLT'
        for attr in ('idx', 'px', 'py', 'pz', 'eta', 'phi'):
            self.set(attr, E, prefix+attr, i)

        triggerMuonEnergy = math.sqrt(sum([x**2. for x in (self.px, self.py, self.pz)]) + 0.105658375**2.)
        self.p4 = R.TLorentzVector()
        self.p4.SetPxPyPzE(self.px, self.py, self.pz, triggerMuonEnergy) 

        self.p3 = R.TVector3(self.px, self.py, self.pz)
        self.pt = math.sqrt(self.px**2. + self.py**2.)

    # idx, trigger, pt, px, py, pz, eta, phi
    headerFormat = '|{:4s}|{:8s}|{:9s}|{:9s}|{:9s}|{:9s}|{:9s}|{:9s}|\n'
    dataFormat   = '|{:4d}|{:8s}|{:9.3f}|{:9.3f}|{:9.3f}|{:9.3f}|{:9.3f}|{:9.3f}|\n'

    # so that we don't need an instance of the class to call this method
    @staticmethod
    def headerstr():
        return TriggerMuon.headerFormat.format('idx', 'trigger', 'pt', 'px', 'py', 'pz', 'eta', 'phi')

    def datastr(self):
        return TriggerMuon.dataFormat.format(self.idx, self.trigger, self.pt, self.px, self.py, self.pz, self.eta, self.phi)

    def __str__(self):
        return TriggerMuon.headerstr() + self.datastr()

# Beamspot class
class Beamspot(Primitive):
    def __init__(self, E):
        Primitive.__init__(self)
        for attr in ('x', 'y', 'z', 'dx', 'dy', 'dz'):
            self.set(attr, E, 'bs_'+attr)

        self.pos = R.TVector3(self.x , self.y , self.z )
        self.err = R.TVector3(self.dx, self.dy, self.dz)

    def __str__(self):
        outstr = colorText(self.__class__.__name__) + '\n'
        outstr += 'x +/- dx = {:6.3f} +/- {:6.3f} [cm]\n'.format(self.x, self.dx)
        outstr += 'y +/- dy = {:6.3f} +/- {:6.3f} [cm]\n'.format(self.y, self.dy)
        outstr += 'z +/- dz = {:6.3f} +/- {:6.3f} [cm]\n'.format(self.z, self.dz)
        return outstr

# Vertex class
# tree only saves primary vertex and nVtx
class Vertex(Primitive):
    def __init__(self, E):
        Primitive.__init__(self)
        for attr in ('x', 'y', 'z', 'dx', 'dy', 'dz', 'chi2', 'ndof', 'ntrk'):
            self.set(attr, E, 'vtx_pv_'+attr)
        self.set('nvtx', E, 'vtx_nvtx')

        self.pos = R.TVector3(self.x , self.y , self.z )
        self.err = R.TVector3(self.dx, self.dy, self.dz)

    def __str__(self):
        outstr = colorText(self.__class__.__name__) + '\n'
        outstr += 'nvtx = {:d}    ntrk: {:d}    chi2/ndf: {:3.2f}/{:3.2f} = {:3.2f}\n'.format(self.nvtx, self.ntrk, self.chi2, self.ndof, self.chi2/self.ndof)
        outstr += 'x +/- dx = {:6.3f} +/- {:6.3f} [cm]\n'.format(self.x, self.dx)
        outstr += 'y +/- dy = {:6.3f} +/- {:6.3f} [cm]\n'.format(self.y, self.dy)
        outstr += 'z +/- dz = {:6.3f} +/- {:6.3f} [cm]\n'.format(self.z, self.dz)
        return outstr

# Things start to get more complicated here...
# We have several kinds of particle-like objects
# Define a base Particle class that has 9 basic particle variables
# Then derive all particle-like objects from it

# Particle class
# sets all the variables, also sets pos, p4, and p3 vectors
class Particle(Primitive):
    def __init__(self, E, i, prefix):
        Primitive.__init__(self)

        # fill px py pz if available
        for attr in ('px', 'py', 'pz', 'p'):
            if hasattr(E, prefix+attr):
                self.set(attr, E, prefix+attr, i)

        # set basic particle variables; see getMissingValues below
        missing = self.getMissingValues(E, i, prefix)
        for attr in ('pt', 'eta', 'phi', 'mass', 'energy', 'charge', 'x', 'y', 'z'):
            if attr in missing:
                setattr(self, attr, missing[attr])
            else:
                self.set(attr, E, prefix+attr, i)

        # set position TVector3
        self.pos = R.TVector3(self.x, self.y, self.z)

        # set TLorentzVector
        self.p4 = R.TLorentzVector()
        self.p4.SetPtEtaPhiE(self.pt, self.eta, self.phi, self.energy)

        # this is an XYZ 3-vector!
        self.p3 = R.TVector3(*self.p4.Vect())
        if not hasattr(self, 'p'):
            self.p = self.p3.Mag()

    # Since the nTuples are no longer guaranteed to have all of the
    # 9 basic particle variables above
    # I have to compute them myself from what exists in the tree
    # currently:
    #  - dsamu, rsamu, dim_mu* do not have pt, mass, energy, but have px, py, pz
    #  - dim does not have energy, charge, but has mass and p
    #  - dim_mu* do not have x, y, z, but they are the same as dim_x, dim_y, dim_z
    #  - gen_bs does not have mass, charge, but they are the same as gen_mass, gen_charge
    def getMissingValues(self, E, i, prefix):
        missing = {}
        if not hasattr(E, prefix+'pt'):
            missing['pt'] = math.sqrt(sum((E.get(prefix+'p'+ii, i)**2. for ii in ('x', 'y'))))
        if not hasattr(E, prefix+'mass'):
            if 'mu' in prefix:
                missing['mass'] = .105658375
            elif 'gen_bs' in prefix:
                missing['mass'] = E.get('gen_mass', i)
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
            elif 'gen_bs' in prefix:
                missing['charge'] = E.get('gen_charge', i)
            else:
                raise Exception('Charge for prefix '+prefix+' unavailable.')
        if not hasattr(E, prefix+'x'):
            if 'dim_mu' in prefix:
                missing['x'] = E.get('dim_x', i)
                missing['y'] = E.get('dim_y', i)
                missing['z'] = E.get('dim_z', i)
            else:
                raise Exception('xyz for prefix '+prefix+' unavailable.')
        return missing

    # p, pt, eta, phi, mass, energy, q, (x,y,z);
    headerFormat = '|{:9s}|{:9s}|{:10s}|{:7s}|{:10s}|{:10s}|{:6s}|{:^24s}|\n'
    dataFormat   = '|{:9.2f}|{:9.2f}|{:10.2f}|{:7.2f}|{:10.2f}|{:10.2f}|{:6d}|{:8.2f}{:8.2f}{:8.2f}|\n'

    # so that we don't need an instance of the class to call this method
    @staticmethod
    def headerstr():
        return Particle.headerFormat.format(
            'p', 'pt', 'eta', 'phi', 'mass', 'energy', 'charge', '(x,y,z)')

    def datastr(self):
        return Particle.dataFormat.format(
            self.p, self.pt, self.eta, self.phi, self.mass, self.energy, int(self.charge), self.x, self.y, self.z)

    def __str__(self):
        return Particle.headerstr() + self.datastr()

# GenParticle class
# just like Particle, but also sets gen info: pdgID, status, and mother
class GenParticle(Particle):
    def __init__(self, E, i):
        Particle.__init__(self, E, i, 'gen_')

        # set gen info for gen particles
        for attr in ('pdgID', 'status', 'mother'):
            self.set(attr, E, 'gen_'+attr, i)

    # pdgID, status, mother
    headerFormatPre = '|{:7s}|{:6s}|{:5s}'
    dataFormatPre   = '|{:7d}|{:6d}|{:5d}'

    # so that we don't need an instance of the class to call this method
    @staticmethod
    def headerstr():
        return GenParticle.headerFormatPre.format('pdgID', 'stat', 'mom') + Particle.headerstr()

    def datastr(self):
        return GenParticle.dataFormatPre.format(self.pdgID, self.status, self.mother) + Particle.datastr(self)

    def __str__(self):
        return GenParticle.headerstr() + self.datastr()

# Muon classes
# sets all the particle variables
# base class for several "kinds" of muons, each with different additional branches
# GenMuon        : gen muons from the GenParticle collection      (gen_)
# RecoMuon       : reco muons from a reco::Track collection
#   ("DSA")      : reco DSA muons from displacedStandAloneMuons   (dsamu_)
#   ("RSA")      : reco RSA muons from refittedStandAloneMuons    (rsamu_)
#   ("PAT")      : reco PAT muons from patMuons                   (patmu_)
#     .gen       : gen muon matched/attached to the PAT muon      (patmu_gen_)
#   ("DIM_REF1") : reco DSA/PAT muons from refitted dimuon tracks (dim_mu1_)
#   ("DIM_REF2") : reco DSA/PAT muons from refitted dimuon tracks (dim_mu2_)
class Muon(Particle):
    def __init__(self, E, i, prefix):
        Particle.__init__(self, E, i, prefix)

# GenMuon: see above
class GenMuon(Muon, GenParticle):
    def __init__(self, E, i, isSignal=False):
        Muon.__init__(self, E, i, 'gen_')
        GenParticle.__init__(self, E, i)

        # genMuons and reco muons get d0 with d0()
        # so make sure that the name doesn't collide
        self.set('d0_' , E, 'gen_d0' , i)
        self.set('dz_' , E, 'gen_dz' , i)

        # get the gen quantities with respect to beamspot
        self.BS = Particle(E, i, 'gen_bs_')
        setattr(self.BS, 'd0_' , E.get('gen_bs_d0', i))
        setattr(self.BS, 'dz_' , E.get('gen_bs_dz', i))

        # explicit set d0 to positive for now until
        # we can figure out what to do with the sign
        self.d0_    = abs(self.d0_)
        self.dz_    = abs(self.dz_)
        self.BS.d0_ = abs(self.BS.d0_)
        self.BS.dz_ = abs(self.BS.dz_)

        # these three quantities are specific to signal gen muons
        if isSignal:
            for attr in ('cosAlpha', 'deltaR'):
                self.set(attr, E, 'gen_'+attr, i)

            # genMuons and dimuons get Lxy with Lxy()
            # so make sure that the name doesn't collide
            self.set('Lxy_', E, 'gen_Lxy', i)
        # other gen muons don't have them, so set them to a dummy value
        else:
            for attr in ('cosAlpha', 'deltaR', 'Lxy_'):
                setattr(self, attr, -999.)

    # access functions
    def Lxy(self):
        return self.Lxy_
    def d0(self, vertex='BS', extrap='LIN'):
        if extrap == 'LIN':
            return self.d0_
        else:
            return self.BS.d0_
    def dz(self, vertex='BS', extrap='LIN'):
        if extrap == 'LIN':
            return self.dz_
        else:
            return self.BS.dz_

    # Lxy, cosAlpha, d0, dz, dR
    headerFormatPost = '{:8s}|{:8s}|{:8s}|{:8s}|{:7s}|\n'
    dataFormatPost   = '{:8.2f}|{:8.3f}|{:8.2f}|{:8.2f}|{:7.2f}|\n'

    # so that we don't need an instance of the class to call this method
    @staticmethod
    def headerstr(line=1):
        if line == 1:
            # take care of the \n
            return GenParticle.headerstr().strip('\n') + GenMuon.headerFormatPost.format('Lxy', 'cosAlpha', 'd0', 'dz', 'dR')

    def datastr(self):
        outstr = GenParticle.datastr(self).strip('\n') + GenMuon.dataFormatPost.format(self.Lxy_, self.cosAlpha, self.d0_, self.dz_, self.deltaR)
        outstr += GenParticle.headerFormatPre.format('', '', 'bs') + self.BS.datastr().strip('\n') + GenMuon.dataFormatPost.format(-999.,-999., self.BS.d0_, self.BS.dz_,-999.)
        return outstr

    def __str__(self):
        return GenMuon.headerstr() + self.datastr()

# RecoMuon: see above
# the ImpactParameter is a member variable allowing easy access to d0, dz
# and the associated quantities. allow accessing its methods directly on the muon.
# for PAT muons, note that the gen muon attached to it is of type Muon
class RecoMuon(Muon):
    def __init__(self, E, i, tag):
        TAGDICT = {
            'DSA'      : 'dsamu_',
            'RSA'      : 'rsamu_',
            'PAT'      : 'patmu_',
            'DIM_REF1' : 'dim_mu1_',
            'DIM_REF2' : 'dim_mu2_',
        }
        prefix = TAGDICT[tag]
        Muon.__init__(self, E, i, prefix)

        self.tag = tag

        # all reco muons have idx, ptError, and impact parameter
        self.set('idx', E, prefix+'idx', i)
        self.set('ptError', E, prefix+'ptError', i)
        self.IP = ImpactParameter(E, i, prefix)

        # only PAT, DSA, and RSA have these attributes
        if tag in ('DSA', 'RSA', 'PAT'):
            for attr in ('nMuonHits', 'nDTHits', 'nCSCHits', 'nDTStations', 'nCSCStations', 'chi2', 'ndof'):
                self.set(attr, E, prefix+attr, i)
            self.normChi2 = self.chi2/self.ndof if self.ndof != 0 else float('inf')
        # only DSA and RSA have these attributes
        if tag in ('DSA', 'RSA'):
            for attr in ('x_fhit', 'y_fhit', 'z_fhit'):
                self.set(attr, E, prefix+attr, i)
            self.fhit = R.TVector3(self.x_fhit, self.y_fhit, self.z_fhit)
        # only PAT has these attributes
        if tag in ('PAT',):
            self.gen = None
            if E.get('patmu_gen_energy', i) > 0.:
                self.gen = Muon(E, i, 'patmu_gen_')
            for attr in ('nMatchedStations', 'isGlobal', 'isTracker', 'nPixelHits', 'nTrackerHits', 'nTrackerLayers', 'trackIso', 'ecalIso', 'hcalIso'):
                self.set(attr, E, prefix+attr, i)
            self.set('hitPurity', E, prefix+'hpur', i)
            for attr in ('isGlobal', 'isTracker'):
                setattr(self, attr, bool(getattr(self, attr)))
        # only DSA has these attributes
        if tag in ('DSA',):
            for attr in ('idx_ProxMatch', 'idx_SegMatch', 'deltaR_ProxMatch'):
                self.set(attr, E, prefix+attr, i)
            if     self.idx_ProxMatch    < 0   : self.idx_ProxMatch    = None
            if len(self.idx_SegMatch)   == 0   : self.idx_SegMatch     = None
            if     self.deltaR_ProxMatch > 500.: self.deltaR_ProxMatch = float('inf')
        # only refitted muons have these attributes
        if 'REF' in tag:
            if self.idx > 999:
                for attr in ('hitsBeforeVtx', 'missingHitsAfterVtx'):
                    self.set(attr, E, prefix+attr, i)

    def __getattr__(self, name):
        if name in ('d0', 'dz', 'd0Sig', 'dzSig', 'd0Err', 'dzErr'):
            return getattr(self.IP, name)
        raise AttributeError('\'RecoMuon\' object has no attribute \''+name+'\'')

    # idx
    headerFormatPre = '|{:3s}'
    dataFormatPre   = '|{:3d}'

    # nMuonHits, nDTHits, nCSCHits, nDTStations, nCSCStations, chi2, ndof, x_fhit, y_fhit, z_fhit
    headerFormatExtra = '|{:10s}|{:8s}|{:8s}|{:14s}|{:14s}|{:9s}|{:9s}|{:^27s}|\n'
    dataFormatExtra   = '|{:10d}|{:8d}|{:8d}|{:14d}|{:14d}|{:9.2f}|{:9.2f}|{:9.2f}{:9.2f}{:9.2f}|\n'

    # ptError, d0, dz, d0Sig, dzSig
    headerFormatPost = '{:8s}|\n'
    dataFormatPost   = '{:8.2f}|\n'

    @staticmethod
    def headerstr(line=1):
        if line == 1:
            return RecoMuon.headerFormatPre.format('idx') +\
                   Particle.headerstr().strip('\n')     +\
                   RecoMuon.headerFormatPost.format('ptErr')
        elif line == 2:
            return RecoMuon.headerFormatExtra.format(
                'nMuonHits', 'nDTHits', 'nCSCHits', 'nDTStations', 'nCSCStations', 'chi2', 'ndof', '(x_fhit, y_fhit, z_fhit)')
        elif line == 3:
            return ImpactParameter.headerstr()
        else:
            return ''

    def datastr(self, line=1):
        if line == 1:
            return RecoMuon.dataFormatPre.format(self.idx) +\
                   Particle.datastr(self).strip('\n')    +\
                   RecoMuon.dataFormatPost.format(self.ptError)
        elif line == 2:
            try:
                return RecoMuon.dataFormatExtra.format(
                    self.nMuonHits, self.nDTHits, self.nCSCHits, self.nDTStations, self.nCSCStations, self.chi2, self.ndof, self.x_fhit, self.y_fhit, self.z_fhit)
            except:
                return '|{:10d}|{:8d}|{:8d}|{:14d}|{:14d}|{:9.2f}|{:9.2f}|\n'.format(
                    self.nMuonHits, self.nDTHits, self.nCSCHits, self.nDTStations, self.nCSCStations, self.chi2, self.ndof)
        elif line == 3:
            return self.IP.datastr()
        else:
            return ''

    def __str__(self):
        return ''.join([RecoMuon.headerstr(i) + self.datastr(i) for i in (1, 2, 3)])

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

    def d0   (self, vertex='BS', extrap=None): return self.getValue('d0', None , vertex, extrap)
    def dz   (self, vertex='BS', extrap=None): return self.getValue('dz', None , vertex, extrap)
    def d0Sig(self, vertex='BS', extrap=None): return self.getValue('d0', 'SIG', vertex, extrap)
    def dzSig(self, vertex='BS', extrap=None): return self.getValue('dz', 'SIG', vertex, extrap)
    def d0Err(self, vertex='BS', extrap=None): return self.d0(vertex, extrap)/self.d0Sig(vertex, extrap)
    def dzErr(self, vertex='BS', extrap=None): return self.dz(vertex, extrap)/self.dzSig(vertex, extrap)


    headerVertexFormat        = '|{:^63s}'
    headerExtrapolationFormat = '|{:^31s}'
    headerValuesFormat        = '|{:7s}|{:7s}|{:7s}|{:7s}'

    dataValuesFormat          = '|{:7.2f}|{:7.2f}|{:7.2f}|{:7.2f}'

    extrapolationDictionary   = {None : 'Full Fit', 'LIN': 'Linear Fit'}
    vertexDictionary          = {'PV': 'Primary Vertex', 'BS': 'Beamspot'}

    @staticmethod
    def headerstr():

        outstr = ''
        for vertex in ImpactParameter.vertexDictionary.keys():
            outstr += ImpactParameter.headerVertexFormat.format(ImpactParameter.vertexDictionary[vertex])

        outstr += '|\n'

        for vertex in ImpactParameter.vertexDictionary.keys():
            for extrapolation in ImpactParameter.extrapolationDictionary.keys():
                outstr += ImpactParameter.headerExtrapolationFormat.format(ImpactParameter.extrapolationDictionary[extrapolation])
        outstr +='|\n'             

        for vertex in ImpactParameter.vertexDictionary.keys():
            for extrapolation in ImpactParameter.extrapolationDictionary.keys():
                outstr+= ImpactParameter.headerValuesFormat.format('d0', 'd0Sig','dz',  'dzSig')
        outstr +='|\n'  
        return outstr

    def datastr(self): 
        outstr = ''
        for vertex in ImpactParameter.vertexDictionary.keys():
            for extrapolation in ImpactParameter.extrapolationDictionary.keys():
                outstr+= ImpactParameter.dataValuesFormat.format(
                    self.d0(vertex, extrapolation),
                    self.d0Sig(vertex, extrapolation),
                    self.dz(vertex, extrapolation),
                    self.dzSig(vertex, extrapolation))
        outstr +='|\n'
        return outstr

# Dimuon class
# the TranverseDecayLength is a member variable allowing easy access to Lxy and LxySig
# and the associated quantities. allow accessing its methods directly on the dimuon.
class Dimuon(Particle):
    def __init__(self, E, i):
        Particle.__init__(self, E, i, 'dim_')
        for attr in ('normChi2', 'deltaR', 'deltaPhi', 'cosAlpha'):
            self.set(attr, E, 'dim_'+attr, i)
        self.Lxy_ = TransverseDecayLength(E, i, 'dim_')

        self.mu1 = RecoMuon(E, i, 'DIM_REF1')
        self.mu2 = RecoMuon(E, i, 'DIM_REF2')

        self.idx1 = self.mu1.idx
        self.idx2 = self.mu2.idx

        self.ID   = (self.mu1.idx, self.mu2.idx)

        if         sum(self.ID) < 999 :
            self.composition = 'DSA'
        elif       sum(self.ID) > 2000:
            self.composition = 'PAT'
        elif 999 < sum(self.ID) < 2000:
            self.composition = 'HYBRID'

    def __getattr__(self, name):
        if name in ('Lxy', 'LxySig', 'LxyErr'):
            return getattr(self.Lxy_, name)
        raise AttributeError('\'Dimuon\' object has no attribute \''+name+'\'')

    def isOC(self, DSAmuons=None):
        if DSAmuons is None:
            return self.mu1.charge != self.mu2.charge
        else:
            return DSAmuons[self.idx1].charge != DSAmuons[self.idx2].charge

    # normChi2, deltaR, deltaPhi, cosAlpha, Lxy, LxySig
    headerFormatPost = '{:8s}|{:8s}|{:8s}|{:8s}|\n'
    dataFormatPost   = '{:8.2f}|{:8.2f}|{:8.2f}|{:8.2f}|\n'
    DIMUON_PRESPACE  = '    '

    @staticmethod
    def headerstr(line=1):
        # extra spaces are to align with the RecoMuon |idx| field
        if line == 1:
            return Dimuon.DIMUON_PRESPACE + Particle.headerstr().strip('\n') +\
                   Dimuon.headerFormatPost.format('normChi2', 'deltaR', 'deltaPhi', 'cosAlpha')
        elif line == 2:
            return TransverseDecayLength.headerstr()

    def datastr(self, line=1):
        # extra spaces are to align with the RecoMuon |idx| field
        if line == 1:
            return Dimuon.DIMUON_PRESPACE + Particle.datastr(self).strip('\n') +\
                   Dimuon.dataFormatPost.format(self.normChi2, self.deltaR, self.deltaPhi, self.cosAlpha)

        elif line == 2: 
            return self.Lxy_.datastr() 

    def __str__(self):
        outstr = colorText('Dimuon', color='blue') + '\n'
        outstr += Dimuon.headerstr()  + self.datastr()
        outstr += Dimuon.headerstr(2) + self.datastr(2)
        outstr += colorText('Refitted Muons', color='blue') + '\n'
        for i in (1, 3):
            outstr += RecoMuon.headerstr(i)
            for mu in (self.mu1, self.mu2):
                outstr += mu.datastr(i)
        # no need to print header 2 because no header 2 quantities in refitted muons
        outstr += '\n'
        return outstr

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
    def LxyErr(self, vertex='PV'): return self.Lxy(vertex)/self.LxySig(vertex)


    headerVertexFormat = '|{:^15s}'
    headerValuesFormat = '|{:7}|{:7}'
    dataValuesFormat   = '|{:7.3f}|{:7.3f}'
    vertexDictionary   = {'PV': 'Primary Vertex', 'BS': 'Beamspot'}

    @staticmethod
    def headerstr():
        outstr = ''
        for vertex in TransverseDecayLength.vertexDictionary.keys():
            outstr += TransverseDecayLength.headerVertexFormat.format(TransverseDecayLength.vertexDictionary[vertex])
        outstr += '|\n'
        for vertex in TransverseDecayLength.vertexDictionary.keys():
            outstr += TransverseDecayLength.headerValuesFormat.format('Lxy', "Lxy Sig")
        outstr += '|\n'


        return outstr

    def datastr(self):
        outstr = ''
        for vertex in TransverseDecayLength.vertexDictionary.keys():
            outstr += TransverseDecayLength.dataValuesFormat.format(self.Lxy(vertex), self.LxySig(vertex))
        outstr += '|\n'
        return outstr

# function for copying nHits, chi2, first hit x, y, z, etc. from DSAmuons to refitted muons
# This could have been done in the Dimuon class, but would require some sort of juggling to
# ensure that DSAMUON BranchKey is declared, otherwise the ETree will not have the branches
# It would also happen every time, whether it was needed or not
# So, this function takes fully instantiated Primitives lists and MODIFIES them
# It's inherently dangerous, of course
# I guarantee that this function does not modify the DSAmuons argument, but DOES modify the
# passed Dimuons list, namely, copies information to the embedded mu1 and mu2 objects
# After declaring Dimuons and DSAmuons, call Primitives.CopyExtraRecoMuonInfo(Dimuons, DSAmuons)
# The original Dimuons list will be modified
def CopyExtraRecoMuonInfo(Dimuons, DSAmuons):
    for dimuon in Dimuons:
        # hack for ignoring the PAT Dimuons and Hybrid Dimuons
        if sum(dimuon.ID) > 999: continue
        for muNum in ('1', '2'):
            thisMu = getattr(dimuon, 'mu'+muNum)
            recoMu = DSAmuons[thisMu.idx]
            for attr in ('nMuonHits', 'nDTHits', 'nCSCHits', 'nDTStations', 'nCSCStations', 'chi2', 'ndof', 'x_fhit', 'y_fhit', 'z_fhit', 'normChi2', 'fhit'):
                setattr(thisMu, attr, getattr(recoMu, attr))
