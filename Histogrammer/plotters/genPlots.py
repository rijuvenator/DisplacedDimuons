import ROOT as R
import DisplacedDimuons.Histogrammer.Plotter as Plotter
import DisplacedDimuons.Histogrammer.Primitives as Primitives
from DisplacedDimuons.Histogrammer.Primitives import Point
import DisplacedDimuons.Histogrammer.RootTools as RT
from DisplacedDimuons.Histogrammer.Constants import DIR_DD, DIR_WS, SIGNALS

# this works for a tuple OR 3 arguments
def SPStr(*args):
	if len(args) == 3:
		return '{}_{}_{}'.format(*args)
	elif len(args) == 1:
		return '{}_{}_{}'.format(*args[0])

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

		# this seems to be a nice upper limits for X PT
		XPtUpper = (mH-mX)*1.4
		
		# actual init code. saves constructor argument for each histogram type
		self.keys = ('massH', 'massX', 'cTau', 'pTH', 'pTX', 'beta', 'Lxy', 'd0', 'Lxyz')
		self.attr = ('name', 'xTitle', 'yTitle', 'nBins', 'binLow', 'binHigh')

		def HName(key): return key + '_' + SPStr(mH, mX, cTau)

		self.data = {}
		self.data['massH'] = self.makeAttrDict((HName('massH'), 'Higgs Mass [GeV]' , 'Counts', 100, mH*(1-HErr), mH*(1+HErr)))
		self.data['massX'] = self.makeAttrDict((HName('massX'), 'X Mass [GeV]'     , 'Counts', 100, mX*(1-XErr), mX*(1+XErr)))
		self.data['cTau' ] = self.makeAttrDict((HName('cTau' ), 'c#tau [mm]'       , 'Counts', 100, 0.         , cTau*6.    ))
		self.data['pTH'  ] = self.makeAttrDict((HName('pTH'  ), 'Higgs p_{T} [GeV]', 'Counts', 100, 0.         , HPtUpper   ))
		self.data['pTX'  ] = self.makeAttrDict((HName('pTX'  ), 'X p_{T} [GeV]'    , 'Counts', 100, 0.         , XPtUpper   ))
		self.data['beta' ] = self.makeAttrDict((HName('beta' ), '#beta = v/c'      , 'Counts', 100, 0.         , 1.         ))
		self.data['Lxy'  ] = self.makeAttrDict((HName('Lxy'  ), 'L_{xy} [mm]'      , 'Counts', 100, 0.         , LxyUpper   ))
		self.data['Lxyz' ] = self.makeAttrDict((HName('Lxyz' ), 'L_{xyz} [mm]'     , 'Counts', 100, 0.         , LxyUpper   ))
		self.data['d0'   ] = self.makeAttrDict((HName('d0'   ), 'd_{0} [mm]'       , 'Counts', 100, 0.         , cTau*2.    ))
	
	def HName(self, key):
		return key + '_' + SPStr(self.mH, self.mX, self.cTau)

	def makeAttrDict(self, tup):
		assert len(tup) == len(self.attr)
		return dict(zip(self.attr, tup))

	def __getitem__(self, key):
		AD = self.data[key]
		return AD['name'], ';{};{}'.format(AD['xTitle'], AD['yTitle']), AD['nBins'], AD['binLow'], AD['binHigh']

# empty histogram dictionary
HISTS = {}

