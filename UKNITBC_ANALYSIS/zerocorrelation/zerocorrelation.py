import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from uknit_bc import UKNITBC
import multiprocessing

def checkmask( C, start, ROUND, inpos, outpos, filename ):
    res = C.zerocorrelation( start, start + ROUND, inpos, outpos, seed = 1000 )
    if res == -1:
        resfile = open( filename, 'w' )
        print( start, start + ROUND, inpos, outpos, 'YES', file = resfile  )
        resfile.close()
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
        print( 'usage: python3 zerocorrelation.py <rounds>' )
        raise SystemExit(0)

    CIPHER = UKNITBC()

    a = int( sys.argv[1] )

    ROUND = a

    #||||||||||||||||
    FILE = 'ZC'
    if os.path.isdir( FILE ) != True:
        os.system( 'mkdir %s' % FILE  )

    DIR = '%s/ROUND_UKNITBC_%d' % ( FILE, ROUND )

    if os.path.isdir( DIR ) != True:
        os.system( 'mkdir %s' % DIR )
    else:
        os.system( 'rm %s/*' % DIR )

    tasks = []
    for inpos in range(64):
        for outpos in range(64):
            for start in range(0, 12 - ROUND + 1):
                filename = '%s/zc_round%d_start%d_in%d_out%d.txt' % ( DIR, ROUND, start, inpos, outpos )
                tasks.append( (CIPHER, start, ROUND, inpos, outpos, filename ) )
    
    with multiprocessing.Pool(processes=16) as pool:
        pool.starmap( checkmask, tasks )
