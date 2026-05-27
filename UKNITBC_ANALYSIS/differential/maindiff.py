import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from uknit_bc import UKNITBC
#from calperm import genNibbleMatrix
import multiprocessing
import os, sys

def checkpro( C, start, ROUND, obj, filename ):
    f = open( filename, 'w' )
    print( "Window Start from ", start, file = f )
    print( "Trying obj = ", obj, file = f )
    res = C.diffModel( start, start + ROUND, obj, seed = 1000 )
    if res == -1:
        print( False, file = f )
    elif res == 0:
        print( 'Time Out', file = f )
    else:
        print( 'Has a path with obj = ', obj, file = f )
        res.printPath( f = f, latex = True )
    f.close()

if __name__ == '__main__':
    ##################3
    if len( sys.argv ) != 4:
        print( 'usage: python3 maindiff.py <rounds> <start_obj> <end_obj>' )
        raise SystemExit(0)

    uknit_bc = UKNITBC()

    a = int( sys.argv[1] )
    b = int( sys.argv[2] )
    c = int( sys.argv[3] )

    #!!!!!!!!!!!!!!!!
    CIPHER = uknit_bc
    ROUND = a
    START = b
    END = c
    #||||||||||||||||
    FILE = 'Differential'
    if os.path.isdir( FILE ) != True:
        os.system( 'mkdir %s' % FILE  )

    DIR = ''
    if CIPHER == uknit_bc:
        DIR = '%s/RES_UKNITBC_%d_%s' % ( FILE, ROUND, sys.argv[0] )

    if os.path.isdir( DIR ) != True:
        os.system( 'mkdir %s' % DIR )
    else:
        os.system( 'rm %s/*' % DIR )

    tasks = []
    for obj in range(START, END):
        for start in range(0, 12 - ROUND + 1):
            filename = '%s/logfile_round%d_start%d_obj%d.txt' % ( DIR, ROUND, start, obj )
            tasks.append( (CIPHER, start, ROUND, obj, filename ) )

    with multiprocessing.Pool(processes=64) as pool:
        pool.starmap( checkpro, tasks )
