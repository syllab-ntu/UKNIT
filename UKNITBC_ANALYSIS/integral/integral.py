import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from uknit_bc import UKNITBC
from myutility import sbox
#import numpy as np
import multiprocessing

def checkDP( C, start, ROUND, inpos, outpos, filename ):
    res = C.division( start, start + ROUND, inpos, outpos, seed = 1000 )
    if res == -1:
        resfile = open( filename, 'w' )
        print( start, start + ROUND, inpos, outpos, 'YES', file = resfile  )
        resfile.close()
    print( ROUND, start, inpos, outpos ) 
    '''
    elif res == 0:
        print( 'Time Out', file = f )
    else:
        print( 'Has a path with obj = ', obj, file = f )
        res.printPath( f = f, latex = True )
    f.close()
    '''

if __name__ == '__main__':
    ##################3
    if len( sys.argv ) != 2:
        print( 'usage: python3 integral.py <rounds>' )
        raise SystemExit(0)

    uknit_bc = UKNITBC()

    a = int( sys.argv[1] )
    #!!!!!!!!!!!!!!!!
    CIPHER = uknit_bc
    ROUND = a

    DIR = 'DP/ROUND%d/'%a

    if os.path.isdir( DIR ) != True:
        os.system( 'mkdir %s' % DIR  )

    os.system( 'rm %s/*' % DIR)

    tasks = []
    for inputpos in range(0, 64):
        for outputpos in range(0, 64):
            for start in range(0, 12 - ROUND + 1):
                #print( start, inputpos, outputpos )
                filename = '%s/DP_UKNITBC_round%d_start%d_input%d_output%d.txt' % (
                DIR, ROUND, start, inputpos, outputpos )
                tasks.append( (CIPHER, start, ROUND, inputpos, outputpos, filename ) )

    with multiprocessing.Pool(processes=16) as pool:
        pool.starmap( checkDP, tasks )
