import ROOT as R
import numpy as n
R.PyConfig.IgnoreCommandLineOptions = True
R.gROOT.SetBatch(True)

# Imporant note: any functions that manipulate things based on text size assume that
# the containing pad is wider than it is tall. In this case, the character height is
# obtained as a fraction of the pad height, rather than the pad width. A tall, narrow
# pad may cause unexpected behavior in this regard. All text defaults to 4% of height

# Plot, Legend, and Canvas inherit (or pretend to inherit) from their respective ROOT objects
# So anything one would call on the TH1F inside plot or TLegend or TCanvas can be called
# on the Plot, Legend, or Canvas object themselves.
# Note that Plot does not inherit 

# globalSetStyle function, based on TDRStyle, but more flexible
# This function is called ONCE, changing all of the fixed parameters
# Then setStyle is called, changing all of the variable parameters, once per plot
def globalSetStyle():
	style = R.TStyle('style','Style')

	# rainbow
	style.SetPalette(55)

	# generic line thicknesses
	style.SetLineWidth(2)

	# canvas
	style.SetCanvasBorderMode(0)             # off
	style.SetCanvasColor(R.kWhite)           # white

	# pad
	style.SetPadBorderMode(0)                # off
	style.SetPadColor(R.kWhite)              # white
	style.SetPadGridX(R.kFALSE)              # grid x
	style.SetPadGridY(R.kFALSE)              # grid y
	style.SetGridColor(R.kGray)              # gray
	style.SetGridStyle(3)                    # dotted
	style.SetGridWidth(1)                    # pixels

	# frame
	style.SetFrameBorderMode(0)              # off
	style.SetFrameFillColor(R.kWhite)        # white
	style.SetFrameFillStyle(0)               # hollow
	style.SetFrameLineColor(R.kWhite)        # white
	style.SetFrameLineStyle(1)               # solid
	style.SetFrameLineWidth(0)               # pixels

	# legend
	style.SetLegendBorderSize(0)             # off

	# hist
	style.SetHistLineColor(R.kBlack)         # black
	style.SetHistLineStyle(1)                # solid
	style.SetHistLineWidth(2)                # pixels
	style.SetMarkerStyle(R.kFullDotLarge)    # marker
	style.SetMarkerColor(R.kBlack)           # black
	style.SetEndErrorSize(0)                 # no little lines on errors

	# stats box
	style.SetOptStat(0)                      # off

	# fit box
	style.SetOptFit(1)                       # on

	# title
	style.SetOptTitle(0)                     # off
	style.SetTitleTextColor(R.kBlack)        # black
	style.SetTitleStyle(0)                   # hollow
	style.SetTitleFillColor(R.kWhite)        # white
	style.SetTitleBorderSize(0)              # default 2
	style.SetTitleAlign(22)                  # center top

	# axis titles
	style.SetTitleColor(R.kBlack, 'XYZ')     # black
	style.SetTitleOffset(1,'X')              # default 1
	style.SetTitleOffset(1.25,'Y')           # default 1

	# axis labels
	style.SetLabelColor(R.kBlack, 'XYZ')     # black
	style.SetLabelOffset(0.005,'XYZ')        # default 0.005

	# axis
	style.SetAxisColor(R.kBlack, 'XYZ')      # black
	style.SetStripDecimals(R.kTRUE)          # strip decimals
	style.SetPadTickX(1)                     # opposite x ticks
	style.SetPadTickY(1)                     # opposite y ticks

	style.cd()
globalSetStyle()

