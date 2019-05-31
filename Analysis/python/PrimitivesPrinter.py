import DisplacedDimuons.Analysis.Primitives as Primitives

COLORON = False

# color text
def colorText(text, color='blue'):
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
    elif color == 'bold':
        color = 1
    elif color == 'boldblue':
        color = '1;94'
    return '\033[{COLOR}m{TEXT}\033[0m'.format(COLOR=color, TEXT=text)


# master print function
# calls the appropriate print function based on the class type, and PRINTS
# the appropriate print functions are defined below
def Print(obj, *args):
    className = obj.__class__.__name__
    print PrintFunctions[className](obj, *args)

# general format of a class-specific print function:
# outstr = '', add title if desired, add header if desired,
# add data by double splat ** the object dictionary, return

def EventPrint(obj, title=True):
    outstr = ''
    if title:
        outstr += '\n' + colorText(TitleStrings['Event'], 'boldblue') + '\n'

    d = dict(obj.__dict__)
    d['weight']  = float('inf') if 'weight' not in d else d['weight']
    d['nTruePV'] = float('inf') if 'nTruePV' not in d else d['nTruePV']

    return outstr + DataStrings['Event'].format(**d)

def METPrint(obj, title=True):
    outstr = ''
    if title:
        outstr += '\n' + colorText(TitleStrings['MET'], 'boldblue') + '\n'
    return outstr + DataStrings['MET'].format(**obj.__dict__)

def FiltersPrint(obj, title=True):
    outstr = ''
    if title:
        outstr += '\n' + colorText(TitleStrings['Filters'], 'boldblue') + '\n'
    return outstr + DataStrings['Filters'].format(**obj.__dict__)

def BeamspotPrint(obj, title=True):
    outstr = ''
    if title:
        outstr += '\n' + colorText(TitleStrings['Beamspot'], 'boldblue') + '\n'
    return outstr + DataStrings['Beamspot'].format(**obj.__dict__)

def VertexPrint(obj, title=True):
    outstr = ''
    if title:
        outstr += '\n' + colorText(TitleStrings['Vertex'], 'boldblue') + '\n'
    return outstr + DataStrings['Vertex'].format(NC2=obj.chi2/obj.ndof, **obj.__dict__)

# the next six class-specific functions are found in lists, and so
# are suitable for the ListPrint function; therefore, they must all have the same interface
# HLTPathPrint doesn't do anything with the header argument
# only RecoMuonPrint and DimuonPrint do anything with the lines argument
# only GenMuonPrint, RecoMuonPrint, and DimuonPrint do anything with the alt argument
# defaults are set up so that Print(obj) will print the whole class, with title and header

def HLTPathPrint(obj, title=True, header=True, lines=(1,), alt=None):
    outstr = ''
    if title:
        outstr += '\n' + colorText(TitleStrings['HLTPath'], 'boldblue') + '\n'
    return outstr + DataStrings['HLTPath'].format(**obj.__dict__)

def TriggerMuonPrint(obj, title=True, header=True, lines=(1,), alt=None):
    outstr = ''
    if title:
        outstr += '\n' + colorText(TitleStrings['TriggerMuon'], 'boldblue') + '\n'
    if header:
        outstr += colorText(HeaderStrings['TriggerMuon'], 'bold') + '\n'
    return outstr + DataStrings['TriggerMuon'].format(**obj.__dict__)

def GenParticlePrint(obj, title=True, header=True, lines=(1,), alt=None):
    outstr = ''
    if title:
        outstr += '\n' + colorText(TitleStrings['GenParticle'], 'boldblue') + '\n'
    if header:
        outstr += colorText(' '.join([HeaderStrings['GenParticle'], HeaderStrings['Particle']]), 'bold') + '\n'
    return outstr + ' '.join([DataStrings['GenParticle'], DataStrings['Particle']]).format(**obj.__dict__)

# alt is used by ListPrint to figure out whether the given list is entirely GenMuons, or DSAmuons, or whatever
# lines is usually (1,) to indicate that there's just one line
# lines in RecoMuonPrint are really lines, each line containing information
# lines in DimuonPrint is only used to signal whether to print the refitted muon class
# since when printing refitted muons, it's better to reprint line 1 of the dimuons to make connections

