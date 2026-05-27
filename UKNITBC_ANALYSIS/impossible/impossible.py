import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from uknit_bc import UKNITBC
#from calperm import genNibbleMatrix
import multiprocessing
import os, sys

def checkactive( C, start, ROUND, inputpos, outputpos, filename ):
    res = C.impossible( start, start + ROUND, inputpos, outputpos, seed = 1000 )
    if res == -1:
        resfile = open( filename, 'w' )
        print( start, start + ROUND, inputpos, outputpos, 'YES', file = resfile  )
        resfile.close()
    
    print( ROUND, start, inputpos, outputpos )
    '''
    elif res == 0:
        resfile = open( filename, 'w' )
        print( start, start + ROUND, inputpos, outputpos, 'ERROR', file = resfile  )
        resfile.close()
    else:
        resfile = open( filename, 'w' )
        print( start, start + ROUND, inputpos, outputpos, 'NO', file = resfile  )
        resfile.close()
    '''

if __name__ == '__main__':
    ##################3
    if len( sys.argv ) != 2:
        print( 'usage: python3 impossible.py <rounds>' )
        raise SystemExit(0)

    uknit_bc = UKNITBC()

    a = int( sys.argv[1] )
    #!!!!!!!!!!!!!!!!
    CIPHER = uknit_bc
    ROUND = a

    DIR = 'IMPOSSIBEL/'

    if os.path.isdir( DIR ) != True:
        os.system( 'mkdir %s' % DIR  )

    tasks = []
    for inputpos in range(0, 64):
        for outputpos in range(0, 64):
            for start in range(0, 12 - ROUND + 1):
                print( start, inputpos, outputpos )
                filename = '%s/impossible_uknitbc_round%d_start%d_input%d_output%d.txt' % (
                   DIR, ROUND, start, inputpos, outputpos )
                tasks.append( (CIPHER, start, ROUND, inputpos, outputpos, filename ) )

    with multiprocessing.Pool(processes=64) as pool:
        pool.starmap( checkactive, tasks )
    
