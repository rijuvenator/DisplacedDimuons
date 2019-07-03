import sys

def safeDivide(a, b):
    return a/b if b != 0. else 1.

headers = ('mH', 'mX', 'cTau', 'sumw_None', 'pass_None', 'sumw_Nom', 'pass_Nom', 'sumw_Low', 'pass_Low', 'sumw_High', 'pass_High')
data = {}
for line in open(sys.argv[1]):
    cols = line.strip('\n').split()
    sp = tuple(map(int, cols[:3]))
    data[sp] = {headers[3+i]:val for i,val in enumerate(map(float, cols[4:6]+cols[7:9]+cols[10:12]+cols[13:15]))}

    print '{:4d} {:3d} {:4d} ::: {:>9.4%} {:>9.4%} {:>9.4%} ::: {:>9.4%} {:>9.4%}'.format(
            sp[0], sp[1], sp[2],
            (1.-safeDivide( safeDivide(data[sp]['pass_Nom' ], data[sp]['sumw_Nom' ]) , safeDivide(data[sp]['pass_None'], data[sp]['sumw_None']) )),
            (1.-safeDivide( safeDivide(data[sp]['pass_Low' ], data[sp]['sumw_Low' ]) , safeDivide(data[sp]['pass_None'], data[sp]['sumw_None']) )),
            (1.-safeDivide( safeDivide(data[sp]['pass_High'], data[sp]['sumw_High']) , safeDivide(data[sp]['pass_None'], data[sp]['sumw_None']) )),
            (1.-safeDivide( safeDivide(data[sp]['pass_Low' ], data[sp]['sumw_Low' ]) , safeDivide(data[sp]['pass_Nom' ], data[sp]['sumw_Nom' ]) )),
            (1.-safeDivide( safeDivide(data[sp]['pass_High'], data[sp]['sumw_High']) , safeDivide(data[sp]['pass_Nom' ], data[sp]['sumw_Nom' ]) )),
    )