def GenMuonPrint(obj, title=True, header=True, lines=(1,), alt=None):
    outstr = ''
    if title:
        if alt is None:
            outstr += '\n' + colorText(TitleStrings['GenMuon'], 'boldblue') + '\n'
        else:
            outstr += '\n' + colorText(TitleStrings[alt], 'boldblue') + '\n'
    if header:
        outstr += colorText(' '.join([HeaderStrings['GenParticle'], HeaderStrings['Particle'], HeaderStrings['GenMuon']]), 'bold') + '\n'
    return outstr + ' '.join([DataStrings['GenParticle'], DataStrings['Particle'], DataStrings['GenMuon']]).format(d0BS=obj.BS.d0_, dzBS=obj.BS.dz_, **obj.__dict__)

def RecoMuonPrint(obj, title=True, header=True, lines=(1, 2, 3), alt=None):
    outstr = ''
    for line in lines:

        # Line 1: the particle info, plus index, type, pTerror, etc.
        if line == 1:
            if title:
                if alt is None:
                    outstr += '\n' + colorText(TitleStrings['RecoMuon'], 'boldblue') + '\n'
                else:
                    outstr += '\n' + colorText(TitleStrings[alt], 'boldblue') + '\n'
            if header:
                outstr += colorText(' '.join([HeaderStrings['RecoMuon']['pre'], HeaderStrings['Particle'], HeaderStrings['RecoMuon']['post']]), 'bold') + '\n'
            outstr += ' '.join([DataStrings['RecoMuon']['pre'], DataStrings['Particle'], DataStrings['RecoMuon']['post']]).format(typ=F_PrettyTag(obj), **obj.__dict__)

        # Line 2: impact parameter block
        # here, it was more convenient to use tuples instead of keywords for the data and header strings
        if line == 2:
            if len(outstr) > 0 and outstr[-1] != '\n' : outstr += '\n'

            if header:
                outstr += '\n' + colorText(HeaderStrings['ImpactParameter'], 'bold') + '\n'

            data = [obj.idx, F_PrettyTag(obj)]
            for key in [
                'd0-BS-MAG', 'd0Sig-BS-MAG', 'd0-BS-LIN', 'd0Sig-BS-LIN', 
                'd0-PV-MAG', 'd0Sig-PV-MAG', 'd0-PV-LIN', 'd0Sig-PV-LIN', 
                'dz-BS-MAG', 'dzSig-BS-MAG', 'dz-BS-LIN', 'dzSig-BS-LIN', 
                'dz-PV-MAG', 'dzSig-PV-MAG', 'dz-PV-LIN', 'dzSig-PV-LIN']:
                data.append(obj.IP.getValue(key[:2], None if 'Sig' not in key else 'SIG', 'BS' if 'BS' in key else 'PV', None if 'MAG' in key else 'LIN'))
            outstr += DataStrings['ImpactParameter'].format(*data)

        # Line 3: type-specific info (nStations, isGlobal, etc.)
        # several arguments are not suitable for printing without transformation, so
        # the dictionary of attributes is deep copied, and the relevant arguments are modified
        if line == 3:
            if len(outstr) > 0 and outstr[-1] != '\n' : outstr += '\n'

            if 'REF' not in obj.tag:
                RTYPE = obj.tag
            else:
                RTYPE = 'REF'

            if header:
                outstr += '\n' + colorText(HeaderStrings['RecoExtra'][RTYPE], 'bold') + '\n'

            d = dict(obj.__dict__)

            if RTYPE == 'DSA':
                d['IDXPROX'] = -1 if obj.idx_ProxMatch is None else obj.idx_ProxMatch 
                d['DRPROX'] = obj.deltaR_ProxMatch
                d['SEGM'] = ', '.join(map(str, obj.idx_SegMatch)) if obj.idx_SegMatch is not None else '-'

            if RTYPE == 'PAT':
                d['isGlobal'] = str(d['isGlobal'])
                d['isMedium'] = str(d['isMedium'])
                d['isTracker'] = str(d['isTracker'])
                d['highPurity'] = str(d['highPurity'])

            if RTYPE == 'REF':
                if 'DSA' in obj.tag:
                    d['hitsBeforeVtx'] = '-'
                    d['missingHitsAfterVtx'] = '-'
                else:
                    d['hitsBeforeVtx'] = str(d['hitsBeforeVtx'])
                    d['missingHitsAfterVtx'] = str(d['missingHitsAfterVtx'])

            outstr += DataStrings['RecoExtra'][RTYPE].format(typ=F_PrettyTag(obj), **d)

    return outstr

