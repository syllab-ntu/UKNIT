import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from uknit_bc import UKNITBC
#from factor import cipher
#from filters import filters
import multiprocessing

def checkpro( C, start, ROUND, obj, filename ):
    f = open( filename, 'w' )
    print( "Window Start from ", start, file = f )
    print( "Trying obj = ", obj, file = f )
    res = C.linearModel( start, start + ROUND, obj, seed = 1000 )
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
        print( 'usage: python3 linear.py <rounds> <start_obj> <end_obj>' )
        raise SystemExit(0)

    CIPHER = UKNITBC()

    a = int( sys.argv[1] )
    b = int( sys.argv[2] )
    c = int( sys.argv[3] )

    ROUND = a
    START_OBJ = b
    END_OBJ = c
    #||||||||||||||||
    FILE = 'Linear'
    if os.path.isdir( FILE ) != True:
        os.system( 'mkdir %s' % FILE  )

    DIR = '%s/RES_UKNITBC_%d_%s' % ( FILE, ROUND, sys.argv[0] )

    if os.path.isdir( DIR ) != True:
        os.system( 'mkdir %s' % DIR )
    else:
        os.system( 'rm %s/*' % DIR )

    tasks = []
    for obj in range(START_OBJ, END_OBJ):
        for start in range(0, 12 - ROUND + 1):
        #for start in range(3, 4):
        #for start in range(4, 5):
        #for start in range(1, 2):
            filename = '%s/filter_round%d_start%d_obj%d.txt' % ( DIR, ROUND, start, obj )
            tasks.append( (CIPHER, start, ROUND, obj, filename ) )
    
    with multiprocessing.Pool(processes=16) as pool:
        pool.starmap( checkpro, tasks )
