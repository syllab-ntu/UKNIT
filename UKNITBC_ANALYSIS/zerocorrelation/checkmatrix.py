import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from uknit_bc import UKNITBC
import numpy as np
import galois

if __name__ == '__main__':
    uknit_bc = UKNITBC()
    for i in range(0, 11):
        M0 = uknit_bc.matrix(i)
        F2 = galois.GF(2)
        M0 = F2( M0, dtype = int )
        print( M0.dot( M0 ) )

    for i in range(0, 12):
        for j in range(16):
            S = uknit_bc.sbox(i, j)

            for x in range(16):
                print( x == S [ S[x] ] )