def DimuonPrint(obj, title=True, header=True, lines=(1, 2), alt=None):

    # lines is just a proxy for whether or not to print the refitted muons
    printRefitted = lines == (1, 2)

    # Line 1: the dimuon particle info, including Lxy, LxySig, etc.
    outstr = ''
    if title:
        if alt is None:
            outstr += '\n' + colorText(TitleStrings['Dimuon'], 'boldblue') + '\n'
        else:
            outstr += '\n' + colorText(TitleStrings[alt], 'boldblue') + '\n'
    if printRefitted:
        outstr += colorText('\n  ==== DIMUON ====\n', 'bold')
    if header:
        outstr += colorText(' '.join([HeaderStrings['Dimuon']['pre'], HeaderStrings['Particle'], HeaderStrings['Dimuon']['post']]), 'bold') + '\n'
    outstr += ' '.join([DataStrings['Dimuon']['pre'], DataStrings['Particle'], DataStrings['Dimuon']['post']]).format(
            Lxy=obj.Lxy(), LxySig=obj.LxySig(), LxyPV=obj.Lxy('PV'), LxySigPV=obj.LxySig('PV'), **obj.__dict__)

    # Line 2: the refitted muons
    # I have left a ListPrint commented out to remind you that this is mostly a modified bit
    # of ListPrint, except that I needed more control over the arguments and capturing as strings instead of printing
    if printRefitted:
        #ListPrint((obj.mu1, obj.mu2))
        outstr += colorText('\n\n  ==== REFITTED MUONS ====\n', 'bold')
        for subline in (1, 2, 3):
            for i, subobj in enumerate((obj.mu1, obj.mu2)):
                if i == 0:
                    outstr += RecoMuonPrint(subobj, False, True, (subline,), None) + '\n'
                else:
                    outstr += RecoMuonPrint(subobj, False, False, (subline,), None) + '\n'

    return outstr

# gather all the print functions together into a dictionary
# for ease of access via the class name

PrintFunctions = {}
for CLASS in (
    'Event',
    'MET',
    'Filters',
    'Vertex',
    'Beamspot',
    'HLTPath',
    'TriggerMuon',
    'GenParticle',
    'GenMuon',
    'RecoMuon',
    'Dimuon',
    ):
    PrintFunctions[CLASS] = locals()[CLASS+'Print']

# DEFINE all the __str__ classes! So that you can still do print muon, if you really
# don't want any of the special features given by this module
for CLASS in PrintFunctions:
    getattr(Primitives, CLASS).__str__ = PrintFunctions[CLASS]

# And finally, define the print ETree function
# Based on the information gained from writing testNewDump.py
def printETree(ETree):
    if 'EVENT' in ETree.DecList:
        Event = ETree.getPrimitives('EVENT')
        Print(Event)

    if 'MET' in ETree.DecList:
        MET = ETree.getPrimitives('MET')
        Print(MET)

    if 'FILTERS' in ETree.DecList:
        Filters = ETree.getPrimitives('FILTERS')
        Print(Filters)

    if 'BEAMSPOT' in ETree.DecList:
        Beamspot = ETree.getPrimitives('BEAMSPOT')
        Print(Beamspot)

    if 'VERTEX' in ETree.DecList:
        Vertex = ETree.getPrimitives('VERTEX')
        Print(Vertex)

    if 'TRIGGER' in ETree.DecList:
        HLTPaths, HLTMuons, L1TMuons = ETree.getPrimitives('TRIGGER')
        ListPrint(HLTPaths)
        ListPrint(HLTMuons+L1TMuons)

    if 'GEN' in ETree.DecList:
        gens = ETree.getPrimitives('GEN')
        # if this is signal, the last argument is extramu, which is a list
        # just tack it on to the other gens, if so
        if type(gens[-1]) == list:
            ListPrint(list(gens[:-1]) + gens[-1])
        else:
            ListPrint(gens)

    if 'DSAMUON' in ETree.DecList:
        DSAmuons = ETree.getPrimitives('DSAMUON')
        ListPrint(DSAmuons)

    if 'RSAMUON' in ETree.DecList:
        RSAmuons = ETree.getPrimitives('RSAMUON')
        ListPrint(RSAmuons)

    if 'PATMUON' in ETree.DecList:
        PATmuons = ETree.getPrimitives('PATMUON')
        ListPrint(PATmuons)

    if 'DIMUON' in ETree.DecList:
        Dimuons = ETree.getPrimitives('DIMUON')
        ListPrint(Dimuons, dimuonDetails=True)

    return ''

