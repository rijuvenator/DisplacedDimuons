import re
import ROOT as R

Patterns = {
    'HTo2XTo4Mu'   : re.compile(r'(.*)_HTo2XTo4Mu_(\d{3,4})_(\d{2,3})_(\d{1,4})'),
    'HTo2XTo2Mu2J' : re.compile(r'(.*)_HTo2XTo2Mu2J_(\d{3,4})_(\d{2,3})_(\d{1,4})')
}
for sample in (
    'DY10to50'  ,
    'WJets'     ,
    'WW'        ,
    'WZ'        ,
    'ZZ'        ,
    'tW'        ,
    'tbarW'     ,
    'DY50toInf' ,
    'ttbar'     ,
    ):
    Patterns[sample] = re.compile(r'(.*)_'+sample)

# get all histograms
def getHistograms(FILE):
    f = R.TFile.Open(FILE)
    HISTS = {}
    for hkey in [tkey.GetName() for tkey in f.GetListOfKeys()]:
        if 'HTo2X' in hkey:
            if '4Mu' in hkey:
                # hkey has the form KEY_HTo2XTo4Mu_mH_mX_cTau
                matches = Patterns['HTo2XTo4Mu'].match(hkey)
                fs = '4Mu'
            elif '2Mu2J' in hkey:
                # hkey has the form KEY_HTo2XTo2Mu2J_mH_mX_cTau
                matches = Patterns['HTo2XTo2Mu2J'].match(hkey)
                fs = '2Mu2J'
            key = matches.group(1)
            sp = tuple(map(int, matches.group(2, 3, 4)))
            if (fs, sp) not in HISTS:
                HISTS[(fs, sp)] = {}
            HISTS[(fs, sp)][key] = f.Get(hkey)
            HISTS[(fs, sp)][key].SetDirectory(0)
        else:
            # hkey has the form KEY_SAMPLE
            for sample, pattern in Patterns.iteritems():
                matches = pattern.match(hkey)
                if matches:
                    key = matches.group(1)
                    if sample not in HISTS:
                        HISTS[sample] = {}
                    HISTS[sample][key] = f.Get(hkey)
                    HISTS[sample][key].SetDirectory(0)
    return HISTS

PLOTCONFIG = {}
PlotData = (
    ('HTo2XTo4Mu'  , 'H#rightarrow2X#rightarrow4#mu'  , R.kBlue),
    ('HTo2XTo2Mu2J', 'H#rightarrow2X#rightarrow2#mu2j', R.kBlue),
    ('DY10to50'    , 'Drell-Yan M(10, 50)'            , 210    ),
    ('DY50toInf'   , 'Drell-Yan M(50, #infty)'        , 209    ),
    ('WJets'       , 'W+Jets'                         , 52     ),
    ('WW'          , 'WW'                             , 208    ),
    ('WZ'          , 'WZ'                             , 98     ),
    ('ZZ'          , 'ZZ'                             , 94     ),
    ('tW'          , 'tW'                             , 66     ),
    ('tbarW'       , '#bar{t}W'                       , 63     ),
    ('ttbar'       , 't#bar{t}'                       , 4      ),
)
for name, latex, color in PlotData:
    PLOTCONFIG[name] = {'LATEX':latex, 'COLOR':color}
