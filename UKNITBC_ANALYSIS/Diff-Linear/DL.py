import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from uknit_bc import UKNITBC
import multiprocessing
import os, sys

def checkpro( C, start, middle, ROUND, obj, filename ):
    f = open( filename, 'w' )
    print( "Window Start from ", start, file = f )
    print( "Trying obj = ", obj, file = f )
    res = C.DLAttack( start, start + ROUND, middle, obj )
    if res == -1:
        print( False, file = f )
    elif res == 0:
        print( 'Time Out', file = f )
    else:
        print( 'Has a path with obj = ', obj, file = f )
        res.printPath( f = f, latex = False )
    f.close()

if __name__ == '__main__':
    ##################3
    if len( sys.argv ) != 5:
        print( 'usage: python3 DL.py <rounds> <start_obj> <end_obj> <middle_round>' )
        raise SystemExit(0)

    uknit_bc = UKNITBC()

    a = int( sys.argv[1] )
    b = int( sys.argv[2] )
    c = int( sys.argv[3] )
    d = int ( sys.argv[4] )

    #!!!!!!!!!!!!!!!!
    CIPHER = uknit_bc
    ROUND = a
    START = b
    END = c
    middle = d
    #||||||||||||||||
    FILE = 'DL'
    if os.path.isdir( FILE ) != True:
        os.system( 'mkdir %s' % FILE  )

    DIR = ''
    if CIPHER == uknit_bc:
        DIR = '%s/RES_UKNITBC_%d_%d_%s' % ( FILE, middle, ROUND, sys.argv[0] )

    if os.path.isdir( DIR ) != True:
        os.system( 'mkdir %s' % DIR )
    else:
        os.system( 'rm %s/*' % DIR )

    tasks = []
    for obj in range(START, END):
        #for start in range(3, 12 - ROUND + 1):
        for start in range(3, 4):
        #for start in range(2, 3):
            filename = '%s/logfile_round%d_start%d_obj%d.txt' % ( DIR, ROUND, start, obj )
            tasks.append( (CIPHER, start, middle, ROUND, obj, filename ) )

    with multiprocessing.Pool(processes=16) as pool:
        pool.starmap( checkpro, tasks )
