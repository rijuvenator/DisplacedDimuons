import ROOT as R

f = R.TFile.Open('roots/PoorMansShapeAnalysis.root')
h = f.Get('h')

data = [
    (18.5126 , 0.2575),
    ( 6.7612 , 0.1309),
    (14.225  , 0.1123),
    ( 6.7264 , 0.002 ),
    (76.6759 , 0.0714),
    ( 8.9318 , 0.2053),
    ( 8.8142 , 0.3784),
    ( 8.8979 , 0.3114),
    (10.0141 , 0.599 ),
    ( 6.9548 , 0.6037),
    (14.292  , 0.2676),
    (56.9093 , 0.0764),
    (87.703  , 0.0468),
]

data = [{'LxySig':x, 'deltaPhi':y} for x, y in data]

yaxis = h.GetYaxis()
xaxis = h.GetXaxis()

BIN_I1 = xaxis.FindBin(   R.TMath.Pi()/4. + .2)
BIN_I2 = xaxis.FindBin(   R.TMath.Pi()/2. + .2)
BIN_CR = xaxis.FindBin(3.*R.TMath.Pi()/4. + .2)

def safeDivide(a, b):
    try:
        return float(a)/float(b)
    except:
        return 0.

for event in data:
    LxySigBin = yaxis.FindBin(event['LxySig'])

    BIN_SR = xaxis.FindBin(event['deltaPhi'])

    C_SR = int(h.GetBinContent(h.GetBin(BIN_SR, LxySigBin)))
    #C_SR = int(h.Integral(1, BIN_I1-1, LxySigBin, LxySigBin))

    C_I1 = h.GetBinContent(h.GetBin(BIN_I1, LxySigBin))/(BIN_I1-1)
    C_I2 = h.GetBinContent(h.GetBin(BIN_I2, LxySigBin))/(BIN_I1-1)
    C_CR = h.GetBinContent(h.GetBin(BIN_CR, LxySigBin))/(BIN_I1-1)
    #C_I1 = int(h.GetBinContent(h.GetBin(BIN_I1, LxySigBin)))
    #C_I2 = int(h.GetBinContent(h.GetBin(BIN_I2, LxySigBin)))
    #C_CR = int(h.GetBinContent(h.GetBin(BIN_CR, LxySigBin)))

    vals = []
    for i in (C_I1, C_I2, C_CR):
        vals.append(safeDivide(C_SR, i))
        vals.append(safeDivide(i, C_SR))

    #print '{:7.4f} {:<6.4} ~~~ SR mini bin {:5d} --> I1 : {:7.1f} ::: I2 : {:7.1f} ::: CR : {:7.1f} ~~~ SR/R # R/SR : I1 : {:7.4f} # {:7.4f} ::: I2 : {:7.4f} # {:7.4f} ::: CR : {:7.4f} # {:7.4f}'.format(
    #        event['LxySig'],
    #        event['deltaPhi'],
    #        C_SR, C_I1, C_I2, C_CR,
    #        *vals
    #)

    fstring = '{:2.0f} <= LxySig <= {:2.0f} ::: {:7.4f} {:<6.4} ~~~ '
    vals = []
    for i in xrange(1, xaxis.GetNbins()+1):
        fstring += '{:5.0f} '
        vals.append(h.GetBinContent(h.GetBin(i, LxySigBin)))

    print fstring.format(yaxis.GetBinLowEdge(LxySigBin), yaxis.GetBinUpEdge(LxySigBin), event['LxySig'], event['deltaPhi'], *vals)
