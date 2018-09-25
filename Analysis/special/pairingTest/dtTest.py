import pandas
import sklearn
from sklearn import tree
from sklearn.tree import export_graphviz

#data = pandas.read_csv('training.csv', sep=',')
#clf = sklearn.tree.DecisionTreeClassifier(min_samples_leaf=20)
#clf.fit(data[['dR','chi2','sigLxy']], data['class'])
#tree.export_graphviz(clf, out_file='tree.dot', feature_names=['dR','chi2','sigLxy'], class_names=['bg', 'signal'])

results = {'signal' : [0, 0, 0], 'background' : [0, 0, 0]}
f = open('training.csv')
for line in f:
    if 'class' in line: continue
    cols = line.strip('\n').split(',')
    cat, dR, chi2, sigLxy = [int(cols[0])] + [float(i) for i in cols[1:]]
    if cat == 0:
        results['background'][0] += 1
    else:
        results['signal'    ][0] += 1
    if dR < .4638 and dR > .1463 and sigLxy < 19.6:
        if cat == 1:
            results['signal'    ][1] += 1
        else:
            results['signal'    ][2] += 1
            print cat, dR, chi2, sigLxy
    else:
        if cat == 0:
            results['background'][1] += 1
        else:
            results['background'][2] += 1
            print cat, dR, chi2, sigLxy

print results

