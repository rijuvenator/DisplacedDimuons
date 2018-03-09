import ROOT as R
import DisplacedDimuons.Histogrammer.Plotter as Plotter
import DisplacedDimuons.Histogrammer.RootTools as RT
from DisplacedDimuons.Histogrammer.Constants import DIR_DD, DIR_WS, SIGNALS
from DisplacedDimuons.Histogrammer.Utilities import SPStr

#### CLASS AND FUNCTION DEFINITIONS ####
# histogram configuration object
# declared once per signal point and calculates all the histogram properties
# add new histograms here
class HistogramConfigurations(object):
	def __init__(self, sp):
		mH, mX, cTau = sp
		self.mH, self.mX, self.cTau = mH, mX, cTau

		# these values help calculate useful bin limits
		HErr = (0.05 if mH != 1000 else 0.30) * 3/2.
		XErr = 0.005

		# the Lxy upper is best set by whether it's the min, mid, or max cTau
		LxyUppers = [150., 1500., 15000.]
		LxyUpper = LxyUppers[SIGNALS[mH][mX].index(cTau)]

		# all the H PT seem to fit in 0-250
		HPtUpper = 250.

		# this seems to be a nice upper limit for X PT
		XPtUpper = (mH-mX)*1.4

		# muon pT seems to depend only on Higgs mass
		MuPtUpper = mH/2.

		# actual init code. saves constructor argument for each histogram type
		self.keys = ('massH', 'massX', 'cTau', 'pTH', 'pTX', 'beta', 'Lxy', 'd0', 'pTmu', 'd00')
		self.attr = ('name', 'xTitle', 'yTitle', 'nBins', 'binLow', 'binHigh')

		self.data = {}
		self.data['massH'] = self.makeAttrDict((self.HName('massH'), 'Higgs Mass [GeV]' , 'Counts', 100, mH*(1-HErr), mH*(1+HErr)))
		self.data['massX'] = self.makeAttrDict((self.HName('massX'), 'X Mass [GeV]'     , 'Counts', 100, mX*(1-XErr), mX*(1+XErr)))
		self.data['cTau' ] = self.makeAttrDict((self.HName('cTau' ), 'c#tau [mm]'       , 'Counts', 100, 0.         , cTau*6.    ))
		self.data['pTH'  ] = self.makeAttrDict((self.HName('pTH'  ), 'Higgs p_{T} [GeV]', 'Counts', 100, 0.         , HPtUpper   ))
		self.data['pTX'  ] = self.makeAttrDict((self.HName('pTX'  ), 'X p_{T} [GeV]'    , 'Counts', 100, 0.         , XPtUpper   ))
		self.data['beta' ] = self.makeAttrDict((self.HName('beta' ), '#beta = v/c'      , 'Counts', 100, 0.         , 1.         ))
		self.data['Lxy'  ] = self.makeAttrDict((self.HName('Lxy'  ), 'L_{xy} [mm]'      , 'Counts', 100, 0.         , LxyUpper   ))
		self.data['d0'   ] = self.makeAttrDict((self.HName('d0'   ), 'd_{0} [mm]'       , 'Counts', 100, 0.         , cTau*2.    ))
		self.data['pTmu' ] = self.makeAttrDict((self.HName('pTmu' ), '#mu p_{T} [GeV]'  , 'Counts', 100, 0.         , MuPtUpper  ))
		self.data['d00'  ] = self.makeAttrDict((self.HName('d00'  ), '#Deltad_{0} [cm]' , 'Counts', 100, -.1        , .1         ))

	def HName(self, key):
		return key + '_' + SPStr(self.mH, self.mX, self.cTau)

	def makeAttrDict(self, tup):
		assert len(tup) == len(self.attr)
		return dict(zip(self.attr, tup))

	def __getitem__(self, key):
		AD = self.data[key]
		return AD['name'], ';{};{}'.format(AD['xTitle'], AD['yTitle']), AD['nBins'], AD['binLow'], AD['binHigh']

# wrapper for TTree::Draw
def Draw(t, HConfig, key, expressions):
	for i, expr in enumerate(expressions):
		t.Draw('{expr}>>{isFirst}{hName}'.format(expr=expr, isFirst='' if i==0 else '+', hName=HConfig.HName(key)))

# opens file, gets tree, sets aliases, declares histograms, fills histograms, closes file
def fillPlots(sp, HList):
	# get file and tree
	f = R.TFile.Open(DIR_WS + 'genOnly_ntuple_{}.root'.format(SPStr(sp)))
	t = f.Get('GenOnlyNTupler/DDTree')

	# set basic particle aliases
	RT.setGenAliases(t)

	# set additional aliases from HAliases
	for alias, expr in HAliases.iteritems():
		t.SetAlias(alias, expr)

	# define histogram configurations for this signal point
	HConfig = HistogramConfigurations(sp)

	# declare histograms
	# make sure histograms don't get deleted when file is closed
	# fill histograms using TTree::Draw
	for key in HList:
		HISTS[sp][key] = R.TH1F(*HConfig[key])
		Draw(t, HConfig, key, HExpressions[key])
		HISTS[sp][key].SetDirectory(0)

	# cleanup
	del t
	f.Close()
	del f