# setStyle function, based on TDRStyle, but more flexible
def setStyle(width=800, height=600, font=42, fontsize=0.04):
	style = R.gStyle

	width = width
	height = height
	font = font
	tMargin = 0.1
	lMargin = 0.125
	fontsize = float(fontsize)

	rMargin = tMargin * float(height) / float(width)
	bMargin = lMargin
	titleX = lMargin + (1-lMargin-rMargin)/2
	titleY = 1 - (tMargin/2)

	# canvas
	style.SetCanvasDefW(width)               # width
	style.SetCanvasDefH(height)              # height

	# pad margins
	style.SetPadTopMargin(tMargin)           # default 0.1
	style.SetPadBottomMargin(bMargin)        # default 0.1
	style.SetPadLeftMargin(lMargin)          # default 0.1
	style.SetPadRightMargin(rMargin)         # default 0.1

	# legend
	style.SetLegendFont(font)                # helvetica normal
	style.SetLegendTextSize(fontsize)        # default 0

	# title
	style.SetTitleFont(font,'')              # helvetica normal
	style.SetTitleFontSize(fontsize)         # default 0
	style.SetTitleX(titleX)                  # center title horizontally with respect to frame
	style.SetTitleY(titleY)                  # center title vertically within margin

	# axis titles
	style.SetTitleFont(font, 'XYZ')          # helvetica normal
	style.SetTitleSize(fontsize, 'XYZ')      # default 0.02

	# axis labels
	style.SetLabelFont(font, 'XYZ')          # helvetica normal
	style.SetLabelSize(fontsize, 'XYZ')      # default 0.04

	style.cd()

# Enhances a plot object, expected to be a hist, graph, or hstack
# legName is the legend display name, legType is the legend symbol draw option, option is the draw option
class Plot(object):
	def __init__(self, plot, legName='hist', legType='felp', option=''):
		self.plot = plot
		self.legName = legName
		self.legType = legType
		self.option = option
	
	# allows Plot objects to behave as if they were inherited from plot
	def __getattr__(self, name):
		return getattr(self.plot, name)

	# scales axis title sizes
	def scaleTitles(self, factor, axes='XY'):
		if 'X' in axes: self.GetXaxis().SetTitleSize(self.GetXaxis().GetTitleSize() * float(factor))
		if 'Y' in axes: self.GetYaxis().SetTitleSize(self.GetYaxis().GetTitleSize() * float(factor))
		if 'Z' in axes: self.GetZaxis().SetTitleSize(self.GetZaxis().GetTitleSize() * float(factor))

	# scales axis label sizes
	def scaleLabels(self, factor, axes='XY'):
		if 'X' in axes: self.GetXaxis().SetLabelSize(self.GetXaxis().GetLabelSize() * float(factor))
		if 'Y' in axes: self.GetYaxis().SetLabelSize(self.GetYaxis().GetLabelSize() * float(factor))
		if 'Z' in axes: self.GetZaxis().SetLabelSize(self.GetZaxis().GetLabelSize() * float(factor))
	
	# scales axis title offsets from axis
	def scaleTitleOffsets(self, factor, axes='XY'):
		if 'X' in axes: self.GetXaxis().SetTitleOffset(self.GetXaxis().GetTitleOffset() * float(factor))
		if 'Y' in axes: self.GetYaxis().SetTitleOffset(self.GetYaxis().GetTitleOffset() * float(factor))
		if 'Z' in axes: self.GetZaxis().SetTitleOffset(self.GetZaxis().GetTitleOffset() * float(factor))
	
	# sets axis titles
	def setTitles(self, X=None, Y=None, Z=None):
		if X is not None: self.GetXaxis().SetTitle(X)
		if Y is not None: self.GetYaxis().SetTitle(Y)
		if Z is not None: self.GetZaxis().SetTitle(Z)

# Enhances a TLegend, providing some much needed geometry functionality
# X1, X2, Y1, Y2 construct the parent TLegend object; corner is a pos string (see Canvas)
class Legend(R.TLegend):
	def __init__(self, X1, Y1, X2, Y2, corner):
		R.TLegend.__init__(self, X1, Y1, X2, Y2)
		self.lines = 0
		self.corner = corner

	# wrapper for adding legend entries; keeps track of the number of entries
	def addLegendEntry(self, plot):
		self.AddEntry(plot.plot, plot.legName, plot.legType)
		self.lines += 1
	
	# moves the entire legend X, Y units in the x and y directions
	def moveLegend(self, X=0., Y=0.):
		self.SetX1(self.GetX1() + X)
		self.SetX2(self.GetX2() + X)
		self.SetY1(self.GetY1() + Y)
		self.SetY2(self.GetY2() + Y)
	
	# moves the L, R, T, B edges. Positive is right/up; negative is left/down
	def moveEdges(self, L=0., R=0., T=0., B=0.):
		self.SetX1(self.GetX1() + L)
		self.SetX2(self.GetX2() + R)
		self.SetY1(self.GetY1() + B)
		self.SetY2(self.GetY2() + T)
	
	# resizes the legend bounding box based on the number of entries
	# scale allows for some extra padding if desired
	def resizeHeight(self, scale=1.):
		fontsize = self.GetTextSize()
		oldheight = self.GetY2() - self.GetY1()
		newheight = self.lines * fontsize * scale * 1.1
		resize = newheight - oldheight
		# Assume the anchoring corner is in the correct spot
		if self.corner[0] == 't':
			self.moveEdges(B=-resize) # resize > 0 = move B down = negative
		elif self.corner[0] == 'b':
			self.moveEdges(T=resize)  # resize > 0 = move T up   = positive

