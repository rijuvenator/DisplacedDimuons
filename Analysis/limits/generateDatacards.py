import sys
from DisplacedDimuons.Analysis.HistogramGetter import INTEGRATED_LUMINOSITY_2016

##############
#### DATA ####
##############

# arbitrary cross section, and masses
SIGMAB    = 1.e-2
MASSES = ('20', '50', '150', '350')

# needs to be a text file with four (mass) lines in the format '<MASS> <CR-DRY> <TF-DRY> <UNC-DRY> <CR-QCD> <TF-QCD> <UNC-QCD> <OBS>'
HEADERS = ('MASS', 'CR-DRY', 'TF-DRY', 'UNC-DRY', 'CR-QCD', 'TF-QCD', 'UNC-QCD', 'OBS')
DATACOUNTS = {m:{h:0 for h in HEADERS[1:]} for m in MASSES}
f = open('text/realDataCounts.txt')
for line in f:
    cols = line.strip('\n').split()
    vals = dict(zip(HEADERS, tuple(cols)))
    for h in HEADERS[1:]:
        DATACOUNTS[vals['MASS']][h] = float(vals[h]) if 'CR-' not in h and 'OBS' != h else int(vals[h])
f.close()

TAU   = {'DRY' : {}, 'QCD' : {}}
ALPHA = {'DRY' : {}, 'QCD' : {}}
for m in MASSES:
    TAU  ['DRY'][m] = {'val':   DATACOUNTS[m]['TF-DRY'], 'unc':DATACOUNTS[m]['UNC-DRY']}
    TAU  ['QCD'][m] = {'val':1./DATACOUNTS[m]['TF-QCD'], 'unc':DATACOUNTS[m]['UNC-QCD']} # I copy the QCD value as the reciprocal of the right value

    ALPHA['DRY'][m] = 1./TAU['DRY'][m]['val']
    ALPHA['QCD'][m] = 1./TAU['QCD'][m]['val']

# systematics dictionary
# lumi is the luminosity uncertainty, fixed
# systS is the systematic uncertainty on expected signal, fixed
# statS is the statistical uncertainty on expected signal, computed from weights in the loop below
# systB-*** is the systematic uncertainty on expected *** background, different for each mass and TF
# statB-*** is the correct way to propagate uncertainty on expected *** background obtained from CR, different for each CR
SYSTEMATICS = {
        'lumi'     : {'mode':'lnN', '2Mu':'1.025', 'DRY':'-'   , 'QCD':'-'   ,           },
        'systS'    : {'mode':'lnN', '2Mu':'1.20' , 'DRY':'-'   , 'QCD':'-'   ,           },
        'statS'    : {'mode':'lnN', '2Mu':''     , 'DRY':'-'   , 'QCD':'-'   ,           },

        'systB-DRY': {'mode':'lnN', '2Mu':'-'    , 'DRY':''    , 'QCD':'-'   ,           },
        'systB-QCD': {'mode':'lnN', '2Mu':'-'    , 'DRY':'-'   , 'QCD':''    ,           },
        'statB-DRY': {'mode':'gmN', '2Mu':'-'    , 'DRY':''    , 'QCD':'-'   , 'nOff': ''},
        'statB-QCD': {'mode':'gmN', '2Mu':'-'    , 'DRY':'-'   , 'QCD':''    , 'nOff': ''},
}

# output of getCounts
headers = ['mH', 'mX', 'cTau', 'op', 'factor', 'nEvents', 'sumW', 'sig', 'sig2']
data = []
f = open('text/datacardRawInput.txt')
for line in f:
    cols = line.strip('\n').split()
    data.append(dict(zip(headers, cols[:3] + cols[4:6] + cols[7:11])))
f.close()

skippedJobs = 0