# makes plot using Plotter class
def makePlots(sp, HList):
	for key in HList:
		h = HISTS[sp][key]

		p = Plotter.Plot(h, '', 'p', 'hist')
		canvas = Plotter.Canvas()
		canvas.addMainPlot(p)
		p.SetLineColor(R.kBlue)
		canvas.drawText('#color[4]{' + '#bar{{x}} = {:.4f}'   .format(h.GetMean())   + '}', (.7, .8    ))
		canvas.drawText('#color[4]{' + 's = {:.4f}'           .format(h.GetStdDev()) + '}', (.7, .8-.04))
		canvas.makeTransparent()
		canvas.finishCanvas()
		canvas.save('pdfs/{}_{}.pdf'.format(key, SPStr(sp)))
		canvas.deleteCanvas()

#### ALL GLOBAL VARIABLES DECLARED HERE ####
# empty histogram dictionary
HISTS = {}

# list of histogram keys to actually fill this time
#HList = (
#	'massH',
#	'massX',
#	'cTau',
#	'pTH',
#	'pTX',
#	'beta',
#	'Lxy',
#	'd0',
#	'pTmu',
#	'd00',
#)
# for parallelizing with : parallel python genPlots.py ::: massH massX cTau pTH pTX beta Lxy d0 pTmu d00
import sys
HList = (sys.argv[-1],)

# TTree aliases: alias : expr
HAliases = {
	'cTau1' : 'X1.mass/sqrt(pow(X1.energy,2)-pow(X1.mass,2))*sqrt(pow(mu11.x-X1.x,2) + pow(mu11.y-X1.y,2) + pow(mu11.z-X1.z,2))*10.',
	'cTau2' : 'X2.mass/sqrt(pow(X2.energy,2)-pow(X2.mass,2))*sqrt(pow(mu21.x-X2.x,2) + pow(mu21.y-X2.y,2) + pow(mu21.z-X2.z,2))*10.',
	'beta1' : 'sqrt(pow(X1.energy,2)-pow(X1.mass,2))/X1.energy',
	'beta2' : 'sqrt(pow(X2.energy,2)-pow(X2.mass,2))/X2.energy',
	'Lxy1'  : 'sqrt(pow(mu11.x-X1.x,2) + pow(mu11.y-X1.y,2))*10.',
	'Lxy2'  : 'sqrt(pow(mu21.x-X2.x,2) + pow(mu21.y-X2.y,2))*10.',
	'd01'   : 'TMath::Min(mu11.d0,mu12.d0)*10.',
	'd02'   : 'TMath::Min(mu21.d0,mu22.d0)*10.',
	'd0011' : 'TMath::Abs(mu11.x*mu11.pt*TMath::Sin(mu11.phi)-mu11.y*mu11.pt*TMath::Cos(mu11.phi))/mu11.pt-mu11.d0',
	'd0012' : 'TMath::Abs(mu12.x*mu12.pt*TMath::Sin(mu12.phi)-mu12.y*mu12.pt*TMath::Cos(mu12.phi))/mu12.pt-mu12.d0',
	'd0021' : 'TMath::Abs(mu21.x*mu21.pt*TMath::Sin(mu21.phi)-mu21.y*mu21.pt*TMath::Cos(mu21.phi))/mu21.pt-mu21.d0',
	'd0022' : 'TMath::Abs(mu22.x*mu22.pt*TMath::Sin(mu22.phi)-mu22.y*mu22.pt*TMath::Cos(mu22.phi))/mu22.pt-mu22.d0',
}

# TTree draw configuration: histogram name : (list of Draw expressions)
HExpressions = {
	'massH' : ('H.mass',),
	'massX' : ('X1.mass', 'X2.mass'),
	'cTau'  : ('cTau1', 'cTau2'),
	'pTH'   : ('H.pt',),
	'pTX'   : ('X1.pt', 'X2.pt'),
	'beta'  : ('beta1', 'beta2'),
	'Lxy'   : ('Lxy1', 'Lxy2'),
	'd0'    : ('d01', 'd02'),
	'pTmu'  : ('mu11.pt', 'mu12.pt', 'mu21.pt', 'mu22.pt'),
	'd00'   : ('d0011', 'd0012', 'd0021', 'd0022'),
}

#### MAIN CODE ####
# loop over signal points
for mH in SIGNALS:
	for mX in SIGNALS[mH]:
		for cTau in SIGNALS[mH][mX]:
			sp = (mH, mX, cTau)
			HISTS[sp] = {}

			fillPlots(sp, HList)
			makePlots(sp, HList)

			print 'Did', sp
