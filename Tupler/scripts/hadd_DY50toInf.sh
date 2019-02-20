#!/bin/bash

# hadd on the full DY50toInf sample does not work for me
# (It fails with a basket buffer error of some kind)
# So, this hadds them into six pieces, which can then hadd safely
# In the current configuration, DY50toInf produces 51 files:
# 52 jobs, of which job #6 fails with a file open error

# Comment out the &'s if you want them to run in parallel
# but then do be sure to uncomment out the three last lines, since they will
# otherwise run immediately after the background jobs submit

hadd ntuple_DY50toInf_A.root ntuple_DY50toInf_{1..5}.root ntuple_DY50toInf_{7..9}.root #&
hadd ntuple_DY50toInf_B.root ntuple_DY50toInf_{10..19}.root                            #&
hadd ntuple_DY50toInf_C.root ntuple_DY50toInf_{20..29}.root                            #&
hadd ntuple_DY50toInf_D.root ntuple_DY50toInf_{30..39}.root                            #&
hadd ntuple_DY50toInf_E.root ntuple_DY50toInf_{40..49}.root                            #&
hadd ntuple_DY50toInf_F.root ntuple_DY50toInf_{50..52}.root                            #&

hadd ntuple_DY50toInf.root ntuple_DY50toInf_{A..F}.root
mv ntuple_DY50toInf.root ~/eos/DisplacedDimuons/
rm ntuple_DY50toInf_{A..F}.root