def fillPlots(sp):
	f = R.TFile.Open(DIR_WS + 'genOnly_ntuple_{}.root'.format(SPStr(sp)))
	t = f.Get('GenOnlyNTupler/DDTree')

	RT.setGenAliases(t)

	HConfig = HistogramConfigurations(sp)

	HISTS[sp] = {}

	for key in HConfig.keys:
		HISTS[sp][key] = R.TH1F(*HConfig[key])

	t.SetAlias('cTau1' , 'X1.mass/sqrt(pow(X1.energy,2)-pow(X1.mass,2))*sqrt(pow(mu11.x-X1.x,2) + pow(mu11.y-X1.y,2) + pow(mu11.z-X1.z,2))*10.')
	t.SetAlias('cTau2' , 'X2.mass/sqrt(pow(X2.energy,2)-pow(X2.mass,2))*sqrt(pow(mu21.x-X2.x,2) + pow(mu21.y-X2.y,2) + pow(mu21.z-X2.z,2))*10.')
	t.SetAlias('beta1' , 'sqrt(pow(X1.energy,2)-pow(X1.mass,2))/X1.energy')
	t.SetAlias('beta2' , 'sqrt(pow(X2.energy,2)-pow(X2.mass,2))/X2.energy')
	t.SetAlias('Lxy1'  , 'sqrt(pow(mu11.x-X1.x,2) + pow(mu11.y-X1.y,2))*10.')
	t.SetAlias('Lxy2'  , 'sqrt(pow(mu21.x-X2.x,2) + pow(mu21.y-X2.y,2))*10.')
	t.SetAlias('Lxyz1' , 'sqrt(pow(mu11.x-X1.x,2) + pow(mu11.y-X1.y,2) + pow(mu11.z-X1.z,2))*10.')
	t.SetAlias('Lxyz2' , 'sqrt(pow(mu21.x-X2.x,2) + pow(mu21.y-X2.y,2) + pow(mu21.z-X2.z,2))*10.')
	t.SetAlias('d01'   , 'min(gen_d0[0],gen_d0[1])*10.')
	t.SetAlias('d02'   , 'min(gen_d0[2],gen_d0[3])*10.')

	t.Draw('H.mass>>{}'  .format(HConfig.data['massH']['name']))
	t.Draw('X1.mass>>{}' .format(HConfig.data['massX']['name']))
	t.Draw('X2.mass>>+{}'.format(HConfig.data['massX']['name']))
	t.Draw('cTau1>>{}'   .format(HConfig.data['cTau' ]['name']))
	t.Draw('cTau2>>+{}'  .format(HConfig.data['cTau' ]['name']))
	t.Draw('H.pt>>{}'    .format(HConfig.data['pTH'  ]['name']))
	t.Draw('X1.pt>>{}'   .format(HConfig.data['pTX'  ]['name']))
	t.Draw('X2.pt>>+{}'  .format(HConfig.data['pTX'  ]['name']))
	t.Draw('beta1>>{}'   .format(HConfig.data['beta' ]['name']))
	t.Draw('beta2>>+{}'  .format(HConfig.data['beta' ]['name']))
	t.Draw('Lxy1>>{}'    .format(HConfig.data['Lxy'  ]['name']))
	t.Draw('Lxy2>>+{}'   .format(HConfig.data['Lxy'  ]['name']))
	t.Draw('Lxyz1>>{}'   .format(HConfig.data['Lxyz' ]['name']))
	t.Draw('Lxyz2>>+{}'  .format(HConfig.data['Lxyz' ]['name']))

	t.Draw('{}>>{}'      .format('min(gen_d0[0],gen_d0[1]*10.)', HConfig.data['d0'   ]['name']))
	t.Draw('{}>>+{}'     .format('min(gen_d0[2],gen_d0[3]*10.)', HConfig.data['d0'   ]['name']))

	for key in HConfig.keys:
		HISTS[sp][key].SetDirectory(0)

	del t
	f.Close()
	del f

def makePlot(sp, name):
	h = HISTS[sp][name]

	p = Plotter.Plot(h, '', 'p', 'hist')
	canvas = Plotter.Canvas()
	canvas.addMainPlot(p)
	p.SetLineColor(R.kBlue)
	canvas.drawText('#mu = {:.4f}'   .format(h.GetMean())  , (.18, .8    ))
	canvas.drawText('#sigma = {:.4f}'.format(h.GetStdDev()), (.18, .8-.04))
	canvas.makeTransparent()
	canvas.finishCanvas()
	canvas.save('pdfs/{}_{}.pdf'.format(name, SPStr(sp)))
	canvas.deleteCanvas()

for mH in SIGNALS:
	for mX in SIGNALS[mH]:
		for cTau in SIGNALS[mH][mX]:
			sp = (mH, mX, cTau)

			fillPlots(sp)

			#makePlot(sp, 'massH')
			#makePlot(sp, 'massX')
			#makePlot(sp, 'cTau')
			#makePlot(sp, 'pTH')
			#makePlot(sp, 'pTX')
			#makePlot(sp, 'beta')
			#makePlot(sp, 'cTauM')
			#makePlot(sp, 'Lxy')
			makePlot(sp, 'Lxyz')
			#makePlot(sp, 'd0')

			print 'Did', sp

# loop over tree code
	#BRANCHKEYS = ('EVENT', 'GEN')
	#Primitives.SelectBranches(t, BRANCHKEYS)
	#for i, event in enumerate(t):
	#	#if i == 10: break

	#	E = Primitives.ETree(t, BRANCHKEYS)
	#	mu11, mu12, mu21, mu22, X1, X2, H, P = E.getPrimitives('GEN')

	#	HISTS[sp]['massH'].Fill(H .mass)
	#	HISTS[sp]['massX'].Fill(X1.mass)
	#	HISTS[sp]['massX'].Fill(X2.mass)
	#	HISTS[sp]['cTau' ].Fill(X1.mass / X1.p3.norm() * Point.dist(mu11.pos, X1.pos) * 10)
	#	HISTS[sp]['cTau' ].Fill(X2.mass / X2.p3.norm() * Point.dist(mu21.pos, X2.pos) * 10)

# cTau M legacy code

	#self.data['cTauM'] = self.makeAttrDict((HName('cTauM'), 'c#tau [mm]'       , 'Counts', 100, 0.         , cTau*6.    ))
	#t.SetAlias('cTauM1', 'X1.mass/X1.energy*sqrt(pow(mu11.x-X1.x,2) + pow(mu11.y-X1.y,2) + pow(mu11.z-X1.z,2))*10.')
	#t.SetAlias('cTauM2', 'X2.mass/X2.energy*sqrt(pow(mu21.x-X2.x,2) + pow(mu21.y-X2.y,2) + pow(mu21.z-X2.z,2))*10.')
	#t.Draw('cTauM1>>{}'  .format(HConfig.data['cTauM']['name']))
	#t.Draw('cTauM2>>+{}' .format(HConfig.data['cTauM']['name']))
