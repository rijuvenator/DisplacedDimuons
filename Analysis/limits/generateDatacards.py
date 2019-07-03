import sys
from DisplacedDimuons.Analysis.HistogramGetter import INTEGRATED_LUMINOSITY_2016

headers = ['mH', 'mX', 'cTau', 'op', 'factor', 'sumw', 'sig']
data = []
f = open('text/datacardRawInput.txt')
for line in f:
    cols = line.strip('\n').split()
    data.append(dict(zip(headers, cols[:3] + cols[4:6] + cols[7:9])))
f.close()

for job in data:

    ###########################
    ##### DATACARD VALUES #####
    ###########################

    OBS = 3

    PROCESSES = ('2Mu', 'BG')

    RATES = {
        '2Mu' : str(float(job['sig'])/float(job['sumw'])*INTEGRATED_LUMINOSITY_2016*1.e-2),
        'BG'  : '3.00',
    }

    SYSTEMATICS = {
#       'lumi' : {'mode':'lnN', '2Mu':'1.025', 'BG':'1.025'              },
        'systS': {'mode':'lnN', '2Mu':'1.2'  , 'BG':'-'                  },
        'systB': {'mode':'lnN', '2Mu':'-'    , 'BG':'1.2'                },
        'stat' : {'mode':'gmN', '2Mu':'-'    , 'BG':'1.00' , 'nOff':'3'  },
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
    maxNOff = 2

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
