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

# TLorentzVector doesn't implement an iterator (for..in or *) or a length, but TVector2/3 do
R.TLorentzVector.__len__  = lambda self : 4
R.TLorentzVector.__iter__ = lambda self : iter([self[0], self[1], self[2], self[3]])

# TVector2 doesn't do __mul__ correctly. Also, make Mag() return Mod().
def fixedMul(self, second):
    try:
        return self.X()*second.X() + self.Y()*second.Y()
    except:
        return R.TVector2(self.X()*second, self.Y()*second)
R.TVector2.__mul__ = fixedMul
R.TVector2.__rmul__ = fixedMul
R.TVector2.Mag = R.TVector2.Mod

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
def addBinWidth(plot):
    yAxisTitle = plot.GetYaxis().GetTitle()
    xAxisTitle = plot.GetXaxis().GetTitle()
    binWidth = plot.GetXaxis().GetBinWidth(1)
    if binWidth.is_integer():
        binWidth = int(binWidth)
        binWidthString = ' / {:d}'.format(binWidth)
    else:
        binWidthString = ' / {:.2f}'.format(binWidth)
    if 'GeV' in xAxisTitle:
        units = ' GeV'
    elif 'cm' in xAxisTitle:
        units = ' cm'
    else:
        units = ''
    plot.setTitles(Y=yAxisTitle + binWidthString + units)
