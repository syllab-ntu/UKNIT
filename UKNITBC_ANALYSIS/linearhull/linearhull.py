import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from uknit_bc import UKNITBC
#from calperm import genNibbleMatrix
import multiprocessing
import shutil
import os, sys, math

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

if __name__ == '__main__':
    ##################3
    if shutil.which( 'kissat' ) is None:
        print( 'kissat not found on PATH; install a SAT solver to rerun this historical linear-hull search.' )
        raise SystemExit(0)

    uknit_bc = UKNITBC()

    #!!!!!!!!!!!!!!!!
    CIPHER = uknit_bc
    ROUND = 8
    start = 2
    obj = 34
    print( ROUND, start, obj )
    #||||||||||||||||
    FILE = 'LinearHull'
    if os.path.isdir( FILE ) != True:
        os.system( 'mkdir %s' % FILE  )

    DIR = ''
    if CIPHER == uknit_bc:
        DIR = '%s/RES_UKNITBC_%d_%s' % ( FILE, ROUND, sys.argv[0] )

    if os.path.isdir( DIR ) != True:
        os.system( 'mkdir %s' % DIR )
    else:
        os.system( 'rm %s/*' % DIR )

    # round 0 - round 9
    #INPUT = [ 0,0,0,4,0,0,0,0,0,0,0,1,0,0,0,2 ]
    #OUTPUT = [ 0,1,0,0,0,0,0,0,0,0,0,8,0,0,1,0 ]

    #INPUT = [ 0,0,0,2,0,0,0,4,0,0,0,0,0,0,0,1 ]
    #OUTPUT = [ 8,0,0,8,0,0,9,2,0,0,0,0,0,0,0,0 ]

    #INPUT =  [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2]
    #OUTPUT = [0,0,0,6,0,0,4,0,0,0,0,0,5,0,0,0]

    #INPUT =  [0,0,0,0xa,0,0,0,0,0,0,0,2,0,0,0,0xa]
    #OUTPUT = [0,1,0,0,  0,0,0,0,0,0,0,8,0,0,1,0]

    #INPUT = INPUT[::-1]
    #OUTPUT = OUTPUT[::-1]

    INX = []
    OUTX = []

    T = {}
    Pro = 0
    PATH = []
    count = 0
    res = CIPHER.linearhullModel( start, start + ROUND, obj, INX, OUTX, PATH, seed = 15, time = 30 * 24 * 3600 )

    while isinstance( res, tuple ) and res[0] not in [0,-1]:
        count += 1
        #INX = res[0].X[0]
        #OUTX = res[0].Y[-1]

        tmp = res[0].printPath( latex = False )
        print( 'cor ', tmp )

        #Pro += 2 ** (-tmp)
        a = tuple( res[0].X[0] + res[0].Y[ROUND - 1] )
        if a in T:
            T[ a ] += 2 ** (2 * -tmp)
        else:
            T[ a ] = 2 ** (2 * -tmp)
        print( count, math.log( T[a], 2 ), flush = True )

        PATH.append( res[1] )

        res = CIPHER.linearhullModel( start, start + ROUND, obj, INX, OUTX, PATH, seed = 15, time = 30 * 24 * 3600 )

        if count == 100:
            break

    print( count )

    for k, v in T.items():
        print( k, math.log(v, 2) )
