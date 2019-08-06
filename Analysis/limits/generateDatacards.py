import sys
from DisplacedDimuons.Analysis.HistogramGetter import INTEGRATED_LUMINOSITY_2016

##############
#### DATA ####
##############

# transfer factors and cross section
TAU_DRY   = 1.12
ALPHA_DRY = 1./TAU_DRY
TAU_QCD   = 1./3.
ALPHA_QCD = 1./TAU_QCD
SIGMAB    = 1.e-2

# systematics dictionary
# lumi is the luminosity uncertainty
# systS is the systematic uncertainty on expected signal
# statS is the statistical uncertainty on expected signal, as above
# systB-*** is the systematic uncertainty on expected *** background
# statB-*** is the correct way to propagate uncertainty on expected *** background obtained from CR
SYSTEMATICS = {
        'lumi'     : {'mode':'lnN', '2Mu':'1.025', 'DRY':'-'   , 'QCD':'-'   ,           },
        'systS'    : {'mode':'lnN', '2Mu':'1.21' , 'DRY':'-'   , 'QCD':'-'   ,           },
        'statS'    : {'mode':'lnN', '2Mu':''     , 'DRY':'-'   , 'QCD':'-'   ,           },

        'systB-DRY': {'mode':'lnN', '2Mu':'-'    , 'DRY':'1.25', 'QCD':'-'   ,           },
        'systB-QCD': {'mode':'lnN', '2Mu':'-'    , 'DRY':'-'   , 'QCD':'1.25',           },
        'statB-DRY': {'mode':'gmN', '2Mu':'-'    , 'DRY':''    , 'QCD':'-'   , 'nOff': ''},
        'statB-QCD': {'mode':'gmN', '2Mu':'-'    , 'DRY':'-'   , 'QCD':''    , 'nOff': ''},
}
SYSTEMATICS['statB-DRY']['DRY'] = str(ALPHA_DRY)
SYSTEMATICS['statB-QCD']['QCD'] = str(ALPHA_QCD)

# needs to be a text file with four lines in the format '<MASS> <CRDRY> <CRQCD> <OBS>'
DATACOUNTS = {m:{'CRDY':0, 'CRQCD':0, 'OBS':0} for m in ('20', '50', '150', '350')}
f = open('text/realDataCounts.txt')
for line in f:
    cols = line.strip('\n').split()
    DATACOUNTS[cols[0]]['CRDRY'] = int(cols[1])
    DATACOUNTS[cols[0]]['CRQCD'] = int(cols[2])
    DATACOUNTS[cols[0]]['OBS'  ] = int(cols[3])
f.close()

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
    EXP_DRY = DATACOUNTS[job['mX']]['CRDRY']*ALPHA_DRY
    EXP_QCD = DATACOUNTS[job['mX']]['CRQCD']*ALPHA_QCD

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

    SYSTEMATICS['statB-DRY']['nOff'] = str(DATACOUNTS[job['mX']]['CRDRY'])
    SYSTEMATICS['statB-QCD']['nOff'] = str(DATACOUNTS[job['mX']]['CRQCD'])

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
