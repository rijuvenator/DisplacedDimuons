# export PATH=$HOME/.local/bin:/cvmfs/cms-bril.cern.ch/brilconda/bin:$PATH
# pip install --user --upgrade brilws
# brilcalc lumi -b "STABLE BEAMS" --normtag /cvmfs/cms-bril.cern.ch/cms-lumi-pog/Normtags/normtag_PHYSICS.json -i /afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/ReReco/Final/Cert_271036-284044_13TeV_ReReco_07Aug2017_Collisions16_JSON.txt -u /fb > brilcalcOutput_Golden.txt
# IMPORTANT: The above is for the Golden JSON! We use the Muon JSON! Use this command instead:
# brilcalc lumi -b "STABLE BEAMS" --normtag /cvmfs/cms-bril.cern.ch/cms-lumi-pog/Normtags/normtag_PHYSICS.json -i /afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/ReReco/Final/Cert_271036-284044_13TeV_ReReco_07Aug2017_Collisions16_JSON_MuonPhys.txt -u /fb > brilcalcOutput_Muon.txt
# then just the run info, replace the colon in run:lumi with run lumi

awk 'BEGIN {x=0} {if ($2 >= 273150 && $2 <= 275376) {x+=$14}} END {print x}' brilcalcOutput_Muon.txt
awk 'BEGIN {x=0} {if ($2 >= 275656 && $2 <= 276283) {x+=$14}} END {print x}' brilcalcOutput_Muon.txt
awk 'BEGIN {x=0} {if ($2 >= 276315 && $2 <= 276811) {x+=$14}} END {print x}' brilcalcOutput_Muon.txt
awk 'BEGIN {x=0} {if ($2 >= 276831 && $2 <= 277420) {x+=$14}} END {print x}' brilcalcOutput_Muon.txt
awk 'BEGIN {x=0} {if ($2 >= 277932 && $2 <= 278808) {x+=$14}} END {print x}' brilcalcOutput_Muon.txt
awk 'BEGIN {x=0} {if ($2 >= 278820 && $2 <= 280385) {x+=$14}} END {print x}' brilcalcOutput_Muon.txt
awk 'BEGIN {x=0} {if ($2 >= 281613 && $2 <= 284044) {x+=$14}} END {print x}' brilcalcOutput_Muon.txt
