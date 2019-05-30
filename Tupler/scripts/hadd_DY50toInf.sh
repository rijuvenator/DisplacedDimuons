#!/bin/bash

# hadd on the full DY50toInf sample does not work for me
# (It fails with a basket buffer error of some kind)
# So, this hadds them into six pieces, which can then hadd safely
# In the current configuration, DY50toInf produces 51 files:
# 52 jobs, of which job #6 fails with a file open error

# Option 1: let the six jobs run in parallel
# then do the final line by copy pasting
# It's commented out, otherwise it will run immediately after the background jobs submit

hadd ntuple_DY50toInf_A.root ntuple_DY50toInf_{1..5}.root ntuple_DY50toInf_{7..9}.root &
hadd ntuple_DY50toInf_B.root ntuple_DY50toInf_{10..19}.root                            &
hadd ntuple_DY50toInf_C.root ntuple_DY50toInf_{20..29}.root                            &
hadd ntuple_DY50toInf_D.root ntuple_DY50toInf_{30..39}.root                            &
hadd ntuple_DY50toInf_E.root ntuple_DY50toInf_{40..49}.root                            &
hadd ntuple_DY50toInf_F.root ntuple_DY50toInf_{50..52}.root                            &

# final commands, all in one line
# hadd ntuple_DY50toInf.root ntuple_DY50toInf_{A..F}.root; mv ntuple_DY50toInf.root ~/eos/DisplacedDimuons/; rm ntuple_DY50toInf_{A..F}.root

# Option 2: do everything sequentially, so you can walk away and it will all be done

# hadd ntuple_DY50toInf_A.root ntuple_DY50toInf_{1..5}.root ntuple_DY50toInf_{7..9}.root
# hadd ntuple_DY50toInf_B.root ntuple_DY50toInf_{10..19}.root
# hadd ntuple_DY50toInf_C.root ntuple_DY50toInf_{20..29}.root
# hadd ntuple_DY50toInf_D.root ntuple_DY50toInf_{30..39}.root
# hadd ntuple_DY50toInf_E.root ntuple_DY50toInf_{40..49}.root
# hadd ntuple_DY50toInf_F.root ntuple_DY50toInf_{50..52}.root

# hadd ntuple_DY50toInf.root ntuple_DY50toInf_{A..F}.root
# mv ntuple_DY50toInf.root ~/eos/DisplacedDimuons/
# rm ntuple_DY50toInf_{A..F}.root
