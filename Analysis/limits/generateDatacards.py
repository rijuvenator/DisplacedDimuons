import sys
from DisplacedDimuons.Analysis.HistogramGetter import INTEGRATED_LUMINOSITY_2016

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

    OBS = 3

    PROCESSES = ('2Mu', 'BG')

    RATES = {
        '2Mu' : str(float(job['sig'])/float(job['sumW'])*INTEGRATED_LUMINOSITY_2016*1.e-2),
        'BG'  : '3.00',
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

    # systematics dictionary
    # lumi is the luminosity uncertainty
    # systS is the systematic uncertainty on expected signal
    # systB is the systematic uncertainty on expected background
    # statS is the statistical uncertainty on expected signal, as above
    # statB is the correct way to propagate uncertainty on nBG-Exp obtained from CR

    SYSTEMATICS = {
        'lumi' : {'mode':'lnN', '2Mu':'1.025' , 'BG':'-'                 },
        'systS': {'mode':'lnN', '2Mu':'1.2'   , 'BG':'-'                 },
        'systB': {'mode':'lnN', '2Mu':'-'     , 'BG':'1.2'               },
        'statS': {'mode':'lnN', '2Mu':STATSIG , 'BG':'-'                 },
        'statB': {'mode':'gmN', '2Mu':'-'     , 'BG':'1.0' , 'nOff':'3'  },
    }

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
