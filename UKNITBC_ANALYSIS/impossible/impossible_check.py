import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from uknit_bc import UKNITBC
#from calperm import genNibbleMatrix
import multiprocessing
import shutil
import os, sys

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
    print( X[0:4], '\t', X[16:20], '\t', X[32:36],  '\t', X[48:52] )
    print( X[4:8], '\t', X[20:24], '\t', X[36:40],  '\t', X[52:56] )
    print( X[8:12], '\t', X[24:28], '\t', X[40:44], '\t', X[56:60] )
    print( X[12:16], '\t', X[28:32], '\t', X[44:48], '\t', X[60:64] )

if __name__ == '__main__':
    ##################3
    if shutil.which( 'kissat' ) is None:
        print( 'kissat not found on PATH; install a SAT solver to rerun this historical impossible-differential check.' )
        raise SystemExit(0)

    uknit_bc = UKNITBC()
    res = uknit_bc.impossibleForTruncted( 3, 3 + 7, 61, 0, -1 )
    print( res )