Primitives.ETree.__str__ = printETree

##########

# Takes a RecoMuon tag and writes it slightly nicer and compact
def F_PrettyTag(obj):
    if 'REF' not in obj.tag:
        return obj.tag
    else:
        # form: DIM_DSA_REF1, DIM_PAT_REF2, etc.
        return obj.tag[8:] + '/' + obj.tag[4:7]

# ListPrint: the hallowed function that prints lists by printing all of line 1 first, then all of line 2, etc.
# Only two classes need modification of the default (1,) lines argument: RecoMuon and Dimuon
# Works for HLTPath, TriggerMuon, GenParticle, GenMuon, RecoMuon, Dimuon
# the block that sets alt is currently never called for refitted muons, because
# refitted muons are called explicitly from DimuonPrint
# so never do ListPrint((dim.mu1, dim.mu2)) -- the alt block will crash in RecoMuonPrint
# only when dimuonDetails = True will this function loop over the dimuons a second time, this time printing
# all of the refitted muon information after each dimuon

def ListPrint(List, title=True, header=True, lines=None, alt=None, dimuonDetails=False):
    if len(List) > 0 and lines is None:
        className = List[0].__class__.__name__
        if className == 'RecoMuon':
            lines = (1, 2, 3)

    if lines is None:
        lines = (1,)

    if alt is None and len(List) > 0:
        if className == 'RecoMuon':
            s = set([List[0].tag])
            for obj in List:
                s.add(obj.tag)
            if s == set([List[0].tag]):
                alt = 'Alt'+List[0].tag
        if className == 'GenMuon':
            s = set([className])
            for obj in List:
                s.add(obj.__class__.__name__)
            if s == set([className]):
                alt = 'AltGen'

    for line in lines:
        prev = ''
        for i, obj in enumerate(List):
            this = obj.__class__.__name__
            if i == 0:
                Print(obj, title and line==lines[0], header, (line,), alt)
            else:
                # this lets you mix reco muons of different types together in the ListPrint input
                # it prints the header of line 3 if the obj.tag for RecoMuon changed
                if this == 'RecoMuon' and line == 3 and obj.tag != prev:
                    Print(obj, False, header, (line,), alt)
                else:
                    Print(obj, False, False, (line,), alt)

            if this == 'RecoMuon':
                prev = obj.tag

    if dimuonDetails and len(List) > 0 and className == 'Dimuon':
        for i, obj in enumerate(List):
            if i == 0:
                Print(obj, title, header, (1, 2), alt)
            else:
                Print(obj, False, header, (1, 2), alt)

### title, data, and header strings
# unfortunately this area is fairly unreadable
# I don't know how to get long blocks of python format strings to be more readable
# The header strings become constants, so it's not terrible important what the keyword args are; they
# are just for convenience
# The data strings, on the other hand, are format strings that need to be named the same way as
# the members of the object's class, AND if there are modified arguments, need to be named accordingly
# e.g. LxySig, d0BS, etc.

DataStrings   = {}
HeaderStrings = {}
TitleStrings  = {}

