from prody import *

a = parsePDB("a.pdb", subset="ca")
b = parsePDB("b.pdb", subset="ca")

ens = calcAdaptiveANM(a, b, 20, mode=AANM_ALTERNATING)

writeDCD("ens.dcd", ens)
