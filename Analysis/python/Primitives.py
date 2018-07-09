import re
import math
import ROOT as R
import DisplacedDimuons.Common.Constants as Constants

##########
# This file defines the Primitives classes for ease of access and idiomatic analysis code.
# Life is much better once you have a list of objects that are actual objects.
##########

BRANCHCONFIG = (
    ('EVENT'    , 'evt_'  ),
    ('TRIGGER'  , 'trig_' ),
    ('MET'      , 'met_'  ),
    ('FILTER'   , 'flag_' ),
    ('BEAMSPOT' , 'bs_'   ),
    ('VERTEX'   , 'vtx_'  ),
    ('GEN'      , 'gen_'  ),
    ('MUON'     , 'mu_'   ),
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
        BranchList = [str(br.GetName()) for br in list(t.GetListOfBranches())]
        self.DecList = [key for key in BRANCHKEYS if key in DecList] #sets correct order
        for KEY in DecList:
            for br in BranchList:
                if re.match(BRANCHPREFIXES[KEY], br):
                    self.copyBranch(t, br)
 
    # this function copies the contents of t into the ETree
    # and makes a Python list from a vector if appropriate
    def copyBranch(self, t, branch):
        if 'vector' in type(getattr(t, branch)).__name__:
            setattr(self, branch, list(getattr(t, branch)))
        else:
            setattr(self, branch, getattr(t, branch))
 
    # this function creates a list of Primitives objects given a tag
    # it should be called for each analysis object, once per event (after the ETree is declared)
    def getPrimitives(self, KEY):
        if not KEY in self.DecList:
            raise Exception('Key: %s not found in tree'%KEY)
        
        if KEY == 'EVENT'    : return Event       (self)
        if KEY == 'TRIGGER'  :
            if not hasattr(self, 'trig_hlt_idx'):
                raise Exception('Sample does not contain Trigger branches; tree must be made from PAT Tuple')
            HLTPaths =                [HLTPath    (self, i)                for i in range(len(self.trig_hlt_idx  ))]
            HLTMuons =                [TriggerMuon(self, i, 'trig_hltmu_') for i in range(len(self.trig_hltmu_idx))]
            L1TMuons =                [TriggerMuon(self, i, 'trig_l1tmu_') for i in range(len(self.trig_hltmu_idx))]
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
            if Constants.LLX_PDGID in self.gen_pdgID: #signal sample
                if abs(self.gen_pdgID[2]) != Constants.ABS_MUON_PDGID: #2mu2J sample
                    muons   =             [GenMuon    (self, i        )        for i in range(2)                       ]
                    jets    =             [GenMuon    (self, i        )        for i in range(2, 4)                    ]
                    mothers =             [Particle   (self, i, 'gen_')        for i in range(4, 8)                    ]
                    extramu =             []
                    if len(self.gen_eta) > 8:
                        extramu =         [Muon       (self, i, 'gen_')        for i in range(8, len(self.gen_eta    ))]
                    return muons + jets + mothers + [extramu]
                else: #4mu
                    muons   =             [GenMuon    (self, i        )        for i in range(4)                       ]
                    mothers =             [Particle   (self, i, 'gen_')        for i in range(4, 8)                    ]
                    extramu =             []
                    if len(self.gen_eta) > 8:
                        extramu =         [Muon       (self, i, 'gen_')        for i in range(8, len(self.gen_eta    ))]
                    return muons + mothers + [extramu]
            else: #backgound
                return                [Particle   (self, i, 'gen_')        for i in range(len(self.gen_eta       ))]
        if KEY == 'MUON'     : return [AODMuon    (self, i        )        for i in range(len(self.mu_eta        ))]
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
        
        
    def __repr__(self):
        outstr = "\n\033[1m=======================================================\033[0m\n"
        
        for key in self.DecList:
            
            primitives = self.getPrimitives(key) 
           
            try: #is iterable
                if key == 'TRIGGER':
                    HLTPaths, HLTMuons, L1TMuons = primitives
                    outstr += str(HLTPaths) + '\n'
                    outstr+='\033[1m\033[95mTrigger Muons\033[0m\033[0m:\n'
                    outstr+= TriggerMuon.headerstr()
                    for trigmuon in L1TMuons: outstr += trigmuon.datastr()
                    for trigmuon in HLTMuons: outstr += trigmuon.datastr()
                    outstr+= '\n'
                    
                elif key == 'GEN':
                    outstr+='\033[1m\033[95mGen Muons\033[0m\033[0m:\n'
                    outstr += GenMuon.headerstr()
                    for particle in primitives:
                        
                        if isinstance(particle, list):
                            outstr +=" %i Extra Muons in event\n"%len(particle)
                            for mu in particle:
                                outstr += mu.datastr()
                        else:
                            outstr += particle.datastr()
                    outstr +='\n'
                    
                elif key == 'MUON':
                    outstr+='\033[1m\033[95mAOD MUON\033[0m\033[0m:\n'
                    outstr += AODMuon.headerstr()
                    for particle in primitives:
                        outstr += particle.datastr()
                    outstr +='\n'
                        
                elif key == 'DSAMUON' or key == 'RSAMUON':
                    outstr += '\033[1m\033[95m%s\033[0m\033[0m:\n' % key
                    outstr += RecoMuon.headerstr()
                    for particle in primitives:
                        outstr += particle.datastr()
                    outstr += RecoMuon.headerstr2()
                    for particle in primitives:
                        outstr += particle.datastr2()
                    outstr += RecoMuon.headerstr3()
                    for particle in primitives:
                        outstr += particle.datastr3()
                    outstr += '\n'
                else:
                    for primitive in primitives:
                        outstr += str(primitive) + '\n'
            except TypeError: #isn't iterable
                outstr += str(primitives)  +'\n'          
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
        outstr = '\033[1m\033[95m' + self.__class__.__name__ +'\033[0m\033[0m:\n'
        for attr in self.__dict__.keys():
            tabs = ''
            for ntabs in range(0,2-len(attr)/7): tabs+= '\t'
            
            data = self.__dict__[attr]
            if isinstance(data, bool): #format booleans in a nice way
                if data: #print in green
                    data = '\033[92m' + str(data) + '\033[0m'
                else: #print in red
                    data = '\033[91m' + str(data) + '\033[0m'  
            else:
                data = str(data)
            
            outstr += attr + ':' + tabs +data + ' \n'
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
            
            

# MET class
class MET(Primitive):
    def __init__(self, E):
        Primitive.__init__(self)
        for attr in ('pt', 'phi', 'gen_pt'):
            self.set(attr, E, 'met_'+attr)
            
    def __str__(self):  
        outstr = '\033[1m\033[95m' + self.__class__.__name__ +'\033[0m\033[0m:   '
        for attr in self.__dict__.keys():
            outstr += attr + ':  ' + '%3.3f\t'%self.__dict__[attr]
        outstr += '\n'
        return outstr

# MET filter class
class Filters(Primitive):
    def __init__(self, E):
        Primitive.__init__(self)
        for attr in ('PhysicsDeclared', 'PrimaryVertexFilter', 'AllMETFilters', 'HBHENoiseFilter', 'HBHEIsoNoiseFilter', 'CSCTightHaloFilter', 'EcalTPFilter', 'EeBadScFilter', 'BadPFMuonFilter', 'BadChargedCandidateFilter'):
            self.set(attr, E, 'flag_'+attr)
            setattr(self, attr, bool(getattr(self, attr)))
    
    def __str__(self):  
        outstr = '\033[1m\033[95m' + self.__class__.__name__ +'\033[0m\033[0m:\n'
        for attr in self.__dict__.keys():
            tabs = ''
            for ntabs in range(0,4-len(attr)/7): tabs+= '\t'
            
            data = self.__dict__[attr]
            if isinstance(data, bool): #format booleans in a nice way
                if data: #print in green
                    data = '\033[92m' + str(data) + '\033[0m'
                else: #print in red
                    data = '\033[91m' + str(data) + '\033[0m'  
            else:
                data = str(data)
            
            outstr += attr + ':' + tabs +data + ' \n'
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
            
    def __repr__(self):
        return self.__str__()

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

        self.p3 = R.TVector3(self.px, self.py, self.pz)
        self.pt = math.sqrt(self.px**2. + self.py**2.)

                #'idx', 'trigger', 'pt', 'px', 'py', 'pz', 'eta', 'phi'
    headerFormat = "|{:4}|{:8}|{:9.5}|{:9.9}|{:9.9}|{:9.9}|{:9.9}|{:9.9}|\n"
    dataFormat = "|{:4d}|{:8s}|{:9.3f}|{:9.3f}|{:9.3f}|{:9.3f}|{:9.3f}|{:9.3f}|\n"
      
    @staticmethod #so we don't need an instance of it
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
        outstr = '\033[1m\033[95m' + self.__class__.__name__ +'\033[0m\033[0m:\n'
        outstr += 'x +/- dx =\t%3.3f +/- %3.3f [cm]\n'%(self.x, self.dx)
        outstr += 'y +/- dy =\t%3.3f +/- %3.3f [cm]\n'%(self.y, self.dy)
        outstr += 'z +/- dz =\t%3.3f +/- %3.3f [cm]\n'%(self.z, self.dz)
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
        outstr = '\033[1m\033[95m' + self.__class__.__name__ +'\033[0m\033[0m:\n'
        outstr += 'nvtx = %i\tntrk: %i\t chi2/ndf: %3.2f/%3.2f = %3.2f\n'%(self.nvtx, self.ntrk, self.chi2,
                                                                  self.ndof, self.chi2/self.ndof)
        outstr += 'x +/- dx =\t%3.3f +/- %3.3f [cm]\n'%(self.x, self.dx)
        outstr += 'y +/- dy =\t%3.3f +/- %3.3f [cm]\n'%(self.y, self.dy)
        outstr += 'z +/- dz =\t%3.3f +/- %3.3f [cm]\n'%(self.z, self.dz)
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

        # set basic particle variables; see getMissingValues below
        missing = self.getMissingValues(E, i, prefix)
        for attr in ('pt', 'eta', 'phi', 'mass', 'energy', 'charge', 'x', 'y', 'z'):
            if attr in missing:
                setattr(self, attr, missing[attr])
            else:
                self.set(attr, E, prefix+attr, i)

        # set pdgID for gen particles
        if prefix == 'gen_':
            self.set('pdgID', E, prefix+'pdgID', i)
            self.set('status', E, prefix+'status', i)
            self.set('mother', E, prefix+'mother', i)

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
    #  - dsamu, rsamu, dim_mu* do not have pt, mass, energy, but have px, py, pz
    #  - dim does not have energy, charge, but has mass and p
    #  - dim_mu* do not have x, y, z, but they are the same as dim_x, dim_y, dim_z
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
        if not hasattr(E, prefix+'x'):
            if 'dim_mu' in prefix:
                missing['x'] = E.get('dim_x', i)
                missing['y'] = E.get('dim_y', i)
                missing['z'] = E.get('dim_z', i)
            else:
                raise Exception('xyz for prefix '+prefix+' unavailable.')
        return missing
    
                   # pdgID, status, mother, pt,  eta, phi, mass, energy, q, (x,y,z)";    
    headerFormat = "|{:9}|{:8}|{:8}|{:9}|{:10}|{:7}|{:10}|{:10}|{:5}|{:^21}|\n"
    dataFormat = "|{:9s}|{:8s}|{:8s}|{:9.2f}|{:10.2f}|{:7.2f}|{:10.2f}|{:10.2f}|{:5.1f}|{:7.2f}{:7.2f}{:7.2f}|\n"

    
    @staticmethod #so we don't need an instance of it
    def headerstr():
        return Particle.headerFormat.format('pdgID', 'status', 'mother',\
                                             'pt',  'eta', 'phi', 'mass',\
                                              'energy', 'q', '(x,y,z)') 
    
    
    def datastr(self):
        pdgID_ = 'N/A' if not hasattr(self,'pdgID') else str(self.pdgID)
        status_ = 'N/A' if not hasattr(self, 'status') else str(self.status)
        mother_ = 'N/A' if not hasattr(self, 'mother') else str(self.mother)
        
        return Particle.dataFormat.format(pdgID_, status_, mother_,\
                                           self.pt, self.eta, self.phi, self.mass, \
                                           self.energy, self.charge, self.x, self.y, self.z)
    
    def __str__(self):
        return Particle.headerstr() + self.datastr()
    
    


# Muon classes
# sets all the particle variables
# base class for several "kinds" of muons, each with different additional branches
# AODMuon        : reco AOD muons from the reco::Muon collection (mu_)
#   .gen         : gen muon matched/attached to the AOD muon     (mu_gen_)
# GenMuon        : gen muons from the GenParticle collection     (gen_)
# RecoMuon       : reco muons from a reco::Track collection
#   ("DSA")      : reco DSA muons from displacedStandAloneMuons  (dsamu_)
#   ("RSA")      : reco RSA muons from refittedStandAloneMuons   (rsamu_)
#   ("DIM_DSA1") : reco DSA muons from refitted dimuon tracks    (dim_mu1_)
#   ("DIM_DSA2") : reco DSA muons from refitted dimuon tracks    (dim_mu2_)
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
        for attr in ('cosAlpha', 'deltaR'):
            self.set(attr, E, 'gen_'+attr, i)

        # genMuons and dimuons get Lxy with Lxy()
        # genMuons and reco muons get d0 with d0()
        # so make sure that the name doesn't collide
        self.set('Lxy_', E, 'gen_Lxy', i)
        self.set('d0_' , E, 'gen_d0' , i)
        self.set('dz_' , E, 'gen_dz' , i)

    def Lxy(self):
        return self.Lxy_
    def d0(self):
        return self.d0_
    def dz(self):
        return self.dz_
    
    headerFormat = "{:8}|{:8}|{:8}|{:8}|{:8}|\n"
    dataFormat = "{:8.2f}|{:8.3f}|{:8.2f}|{:8.2f}|{:8.2f}|\n"
    
    @staticmethod #so we don't need an instance of it
    def headerstr():
        header = Particle.headerstr().replace("\n", "") # take of the \n
        return header + GenMuon.headerFormat.format('Lxy', 'cosA', 'd0', 'dz', 'dR')
    
    def datastr(self):
        data = Particle.datastr(self).replace("\n", "")
        return data + GenMuon.dataFormat.format(self.Lxy_, self.cosAlpha, self.d0_, self.dz_, self.deltaR)

    
    

# RecoMuon: see above
# the ImpactParameter is a member variable allowing easy access to d0, dz
# and the associated quantities. allow accessing its methods directly on the muon.
class RecoMuon(Muon):
    def __init__(self, E, i, tag):
        TAGDICT = {
            'DSA'      : 'dsamu_',
            'RSA'      : 'rsamu_',
            'DIM_DSA1' : 'dim_mu1_',
            'DIM_DSA2' : 'dim_mu2_',
        }
        prefix = TAGDICT[tag]
        Muon.__init__(self, E, i, prefix)

        # all reco muons have idx, ptError, and impact parameter
        self.set('idx', E, prefix+'idx', i)
        self.set('ptError', E, prefix+'ptError', i)
        self.IP = ImpactParameter(E, i, prefix)

        # only DSA and RSA have these attributes
        if tag in ('DSA', 'RSA'):
            for attr in ('nMuonHits', 'nDTHits', 'nCSCHits', 'nDTStations', 'nCSCStations', 'chi2', 'ndof', 'x_fhit', 'y_fhit', 'z_fhit'):
                self.set(attr, E, prefix+attr, i)
            self.normChi2 = self.chi2/self.ndof if self.ndof != 0 else float('inf')
            self.fhit = R.TVector3(self.x_fhit, self.y_fhit, self.z_fhit)

    def __getattr__(self, name):
        if name in ('d0', 'dz', 'd0Sig', 'dzSig'):
            return getattr(self.IP, name)
        raise AttributeError('\'RecoMuon\' object has no attribute \''+name+'\'')
    # 'nMuonHits', 'nDTHits', 'nCSCHits', 'nDTStations', 'nCSCStations', 'chi2', 'ndof', 'x_fhit', 'y_fhit', 'z_fhit'
    headerFormat2 = "|{:10}|{:8}|{:8}|{:14}|{:14}|{:9}|{:9}|{:^27}|\n"
    dataFormat2 = "|{:10d}|{:8d}|{:8d}|{:14d}|{:14d}|{:9.2f}|{:9.2f}|{:9.2f}{:9.2f}{:9.2f}|\n"
    
    headerFormat3 = "|{:8}|{:8}|{:8}|{:8}|\n"
    dataFormat3 = "|{:8.2f}|{:8.2f}|{:8.2f}|{:8.2f}|\n"
    
    @staticmethod
    def headerstr2():
        return RecoMuon.headerFormat2.format('nMuonHits', 'nDTHits', 'nCSCHits', 'nDTStations', 'nCSCStations', 'chi2', 'ndof', '(x_fhit, y_fhit, z_fhit)')
    def datastr2(self):
        return RecoMuon.dataFormat2.format(self.nMuonHits, self.nDTHits, self.nCSCHits, self.nDTStations,\
                                           self.nCSCStations, self.chi2, self.ndof, self.x_fhit, self.y_fhit, self.z_fhit)
    
    @staticmethod
    def headerstr3():
        return RecoMuon.headerFormat3.format('d0', 'dz', 'd0Sig', 'dzSig')
    def datastr3(self):
        return RecoMuon.dataFormat3.format(self.d0(), self.dz(), self.d0Sig(), self.dzSig())
    
    def __str__(self):
        return Particle.headerstr() + self.datastr() + RecoMuon.headerstr2() + self.datastr2()\
            + RecoMuon.headerstr3() + self.datastr3()

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
# the TranverseDecayLength is a member variable allowing easy access to Lxy and LxySig
# and the associated quantities. allow accessing its methods directly on the dimuon.
class Dimuon(Particle):
    def __init__(self, E, i):
        Particle.__init__(self, E, i, 'dim_')
        for attr in ('normChi2', 'deltaR', 'deltaPhi', 'cosAlpha'):
            self.set(attr, E, 'dim_'+attr, i)
        self.Lxy_ = TransverseDecayLength(E, i, 'dim_')

        self.mu1 = RecoMuon(E, i, 'DIM_DSA1')
        self.mu2 = RecoMuon(E, i, 'DIM_DSA2')
        
        self.muons = [self.mu1, self.mu2]

        self.idx1 = self.mu1.idx
        self.idx2 = self.mu2.idx

    def __getattr__(self, name):
        if name in ('Lxy', 'LxySig'):
            return getattr(self.Lxy_, name)
        raise AttributeError('\'Dimuon\' object has no attribute \''+name+'\'')
    
    
    headerFormat = "|{:8}|{:8}|{:8}|{:8}|{:8}|{:8}|\n"
    dataFormat = "|{:8.2f}|{:8.2f}|{:8.2f}|{:8.2f}|{:8.2f}|{:8.2f}|\n"
    
    def __str__(self):
        outstr = '\033[1m\033[94m' + self.__class__.__name__ +'\033[0m\033[0m:\n'
        outstr += Dimuon.headerFormat.format('normChi2', 'deltaR', 'deltaPhi', 'cosAlpha', 'Lxy', 'LxySig')
        outstr += Dimuon.dataFormat.format(self.normChi2, self.deltaR, self.deltaPhi, self.cosAlpha, self.Lxy(), self.LxySig()) + '\n'
        
        outstr += RecoMuon.headerstr()
        for mu in self.muons:
            outstr += mu.datastr()
        outstr += RecoMuon.headerstr3() #we don't fillheader 2 stuff here...
        for mu in self.muons:
            outstr += mu.datastr3()
        outstr+='\n'
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