# Event
TitleStrings ['Event'] = '=== EVENT ==='
DataStrings  ['Event'] = '''
  run     : {run:<6d}
  lumi    : {lumi:<7d}
  event   : {event:<10d}
  bx      : {bx:<4d}
  weight  : {weight:<.4f}
  nTruePV : {nTruePV:<.4f}
'''.strip('\n')

# MET
TitleStrings ['MET'] = '=== MET ==='
DataStrings  ['MET'] = '''
  pT     : {pt:3.3f}
  phi    : {phi:3.3f}
  gen pT : {gen_pt:3.3f}
'''.strip('\n')

# Filters
TitleStrings ['Filters'] = '=== FILTERS ==='
DataStrings  ['Filters'] = ''
maxLen = max([len(key) for key in Primitives.Filters.FILTERLIST])
for key in Primitives.Filters.FILTERLIST:
    DataStrings['Filters'] += ('  {:'+str(maxLen)+'s} : ').format(key) + '{'+key+'}\n'
DataStrings['Filters'] = DataStrings['Filters'].rstrip('\n')

# Beamspot
TitleStrings ['Beamspot'] = '=== BEAMSPOT ==='
DataStrings  ['Beamspot'] = '''
  x +/- dx : {x:6.3f} +/- {dx:6.3f} [cm]
  y +/- dy : {y:6.3f} +/- {dy:6.3f} [cm]
  z +/- dz : {z:6.3f} +/- {dz:6.3f} [cm]
'''.strip('\n')

# Vertex
TitleStrings ['Vertex'] = '=== VERTEX ==='
DataStrings  ['Vertex'] = '''
  nVtx     : {nvtx:d}
  nTrk     : {ntrk:d}
  chi2/dof : {chi2:3.2f}/{ndof:3.2f} = {NC2:3.2f}
  x +/- dx : {x:6.3f} +/- {dx:6.3f} [cm]
  y +/- dy : {y:6.3f} +/- {dy:6.3f} [cm]
  z +/- dz : {z:6.3f} +/- {dz:6.3f} [cm]
'''.strip('\n')

# HLTPath
TitleStrings ['HLTPath'] = '=== HLT PATHS ==='
DataStrings  ['HLTPath'] = '  idx {idx:d} ::: {name:s} ::: HLT prescale {HLTPrescale:d} ::: L1T prescale {L1TPrescale:d}'

# TriggerMuon
TitleStrings ['TriggerMuon'] = '=== TRIGGER MUONS ==='
HeaderStrings['TriggerMuon'] = '  {idx:3s} {trigger:7s} {pt:>9s} {eta:>6s} {phi:>6s}'.format(idx='idx', trigger='trigger', pt='pT', eta='eta', phi='phi')
DataStrings  ['TriggerMuon'] = '  {idx:3d} {trigger:7s} {pt:9.3f} {eta:6.3f} {phi:6.3f}'

# Base Particle
HeaderStrings['Particle'] = '{pt:>9s} {et:>9s} {phi:>9s} {m:>9s} {e:>9s} {c:>6s} {x:>8s} {y:>8s} {z:>8s}'.format(pt='pT', et='eta', phi='phi', m='mass', e='energy', c='charge', x='x', y='y', z='z')
DataStrings  ['Particle'] = '{pt:9.2f} {eta:9.2f} {phi:9.2f} {mass:9.2f} {energy:9.2f} {charge:6.0f} {x:8.2f} {y:8.2f} {z:8.2f}'

# everything is quite straightforward up until this point
# now, some notes are needed

# Extra GenMuons get printed with -999 for the extra bit. There may be a good way of not doing that, but I don't want to do it right now
# for ImpactParameter, the list embedded in the print function corresponds to the order, which I used for making the format string
# Every RecoMuon has an idx, type, which go before, and pTerror, which goes after, and impact parameter on another line
# then every RecoMuon has different extra information, which goes on line 3
# I don't really have much of a convention for naming the "missing" or modified information for fields, e.g. bools, or subinfo, or otherwise computed info

# Gen Particle and Gen Muon
TitleStrings ['GenParticle'] = '=== GEN PARTICLES ==='
HeaderStrings['GenParticle'] = '  {pdgID:>7s} {status:>6s} {mother:>6s}'.format(pdgID='pdgID', status='status', mother='mother')
DataStrings  ['GenParticle'] = '  {pdgID:7d} {status:6d} {mother:6d}'

