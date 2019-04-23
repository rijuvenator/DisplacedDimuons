import sys

f = open(sys.argv[1])

for line in f:
    cols = line.strip('\n').split()
    LxySig, chi2, cosAlpha, d0Sig1, d0Sig2, deltaR1, deltaR2 = map(float, cols[10:11]+cols[12:14]+cols[15:19])

    fpte1, fpte2, phi1, phi2, rphi1, rphi2 = map(float, cols[20:])

    # for Bob
    #if LxySig > 5. and d0Sig1 > 3. and d0Sig2 > 3. and cosAlpha > -.8 and chi2 < 20.:
    #    print line.strip('\n')

    # for Slava
    #if LxySig > 5 and chi2 < 20 and cosAlpha < -0.9:
    #    print line.strip('\n')

    # cuts
    #if LxySig > 5 and chi2 < 20 and cosAlpha > -0.8 and d0Sig1 > 3. and d0Sig2 > 3:
    #    print line.strip('\n')

    #if cosAlpha > -0.9:
    #    print line.strip('\n')
