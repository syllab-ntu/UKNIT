import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from uknit_bc import UKNITBC
#from calperm import genNibbleMatrix
import multiprocessing
import os, sys, math
import numpy as np
import galois

if __name__ == '__main__':
    uknit_bc = UKNITBC()
    F2 = galois.GF(2)

    T = {}

    for r in range(12):
        for i in range(16):
            #print( '%d' % (i), end = '\n')
            S = uknit_bc.sbox(r, i)
            for x in range(16):
                print( f'{S[x]:x}', end = '' )
            print()

    M2 = F2( uknit_bc.matrix(1), dtype = int)
    
    I = [ 1, 2, 4, 0, 2, 4, 0, 1, 1, 0, 2, 2, 0, 0, 0, 0]

    II = []
    for i in range(16):
        for j in range(4):
            II.append( I[i] >> (3 - j) & 0x1 )

    II = F2( II, dtype = int )

    O = M2.dot( II ).tolist()

    L = []
    for i in range(16):
        L.append( ( O[4 * i] << 3 ) + ( O[4 * i + 1 ] << 2 ) + ( O[4 * i + 2] << 1 ) + O[4 * i + 3]  )
    
    print( L )





    