TitleStrings ['GenMuon'] = '=== GEN PARTICLES ==='
HeaderStrings['GenMuon'] = '{Lxy:>6s} {cosAlpha:>8s} {dR:>9s} {d0:>7s} {dz:>7s} {d0BS:>7s} {dzBS:>7s}'.format(Lxy='Lxy', cosAlpha='cosAlpha', dR='deltaR', d0='d0', dz='dz', d0BS='BS-d0', dzBS='BS-dz')
DataStrings  ['GenMuon'] = '{Lxy_:6.2f} {cosAlpha:8.4f} {deltaR:9.4f} {d0_:7.2f} {dz_:7.2f} {d0BS:7.2f} {dzBS:7.2f}'

# RecoMuon
TitleStrings ['RecoMuon'] = '=== RECO MUONS ==='
HeaderStrings['RecoMuon'] = {'pre' :'  {idx:>3s} {typ:8s}'.format(idx='idx', typ='type'),
                            'post' :'{pterr:>8s}'.format(pterr='pTError')}
DataStrings  ['RecoMuon'] = {'pre' :'  {idx:3d} {typ:8s}',
                            'post' :'{ptError:8.2f}'}

# Impact Parameter
temp = ['', 'BS', 'PV', 'BS', 'PV',
        '', 'MAG', 'LIN', 'MAG', 'LIN', 'MAG', 'LIN', 'MAG', 'LIN',
        'idx', 'type',
        'd0', 'd0Sig', 'd0', 'd0Sig', 'd0', 'd0Sig', 'd0', 'd0Sig', 'dz', 'dzSig', 'dz', 'dzSig', 'dz', 'dzSig', 'dz', 'dzSig']
HeaderStrings['ImpactParameter'] = '''  {:12s} {:^34s} ::: {:^34s} :::: {:^34s} ::: {:^34s}
  {:12s} {:^15s} :: {:^15s} ::: {:^15s} :: {:^15s} :::: {:^15s} :: {:^15s} ::: {:^15s} :: {:^15s}
  {:3s} {:8s} {:>7s} {:>7s} :: {:>7s} {:>7s} ::: {:>7s} {:>7s} :: {:>7s} {:>7s} :::: {:>7s} {:>7s} :: {:>7s} {:>7s} ::: {:>7s} {:>7s} :: {:>7s} {:>7s}'''.format(*temp)
DataStrings  ['ImpactParameter'] = '  {:3d} {:8s} {:7.2f} {:7.2f} :: {:7.2f} {:7.2f} ::: {:7.2f} {:7.2f} :: {:7.2f} {:7.2f} :::: {:7.2f} {:7.2f} :: {:7.2f} {:7.2f} ::: {:7.2f} {:7.2f} :: {:7.2f} {:7.2f}'

# Type-specific Reco
# Consult Primitives class for the specifics
HeaderStrings['RecoExtra'] = {'DSA':'  ', 'PAT':'  ', 'RSA':'  ', 'REF':'  '}
DataStrings  ['RecoExtra'] = {'DSA':'  ', 'PAT':'  ', 'RSA':'  ', 'REF':'  '}

for RTYPE in HeaderStrings['RecoExtra']:
    HeaderStrings['RecoExtra'][RTYPE] += '{idx:3s} {typ:8s}'.format(idx='idx', typ='type')
    DataStrings  ['RecoExtra'][RTYPE] += '{idx:3d} {typ:8s}'

for RTYPE in ('DSA', 'PAT', 'RSA'):
    HeaderStrings['RecoExtra'][RTYPE] += ' {NMH:>9s} {NDT:>7s} {NCSC:>8s} {NSDT:>8s} {NSCSC:>9s} {chi2:>6s} {dof:>6s} {normChi2:>8s}'.format(
            NMH='nMuonHits', NDT='nDTHits', NCSC='nCSCHits', NSDT='nDTStats', NSCSC='nCSCStats', chi2='chi2', dof='dof', normChi2='normChi2')
    DataStrings  ['RecoExtra'][RTYPE] += ' {nMuonHits:9d} {nDTHits:7d} {nCSCHits:8d} {nDTStations:8d} {nCSCStations:9d} {chi2:6.2f} {ndof:6.1f} {normChi2:8.2f}'