for job in data:

    ###########################
    ##### DATACARD VALUES #####
    ###########################

    OBS     = DATACOUNTS[job['mX']]['OBS']
    EXP_DRY = DATACOUNTS[job['mX']]['CR-DRY']*ALPHA['DRY'][job['mX']]
    EXP_QCD = DATACOUNTS[job['mX']]['CR-QCD']*ALPHA['QCD'][job['mX']]

    PROCESSES = ('2Mu', 'DRY', 'QCD')

    RATES = {
        '2Mu' : str(float(job['sig'])/float(job['sumW'])*INTEGRATED_LUMINOSITY_2016*SIGMAB),
        'DRY' : '{:.2f}'.format(EXP_DRY),
        'QCD' : '{:.2f}'.format(EXP_QCD),
    }

    # first make sure there are no jobs with zero expected signal
    if float(RATES['2Mu']) < 1.e-5:
        print 'Skipping job : {} {} {} :: {} {} ... due to sig. eff. = 0'    .format(*[job[k] for k in headers[:5]])
        skippedJobs += 1
        continue

    # now compute the statistical uncertainty on the signal efficiency from weights
    # if job['sig2'] < 1.e-6, I ran out of digits, so assign it 1.e-6. then,
    # freshman error propagation, ignoring the uncertainty on sumW (which is probably ~0.5%)
    # means just sqrt(sum(w^2))/sum(w)
    # then skip any that are more than 50% uncertainty

    sumW2 = float(job['sig2'])
    if sumW2 < 1.e-6: sumW2 = 1.e-6

    STATSIG = '{:.4f}'.format(1.+(sumW2**0.5)/float(job['sig']))

    if (float(STATSIG)-1.) > .5:
        print 'Skipping job : {} {} {} :: {} {} ... due to stat. unc. on sig.'.format(*[job[k] for k in headers[:5]])
        skippedJobs += 1
        continue

    # fill missing values in systematics dictionary

    SYSTEMATICS['statS']['2Mu' ] = STATSIG

    for BG in ('DRY', 'QCD'):
        SYSTEMATICS['systB-'+BG][BG    ] = str(1.+        TAU[BG][job['mX']]['unc']   )
        SYSTEMATICS['statB-'+BG]['nOff'] = str(    DATACOUNTS    [job['mX']]['CR-'+BG])
        SYSTEMATICS['statB-'+BG][BG    ] = str(         ALPHA[BG][job['mX']]          )

    ###########################
    ##### DATACARD FORMAT #####
    ###########################

    datacard = '''#
imax {imax}
jmax {jmax}
kmax {kmax}
-----------------
bin         bin1
observation {obs}
-----------------
{binnKey} {extra}{binLine}
{procKey} {extra}{procLine1}
{procKey} {extra}{procLine2}
{rateKey} {extra}{rateLine}
-----------------{SYST}
    '''

    ###############################
    ##### STRINGS AND FORMATS #####
    ###############################

    # minimum 4 for 'bin1', the vals for the bin lines
    BinValWidth = max([4] + map(len, PROCESSES) + map(len, RATES.values()) + map(len, [dic[key] for dic in SYSTEMATICS.values() for key in dic]))

    # key val ...
    BinValString = ' '.join(['{{:{}s}}'.format(BinValWidth)]*len(PROCESSES))

    # minimum 8 for 'process ', the keys for the bin and syst lines
    KeyWidth = max([8] + map(len, SYSTEMATICS.keys()))
    KeyString = '{:<'+str(KeyWidth)+'s}'

    SystValString = KeyString + ' {:3s} {:s} ' + BinValString

    # extra spaces accounting for the mode and nOff fields
    extra = '     '
    maxNOff = 1

    # name mode (nOff) unc ...
    FormattedSystString = ''
    for key, dic in SYSTEMATICS.iteritems():
        if 'nOff' in dic:
            maxNOff = max(maxNOff, len(dic['nOff']))
        FormattedSystString += '\n' + SystValString.format(
            key,
            dic['mode'],
            ' ' if dic['mode'] != 'gmN' else str(dic['nOff']),
            *[dic[p] for p in PROCESSES]
        )

    extra += ' '*maxNOff

    ##################
    ##### OUTPUT #####
    ##################

    out = datacard.format(
            imax      = 1,
            jmax      = len(PROCESSES)-1,
            kmax      = len(SYSTEMATICS),

            obs       = OBS,

            binnKey   = KeyString.format('bin'),
            procKey   = KeyString.format('process'),
            rateKey   = KeyString.format('rate'),

            binLine   = BinValString.format(*(['bin1']*len(PROCESSES))      ),
            procLine1 = BinValString.format(*PROCESSES                      ),
            procLine2 = BinValString.format(*map(str, range(len(PROCESSES)))),
            rateLine  = BinValString.format(*[RATES[p] for p in PROCESSES]  ),

            SYST      = FormattedSystString,

            extra     = extra,
    )

    #########################
    ##### WRITE TO FILE #####
    #########################

    open('cards/card_{}_{}_{}_{}_{}.txt'.format(*[job[x] for x in headers[:5]]), 'w').write(out)

print 'Total skipped jobs: {}'.format(skippedJobs)