# Canvas class: enhances a TCanvas by providing several methods for organizing and automating plotting
# cWidth is canvas width, cHeight is canvas height
# fontcode is a string controlling the global font characteristics; see drawText below
# fontscale is a scale factor for resizing globally the font size (defaulting to 0.04 of the height)
# logy is if canvas should be log y scale
# lumi is lumi text (top right), extra is text that follows CMS (top left)
# ratiofactor is fraction of canvas devoted to ratio plot
class Canvas(R.TCanvas):
	def __init__(self, logy=False, lumi='', ratioFactor=0, extra='Internal', cWidth=800, cHeight=600, fontcode='', fontscale=1.):
		self.cWidth      = cWidth
		self.cHeight     = cHeight
		self.fontcode    = fontcode
		self.lumi        = lumi
		self.extra       = extra
		self.logy        = logy
		self.ratioFactor = float(ratioFactor)

		self.legend      = None
		self.plotList    = []
		self.axesDrawn   = False
		self.fontsize    = 0.04

		FontDict = {'' : 4, 'i' : 5, 'b' : 6, 'bi' : 7}
		self.font = 10 * FontDict[fontcode] + 2

		setStyle(self.cWidth,self.cHeight,self.font,self.fontsize*fontscale)

		R.TCanvas.__init__(self, 'c','Canvas',self.cWidth,self.cHeight)

		self.mainPad = R.TPad('main','Main',0,self.ratioFactor,1,1)
		
		if (self.ratioFactor != 0):
			tMargin = self.GetTopMargin()
			lMargin = self.GetLeftMargin()
			rMargin = self.GetRightMargin()

			self.mainPad.SetBottomMargin(0.04)
			self.mainPad.SetRightMargin (tMargin * (self.cHeight * (1 - self.ratioFactor)) / self.cWidth)
			self.ratPad = R.TPad('ratio','Ratio',0,0,1,self.ratioFactor)
			self.ratPad.SetTopMargin(0.04)
			self.ratPad.SetBottomMargin(lMargin * (1 - self.ratioFactor)/self.ratioFactor)
			self.ratPad.SetRightMargin (tMargin * (self.cHeight * (1 - self.ratioFactor)) / self.cWidth)
			self.ratPad.Draw()

		self.mainPad.Draw()
		self.mainPad.SetLogy(self.logy)

	# adds a plot Plot to the main pad
	# the order in which this is called determines the draw order
	# the first plot controls the axes, labels, titles, etc. and is referred to as firstPlot
	# by default, the draw order (stored in plotList) is also used for the legend order
	# just in case, if necessary, addToPlotList won't add a plot to plotList
	def addMainPlot(self, plot, addToPlotList=True):
		plot.UseCurrentStyle()
		self.cd()
		self.mainPad.cd()
		if addToPlotList: self.plotList.append(plot)

		if not self.axesDrawn:
			self.axesDrawn = True
			self.firstPlot = plot
			if type(plot.plot) in [R.TGraph,R.TGraphErrors,R.TGraphAsymmErrors]:
				plot.Draw('A'+plot.option)
			else:
				plot.Draw(plot.option)
			plot.GetXaxis().CenterTitle()
			plot.GetYaxis().CenterTitle()

			if self.ratioFactor != 0:
				plot.GetXaxis().SetLabelSize(0)
		else:
			plot.Draw(plot.option+' same')

	# sets the canvas maximum to 5% above the maximum of all the plots in plotList
	def setMaximum(self):
		self.firstPlot.SetMaximum(1.05 * max([p.GetMaximum() for p in self.plotList]))

	# creates the legend
	# lWidth is width as fraction of pad; height defaults to 0.2, offset defaults to 0.03
	# pos can be tr, tl, br, bl for each of the four corners
	# fontscale is a scale factor for resizing globally the font size (defaulting to 0.04 of the height)
	# autoOrder is if the legend should get its order from the plotList (draw order) or manually
	# if manually, call addLegendEntry on plot objects in the order desired
	def makeLegend(self, lWidth=0.125, pos='tr', fontscale=1., autoOrder=True):
		tMargin = float(self.mainPad.GetTopMargin())
		lMargin = float(self.mainPad.GetLeftMargin())
		rMargin = float(self.mainPad.GetRightMargin())
		bMargin = float(self.mainPad.GetBottomMargin())

		self.cd()
		self.mainPad.cd()
		xOffset = 0.03
		yOffset = 0.03
		lHeight = 0.2

		X1 = {'r' : 1-rMargin-xOffset-lWidth , 'l' : lMargin+xOffset        }
		X2 = {'r' : 1-rMargin-xOffset        , 'l' : lMargin+xOffset+lWidth }
		Y1 = {'t' : 1-tMargin-yOffset-lHeight, 'b' : bMargin+yOffset        }
		Y2 = {'t' : 1-tMargin-yOffset        , 'b' : bMargin+yOffset+lHeight}

		if pos not in ['tr', 'tl', 'br', 'bl']:
			print 'Invalid legend position string; defaulting to top-right'
			pos = 'tr'

		self.legend = Legend(X1[pos[1]], Y1[pos[0]], X2[pos[1]], Y2[pos[0]], pos)
		self.legend.SetTextSize(fontscale * self.fontsize)
		self.legend.SetFillStyle(0)

		if autoOrder:
			for plot in self.plotList:
				self.addLegendEntry(plot)

	# wrapper for adding legend entries
	def addLegendEntry(self, plot):
		self.legend.addLegendEntry(plot)

	# sets style for the stats box, if there is one
	# owner is the TGraph or TH1 that generated the stats box
	# lWidth is width as fraction of pad, lHeight is height as fraction of pad, lOffset is offset from corner as fraction of pad
	# pos can be tr, tl, br, bl for each of the four corners
	def setFitBoxStyle(self, owner, lWidth=0.3, lHeight=0.15, pos='tl', lOffset=0.05, fontscale=0.75):
		tMargin = float(self.mainPad.GetTopMargin())
		lMargin = float(self.mainPad.GetLeftMargin())
		rMargin = float(self.mainPad.GetRightMargin())
		bMargin = float(self.mainPad.GetBottomMargin())

		self.cd()
		self.mainPad.cd()
		self.mainPad.Update()

		sbox = owner.FindObject('stats')

		sbox.SetFillStyle(0)
		sbox.SetBorderSize(0)
		sbox.SetTextFont(self.font)
		sbox.SetTextSize(fontscale * self.fontsize)

		xOffset = 0.03
		yOffset = 0.03

		X1 = {'r' : 1-rMargin-xOffset-lWidth , 'l' : lMargin+xOffset        }
		X2 = {'r' : 1-rMargin-xOffset        , 'l' : lMargin+xOffset+lWidth }
		Y1 = {'t' : 1-tMargin-yOffset-lHeight, 'b' : bMargin+yOffset        }
		Y2 = {'t' : 1-tMargin-yOffset        , 'b' : bMargin+yOffset+lHeight}

		if pos not in ['tr', 'tl', 'br', 'bl']:
			print 'Invalid legend position string; defaulting to top-left'
			pos = 'tl'

		sbox.SetX1NDC(X1[pos[1]])
		sbox.SetX2NDC(X2[pos[1]])
		sbox.SetY1NDC(Y1[pos[0]])
		sbox.SetY2NDC(Y2[pos[0]])

	# makes ratio plot given a top hist and a bottom hist
	# plusminus is the window around 1, i.e. 0.5 means plot from 0.5 to 1.5
	# ytit is the y axis title, xtit is the x axis title, option is the draw option
	def makeRatioPlot(self, topHist, bottomHist, plusminus=0.5, option='', ytit='Data/MC', xtit=''):
		if self.ratioFactor == 0: return
		self.cd()
		self.ratPad.cd()
		self.ratPad.SetGridy(R.kTRUE)

		self.rat = topHist.Clone()
		bot = bottomHist.Clone()
		self.rat.Divide(bot)

		factor = (1 - self.ratioFactor)/self.ratioFactor

		if (xtit != ''):
			self.rat.GetXaxis().SetTitle(xtit)
		self.rat.GetXaxis().SetTitleSize (self.rat.GetXaxis().GetTitleSize()  * factor)
		self.rat.GetXaxis().SetLabelSize (self.rat.GetYaxis().GetLabelSize()  * factor)
		self.rat.GetXaxis().SetTickLength(self.rat.GetXaxis().GetTickLength() * factor)
		self.rat.GetXaxis().CenterTitle()

		self.rat.GetYaxis().SetTitle(ytit)
		self.rat.GetYaxis().SetTitleOffset(self.rat.GetYaxis().GetTitleOffset() / factor)
		self.rat.GetYaxis().SetTitleSize  (self.rat.GetYaxis().GetTitleSize()   * factor)
		self.rat.GetYaxis().SetLabelSize  (self.rat.GetYaxis().GetLabelSize()   * factor)
		self.rat.GetYaxis().SetTickLength (0.01)
		self.rat.GetYaxis().CenterTitle()
		self.rat.GetYaxis().SetNdivisions(5)
		self.rat.GetYaxis().SetRangeUser(1-plusminus,1+plusminus)

		self.rat.Draw(option)

		low = self.rat.GetXaxis().GetXmin()
		up  = self.rat.GetXaxis().GetXmax()
		x   = n.array([ low, up ])
		y   = n.array([ 1. , 1. ])
		self.gr = R.TGraph(2,x,y)
		self.gr.SetLineColor(R.kRed)
		self.gr.SetLineStyle(3)
		self.gr.SetLineWidth(2)
		self.gr.Draw('C same')

		self.rat.Draw(option+' same')
		self.rat.SetMarkerColor(R.kBlack)
		self.rat.SetLineColor(R.kBlack)

		self.ratPad.RedrawAxis()

	# makes background transparent
	def makeTransparent(self):
		self.SetFillStyle(4000)
		self.mainPad.SetFillStyle(4000)
		if self.ratioFactor != 0:
			self.ratPad.SetFillStyle(4000)

	# moves exponent away from under CMS
	def moveExponent(self):
		R.TGaxis.SetExponentOffset(-0.08, 0.02, "y")

	# makes an extra axis
	def makeExtraAxis(self, xmin, xmax, Xmin=None, Xmax=None, Ymin=None, Ymax=None, Yoffset=None, Yoffsetscale=0.23, title='', bMarginScale=None):
		self.cd()
		self.mainPad.cd()
		if bMarginScale is None: bMarginScale = 2. if self.ratioFactor == 0. else 2./0.5
		self.scaleMargins(bMarginScale, 'B')
		xaxis = self.firstPlot.GetXaxis()
		if Xmin    is None: Xmin    = xaxis.GetXmin()
		if Xmax    is None: Xmax    = xaxis.GetXmax()
		if Ymin    is None: Ymin    = self.firstPlot.GetMinimum()
		if Ymax    is None: Ymax    = self.firstPlot.GetMaximum()
		if Yoffset is None: Yoffset = (Ymax-Ymin) * Yoffsetscale * (1-self.ratioFactor)
		axis = R.TGaxis(Xmin, Ymin-Yoffset, Xmax, Ymin-Yoffset, xmin, xmax, 510)
		axis.SetLabelFont  (xaxis.GetLabelFont  ())
		axis.SetLabelOffset(xaxis.GetLabelOffset())
		axis.SetLabelSize  (xaxis.GetLabelSize  () if self.ratioFactor == 0. else self.firstPlot.GetYaxis().GetLabelSize())
		axis.SetTitleFont  (xaxis.GetTitleFont  ())
		axis.SetTitleOffset(xaxis.GetTitleOffset())
		axis.SetTitleSize  (xaxis.GetTitleSize  ())
		axis.SetTitle      (title)
		axis.CenterTitle()
		axis.Draw()
		return axis

	# scales pad margins
	# factor is the scale factor
	# edges is a string containing a subset of 'LRTB' controlling which margins
	def scaleMargins(self, factor, edges=''):
		if 'L' in edges:
			self.mainPad.SetLeftMargin  (self.mainPad.GetLeftMargin  () * factor)
		if 'R' in edges:
			self.mainPad.SetRightMargin (self.mainPad.GetRightMargin () * factor)
		if 'T' in edges:
			self.mainPad.SetTopMargin   (self.mainPad.GetTopMargin   () * factor)
		if 'B' in edges:
			self.mainPad.SetBottomMargin(self.mainPad.GetBottomMargin() * factor)

	# draws some text onto the canvas
	# text is the text
	# pos is a positional tuple in NDC
	# align is a string containing two characters, one each of 'bct' and 'lcr' controlling alignment
	# fontcode is a string containing a subset (including empty) of 'bi' controlling bold, italic
	def drawText(self, text='', pos=(0., 0.), align='bl', fontcode='', fontscale=1.):
		latex = R.TLatex()
		AlignDict = {'l' : 1, 'c' : 2, 'r' : 3, 'b' : 1, 't' : 3}
		FontDict = {'' : 4, 'i' : 5, 'b' : 6, 'bi' : 7}
		RAlign = 10 * AlignDict[align[1]] + AlignDict[align[0]]
		RFont = 10 * FontDict[fontcode] + 2
		latex.SetTextAlign(RAlign)
		latex.SetTextFont(RFont)
		latex.SetTextSize(self.fontsize * fontscale)
		latex.DrawLatexNDC(pos[0], pos[1], text)
	
	# draws the lumi text, 'CMS', extra text, and legend 
	def finishCanvas(self, mode='', extrascale=1., drawCMS=True):
		tMargin = float(self.mainPad.GetTopMargin())
		lMargin = float(self.mainPad.GetLeftMargin())
		rMargin = float(self.mainPad.GetRightMargin())

		tOffset = 0.02

		self.cd()
		self.mainPad.cd()

		if mode == '':
			if drawCMS:
				# 'CMS' is approximately 2.75 times wide as tall, so draw extra at 2.75 * charheight to the right of CMS as a fraction of width
				extraOffset = self.fontsize * self.cHeight * (1-self.ratioFactor) * 2.75 / self.cWidth * extrascale
				self.drawText(text='CMS'     , pos=(  lMargin            , 1-tMargin+tOffset), align='bl', fontcode='b'          , fontscale=1.25*extrascale)
				self.drawText(text=self.extra, pos=(  lMargin+extraOffset, 1-tMargin+tOffset), align='bl', fontcode='i'          , fontscale=1.  *extrascale)
				self.drawText(text=self.lumi , pos=(1-rMargin            , 1-tMargin+tOffset), align='br', fontcode=self.fontcode, fontscale=1.  *extrascale)
			else:
				self.drawText(text=self.extra, pos=(  lMargin            , 1-tMargin+tOffset), align='bl', fontcode=self.fontcode, fontscale=1.  *extrascale)
				self.drawText(text=self.lumi , pos=(1-rMargin            , 1-tMargin+tOffset), align='br', fontcode=self.fontcode, fontscale=1.  *extrascale)
		elif mode == 'BOB':
			self.drawText(text=self.lumi , pos=((1-rMargin+lMargin)/2, 1-tMargin+tOffset), align='bc', fontcode=self.fontcode, fontscale=1.5 *extrascale)

		if self.legend is not None:
			self.legend.Draw()
		self.mainPad.RedrawAxis()
	
	# saves canvas as file
	def save(self, name, extList=''):
		if type(extList) == str:
			if extList == '':
				self.SaveAs(name)
			else:
				self.SaveAs(name+extList)
		if type(extList) == list:
			for ext in extList:
				self.SaveAs(name+ext)
	
	# deletes the ROOT TCanvas pointer
	# This is to prevent lousy "RuntimeWarning: Deleting canvas with same name: c" errors
	def deleteCanvas(self):
		R.gROOT.ProcessLine('delete gROOT->FindObject("c");')
