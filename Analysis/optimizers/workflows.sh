# rehadd

rehaddAll.py --mode split --tags HaikuPlots_IDPHI --dirs tmp mcbg --samples data --noPlots --noMove

# signal -> one file

for i in _Trig_HTo2XTo2Mu2J
do
    rehadd HaikuPlots${i}
    mv HaikuPlots${i}_*.root tmp/
done

# data -> one file

for i in "_IDPHI"
do
    hadd HaikuPlots${i}_DATA.root HaikuPlots${i}_DoubleMuon*.root
    mv HaikuPlots${i}_DoubleMuon*.root tmp/
done

