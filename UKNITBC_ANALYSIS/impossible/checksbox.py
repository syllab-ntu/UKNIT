import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from uknit_bc import UKNITBC
#from calperm import genNibbleMatrix
import multiprocessing
import os, sys
import galois
import numpy as np

def GF16to2( x ):
    xx = [0] * 64
    for i in range(64):
        xx[i] = x[i // 4] >> ( 3 - i % 4 ) & 0x1
    return xx

def GF2to16( x ):
    xx = [0] * 16
    for i in range(64):
        xx[i // 4] ^= x[i] << ( 3 - i % 4 )
    return xx

def printState( X ):
    print( X[0], '\t', X[4], '\t', X[8],  '\t', X[12] )
    print( X[1], '\t', X[5], '\t', X[9],  '\t', X[13] )
    print( X[2], '\t', X[6], '\t', X[10], '\t', X[14] )
    print( X[3], '\t', X[7], '\t', X[11], '\t', X[15] )

if __name__ == '__main__':
    ##################3
    uknit_bc = UKNITBC()
    #!!!!!!!!!!!!!!!!
    CIPHER = uknit_bc

    F2 = galois.GF(2)

    MM4 = np.linalg.inv( F2( uknit_bc.matrix(10), dtype = int ) )
    #MM4 = F2( uknit_bc.matrix(1), dtype = int )
    #MM4 = uknit_bc.matrix(1)

    X3 = [
        0x0, 0x0, 0x0, 0xf, 
        0x0, 0x0, 0xf, 0x0, 
        0x0, 0xf, 0x0, 0x0,
        0xf, 0x0, 0x0, 0x0,
           ]

    XB3 = F2( GF16to2( X3 ), dtype = int )

    #Y = MM4.dot( XB3 )

    #Y2 = GF2to16( Y.tolist() )

    #print( Y2 )

    #printState( Y2 )

    YB2 = [ 0 for i in range(64) ]
    for i in range(64):
        if XB3[i] == 1:
            for j in range(64):
                if MM4[i][j] == 1:
                    YB2[j] = 1

    Y2 = GF2to16( YB2 )
    printState( Y2 )