for RTYPE in ('DSA', 'RSA'):
    HeaderStrings['RecoExtra'][RTYPE] += ' {xf:>9s} {yf:>9s} {yf:>9s}'.format(xf='fHit-x', yf='fHit-y', zf='fHit-z')
    DataStrings  ['RecoExtra'][RTYPE] += ' {x_fhit:9.2f} {y_fhit:9.2f} {z_fhit:9.2f}'

for RTYPE in ('DSA',):
    HeaderStrings['RecoExtra'][RTYPE] += ' {idx_Prox:>8s} {dR_Prox:>9s} {segm:s}'.format(idx_Prox='idx-Prox', dR_Prox='dR-Prox', segm='SegMatch')
    DataStrings  ['RecoExtra'][RTYPE] += ' {IDXPROX:8d} {DRPROX:9.4f} {SEGM:s}'

for RTYPE in ('PAT',):
    HeaderStrings['RecoExtra'][RTYPE] += ' {nMatStats:>9s} {glb:>6s} {tracker:>7s} {medium:>6s} {hPurity:>7s} {nPixHits:>8s} {nTrkLays:>8s} {nTrkHits:>8s} {trkIso:>8s} {ecalIso:>8s} {hcalIso:>8s}'.format(
            nMatStats='nMatStats', glb='global', tracker='tracker', medium='medium', hPurity='hPurity',
            nPixHits='nPixHits', nTrkLays='nTrkLays', nTrkHits='nTrkHits', trkIso='trkIso', ecalIso='ecalIso', hcalIso='hcalIso')
    DataStrings  ['RecoExtra'][RTYPE] += ' {nMatchedStations:9d} {isGlobal:6s} {isTracker:7s} {isMedium:6s} {highPurity:7s} {nPixelHits:8d} {nTrackerLayers:8d} {nTrackerHits:8d} {trackIso:8.2f} {ecalIso:8.2f} {hcalIso:8.2f}'

for RTYPE in ('REF',):
    HeaderStrings['RecoExtra'][RTYPE] += ' {HBV:>13s} {MHAV:>19s}'.format(HBV='hitsBeforeVtx', MHAV='missingHitsAfterVtx')
    DataStrings  ['RecoExtra'][RTYPE] += ' {hitsBeforeVtx:>13s} {missingHitsAfterVtx:>19s}'

# Dimuon
TitleStrings ['Dimuon'] = '=== DIMUONS ==='
HeaderStrings['Dimuon'] = {'pre' :'  {IDX:8s} {TYP:6s}'.format(IDX='ID', TYP='type'),
                           'post':'{NC2:>10s} {DR:>8s} {DPHI:>8s} {CA:>8s} {LXY:>7s} {LXYS:>7s} {LXYPV:>7s} {LXYSPV:>9s} {ISOP:>8s} {ISOL:>8>}'.format(
                                NC2='normChi2', DR='deltaR', DPHI='deltaPhi', CA='cosAlpha', LXY='Lxy', LXYS='LxySig', LXYPV='PV-Lxy', LXYSPV='PV-LxySig', ISOP='isoPmumu', ISOL='isoLxy')}
DataStrings  ['Dimuon'] = {'pre' : '  {idx1:2d}  {idx2:2d}   {composition:6s}',
                           'post':'{normChi2:10.2f} {deltaR:8.2f} {deltaPhi:8.2f} {cosAlpha:8.2f} {Lxy:7.2f} {LxySig:7.2f} {LxyPV:7.2f} {LxySigPV:9.2f} {isoPmumu:8.3f} {isoLxy:8.3f}'}

# Alt Title Strings
TitleStrings['AltDSA'] = '=== DSA MUONS ==='
TitleStrings['AltRSA'] = '=== RSA MUONS ==='
TitleStrings['AltPAT'] = '=== PAT MUONS ==='
TitleStrings['AltGen'] = '=== GEN MUONS ==='
