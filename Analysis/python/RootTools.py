import ROOT as R

#### Improved Vector Classes
def genericDist(self, second):
    return (self-vec).Mag()
def genericInverse(self):
    return self.__class__(*[1./component for component in self])
def genericFormat(self, format_spec):
    if format_spec.endswith('p'):
        fstring = '(' + ', '.join(['{{{index}:{{fs}}}}'.format(index=i) for i in range(len(self))]) + ')'
        return fstring.format(*self, fs=format_spec[:-1]+'f')
    else:
        return self.__format__(format_spec)

for CLASS in R.TLorentzVector, R.TVector3, R.TVector2:
    CLASS.Dist       = genericDist
    CLASS.Inverse    = genericInverse
    CLASS.__format__ = genericFormat

# TLorentzVector and TVector2 don't implement an iterator (for..in or *) or a length, but TVector3 does
R.TLorentzVector.__len__  = lambda self : 4
R.TLorentzVector.__iter__ = lambda self : iter([self[0], self[1], self[2], self[3]])
R.TVector2.__len__  = lambda self : 2
R.TVector2.__iter__ = lambda self : iter([self.X(), self.Y()])

# TVector2 doesn't implement indexing
R.TVector2.__getitem__ = lambda self, index : [self.X(), self.Y()][index]

# TVector2 doesn't do __mul__ correctly. Also, make Mag() return Mod().
def fixedMul(self, second):
    try:
        return self.X()*second.X() + self.Y()*second.Y()
    except:
        return R.TVector2(self.X()*second, self.Y()*second)
R.TVector2.__mul__ = fixedMul
R.TVector2.__rmul__ = fixedMul
R.TVector2.Mag = R.TVector2.Mod

# It's often useful to take a TVector3 (x, y, z) and return (x, y, 0)
def Proj2D(self):
    return R.TVector3(self.X(), self.Y(), 0.)
R.TVector3.Proj2D = Proj2D

#### TTree Tools
# takes an ntuple tree with gen_ branches of length 8
# sets tree aliases for use in formulae
# takes an optional "signal" argument for naming the particles differently
def setGenAliases(t, signal='4Mu'):
    if signal == '4Mu':
        plist = ('mu11', 'mu12', 'mu21', 'mu22', 'X1', 'X2', 'H', 'P')
    elif signal == '2Mu2J':
        plist = ('mu1', 'mu2', 'j1', 'j2', 'X', 'XP', 'H', 'P')
    for i, particle in enumerate(plist):
        for attribute in ('pdgID', 'pt', 'eta', 'phi', 'mass', 'energy', 'charge', 'x', 'y', 'z', 'd0', 'dz', 'cosAlpha', 'Lxy', 'deltaR'):
            if attribute in ('d0', 'dz', 'cosAlpha', 'Lxy', 'deltaR') and particle[0:2] != 'mu' and particle[0] != 'j': continue
            t.SetAlias(particle+'.'+attribute, 'gen_'+attribute+'['+str(i)+']')

#### Histogram Tools
# appends '/ binwidth' to axes, with cm or GeV as appropriate
# works for any 1D type plot, basically unless TH2 is in the title
# TH2s just skip the process; to do: add a TH2 version
def addBinWidth(plot, floatFormat=None):
    try:
        if 'TH2' in str(plot.plot.__class__):
            TYPE = '2D'
        else:
            TYPE = '1D'
    except:
        if 'TH2' in str(plot.__class__):
            TYPE = '2D'
        else:
            TYPE = '1D'

    if TYPE == '1D':
        yAxisTitle = plot.GetYaxis().GetTitle()
        xAxisTitle = plot.GetXaxis().GetTitle()
        binWidth = plot.GetXaxis().GetBinWidth(1)
        if binWidth.is_integer():
            binWidth = int(binWidth)
            binWidthString = ' / {:d}'.format(binWidth)
        else:
            if floatFormat is None:
                binWidthString = ' / {:.2f}'.format(binWidth)
                if binWidthString == ' / 0.00':
                    binWidthString = ' / {:.2e}'.format(binWidth)
            else:
                binWidthString = (' / {:'+floatFormat+'}').format(binWidth)
        if 'GeV' in xAxisTitle:
            units = ' GeV'
        elif 'cm' in xAxisTitle:
            units = ' cm'
        else:
            units = ''
        plot.setTitles(Y=yAxisTitle + binWidthString + units)

# add the content of the underflow and overflow bins to the end bins
def addFlows(plot, overflow=True, underflow=True):
    try:
        if 'TH2' in str(plot.plot.__class__):
            TYPE = '2D'
        else:
            TYPE = '1D'
    except:
        if 'TH2' in str(plot.__class__):
            TYPE = '2D'
        else:
            TYPE = '1D'

    if TYPE == '1D':
        NBins = plot.GetNbinsX()
        if overflow:
            plot.SetBinContent(NBins, plot.GetBinContent(NBins)+plot.GetBinContent(NBins+1))
        if underflow:
            plot.SetBinContent(1    , plot.GetBinContent(1    )+plot.GetBinContent(0      ))
