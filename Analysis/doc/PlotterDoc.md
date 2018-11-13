# Documentation for `Plotter.py`

Last updated: **20 September 2018**

Documention for my Plotter classes. Should be self-explanatory from the comments in the code for the most part, but this is a handy reference.

The first method listed is always the constructor. Any arguments with an = are optional (defaults usually given); any without are mandatory.

The Plotter module contains the Plot, Legend, and Canvas classes.

It is intended to be a general purpose plot and canvas handling module, incorporating a flexible TDRStyle, convenient wrappers and automation.

  * [Plot](#plot)
    * [Class Members](#plotmembers)
    * [Class Methods](#plotmethods)
  * [Legend](#legend)
    * [Class Members](#legendmembers)
    * [Class Methods](#legendmethods)
  * [Canvas](#canvas)
    * [Class Members](#canvasmembers)
    * [Class Methods](#canvasmethods)
  * [How to Use the _Plotter_ Module](#howto)
  * [Module Functions](#modulefunctions)
    * [setStyle](#setstyle)
    * [Object SHIFT, SCALE, and MOVE](#shiftmove)

<a name="plot"></a>
## Plot
<a name="plotmembers"></a>
### Class Members

**plot** is the ROOT plot object to be drawn.  
**legName** is the legend display name.  
**legType** is a string containing a subset of `felp` defining the legend symbol.  
**option** is the draw option passed to the `Draw()` function. No `same` or `A` required.

* _TObject_ **plot**
* _string_  **legName**
* _string_  **legType**
* _string_  **option**

<a name="plotmethods"></a>
### Class Methods
**factor** is a multiplicative scale factor.  
**axes** is a string containing a possibly empty subset of `XYZ`, default `XY`. All axes must exist.
**which** is a string containing a possibly empty subset of `LMF`, default `LM`.

**scaleTitles** and **scaleLabels** scale the size of the axis titles and labels, respectively.  
**scaleTitleOffsets** scales the distance between the axis title and the axis.  
**setTitles** sets axis titles. The function expects strings for each of its arguments.

```python
* Plot                   (plot, legName='hist', legType='felp', option='')
* Plot.scaleTitles       (factor, axes='XY')
* Plot.scaleLabels       (factor, axes='XY')
* Plot.scaleTitleOffsets (factor, axes='XY')
* Plot.setTitles         (X=None, Y=None, Z=None)
* Plot.setColor          (color, which='LF')
```


<a name="legend"></a>
## Legend(TLegend)
<a name="legendmembers"></a>
### Class Members

Inherits from **TLegend**.  
**lines** is the number of lines in the legend. This is stored automatically.  
**corner** is a pos string (`tl`, `tr`, `bl`, `br`) defining which corner the legend will be drawn. 

* _TLegend_ **self**
* _int_     **lines**
* _string_  **corner**

<a name="legendmethods"></a>
### Class Methods

All units are in "user coordinates", i.e. fractions of the plot height and width.  
**X1, X2, Y1, Y2** define the legend box. Used to construct the parent TLegend.  
**Plot** is a Plot object (see above)  
**X, Y** move the legend in the X or Y directions in user units.  
**L, R, T, B** move just the legend box edges in user units.  
**scale** automatically spaces out the legend lines more or less.

**addLegendEntry** adds a reference to a Plot.  
**moveLegend** moves the entire legend in the X or Y directions.  
**moveEdges** moves just the legend edges in + or – directions.  
**resizeHeight** calculates an optimal height given the number of legend lines.

```python
* Legend                (X1, Y1, X2, Y2, corner)
* Legend.addLegendEntry (Plot)
* Legend.moveLegend     (X=0., Y=0.)
* Legend.moveEdges      (L=0., R=0., T=0., B=0.)
* Legend.resizeHeight   (scale=1.)
```

<a name="canvas"></a>
## Canvas(TCanvas)
<a name="canvasmembers"></a>
### Class Members

Inherits from **TCanvas**.  

#### External class members
* _TCanvas_ **self**
* _int_     **cWidth**
* _int_     **cHeight**
* _string_  **fontcode**
* _float_   **fontscale**
* _bool_    **logy**
* _string_  **lumi**
* _string_  **extra**
* _float_   **ratioFactor**

#### Internal class members
- _int_     **font**
- _float_   **fontsize**
- _TPad_    **mainPad**
- _Legend_  **legend**
- _bool_    **axesDrawn**
- _TObject_ **firstPlot**
- _list_    **plotList**
- _TPad_    **ratPad**
- _Plot_    **rat**
- _TGraph_  **gr**
- _dict_    **margins**

<a name="canvasmethods"></a>
### Class Methods
I've omitted some uninteresting defaults from the constructor doc.

**pos**      is a 2 character string: `tb`  + `rl`  
**align**    is a 2 character string: `bct` + `lcr`  
**fontcode** is a string containing a possibly empty subset of `bi`  
**edges**    is a string containing a possibly empty subset of `LRTB`  

```python
  * Canvas                 (lumi=, extra=, logy=False, ratioFactor=0, cWidth=800, cHeight=600, fontcode=, fontscale=)
  * Canvas.addMainPlot     (Plot, addToPlotList=True, addS=False)
  * Canvas.makeLegend      (lWidth=0.125, pos='tr', fontscale=1., autoOrder=True)
  * Canvas.setMaximum      (recompute=False, scale=1.05)
  * Canvas.setMinimum      (recompute=False, scale=1.)
  * Canvas.addLegendEntry  (Plot)
  * Canvas.setFitBoxStyle  (owner, lWidth=0.3, lHeight=0.15, pos='tl', lOffset=0.05, fontscale=0.75)
  * Canvas.makeRatioPlot   (topHist, bottomHist, plusminus=0.5, option='', ytit='Data/MC', xtit='', drawLine=True)
  * Canvas.makeTransparent ()
  * Canvas.moveExponent    ()
  * Canvas.makeExtraAxis   (xmin, xmax, Xmin=, Xmax=, Ymin=, Ymax=, Yoffset=, Yoffsetscale=0.23, title='', bMarginScale=) [returns axis]
  * Canvas.scaleMargins    (factor, edges='')
  * Canvas.drawText        (text='', pos=(0., 0.), align='bl', fontcode='', fontscale=1., NDC=True)
  * Canvas.makeStatsBox    (plot, color=1)
  * Canvas.finishCanvas    ()
  * Canvas.save            (name, extList='')
  * Canvas.deleteCanvas    ()
  * Canvas.cleanup         (filename)
```

<a name="howto"></a>
## HOW TO USE THE PLOTTER MODULE

### 1. Make Plots  

```python
Plotter.Plot(Object, legName, legType='felp', option)
```  
**binding decisions**: none

### 2. Make Canvas

```python
Plotter.Canvas(lumi=, extra='Internal', logy=False, ratioFactor=0, cWidth=800, cHeight=600, fontcode=''(bi), fontscale=1)
```
**binding decisions**: cWidth, cHeight, ratioFactor

### 3. Add Plots

```python
Plotter.Canvas.addMainPlot(Plot, addToPlotList=True)
```
**binding decisions**: draw order

### 4. Make Legend

```python
Plotter.Canvas.makeLegend    (lWidth=0.125, pos='tr', fontscale=1., autoOrder=True)
Plotter.Canvas.addLegendEntry(Plot)
```
**binding decisions**: legend order (automation)

**Note**: If making an extra axis and legend position is to be automatically calculated, make the axis and THEN make the legend.

### 5. Add additional structures

```python
Plotter.Canvas.makeRatioPlot(topHist, bottomHist, plusminus=0.5, option='', ytit='Data/MC', xtit='')
```
**binding decisions**: topHist, bottomHist

```python
Plotter.Canvas.makeExtraAxis(xmin, xmax, Xmin=, Xmax=, Ymin=, Ymax=, Yoffset=, Yoffsetscale=0.23, title='', bMarginScale=)
```
**binding decisions**: everything

**Note**: changes pad margins

### 6. Apply cosmetics
Anything involving sizes, positions, decorations, marker, line, and fill styles, etc.

```python
Plotter.Canvas.makeTransparent()
Plotter.Canvas.moveExponent   ()
Plotter.Canvas.scaleMargins   (factor, edges=''(LRTB))
Plotter.Canvas.drawText       (text, pos=(0., 0.), align='bl', fontcode='', fontscale=1.)
Plotter.Canvas.setFitBoxStyle (owner, lWidth=0.3, lHeight=0.15, pos='tl', lOffset=0.05, fontscale=0.75)
```

### 7. Finish, Save, and Delete

```python
Plotter.Canvas.finishCanvas()
Plotter.Canvas.save        (name, extList='')
Plotter.Canvas.deleteCanvas()
```

or

```python
Plotter.Canvas.cleanup(filename)
```

<a name="modulefunctions"></a>
## Module Functions
<a name="setstyle"></a>
### `setStyle`
The `setStyle` functions are based on TDRStyle and are fully compliant with it. The global version is run once, on module import. The not-global version takes some arguments that are specific to the canvas being drawn, and adjusts things like margins based on the canvas size.

<a name="shiftmove"></a>
### Object `SHIFT`, `SCALE`, and `MOVE`
I often find myself writing many lines of the form

```python
h.GetXaxis().SetTitleOffset(h.GetXaxis().GetTitleOffset() * 1.1)
h.GetYaxis().SetTitleOffset(h.GetYaxis().GetTitleOffset() * 1.1)
```
and similar functions for shifting, scaling, and moving things around. These are a pain to write and maintain and are error prone (forget to change one `X` or one `1` and it's wrong). Python makes it easy to write these lines of code in a structured, programmatic way. So there are now a group of general purpose functions that perform these functions with a friendly signature. For example the above can now be replaced with

```python
SCALE(h, 'TitleOffset', 1.1, Axes='XY')
```

As another example,

```python
legend.SetX1(legend.GetX1() + 0.2)
legend.SetX2(legend.GetX2() + 0.2)
legend.SetY1(legend.GetY1() + 0.1)
legend.SetY2(legend.GetY2() + 0.1)
```
can now be replaced with

```python
MOVE_OBJECT(legend, X=0.2, Y=0.1)
```
All the classes that previously had wrappers for these types of graphical changes (e.g. Plot, Legend) have been updated to use these functions when appropriate. Now you can write fewer lines of code involving the `SetAttr(GetAttr())` idiom.
