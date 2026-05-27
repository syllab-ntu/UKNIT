import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from uknit_bc import UKNITBC
from newcipher import newcipher
import multiprocessing
import shutil
import os, sys
from myutility.sbox import *

def GF2to16( x ):
    xx = [0] * 16
    for i in range(64):
        xx[i // 4] ^= x[i] << ( 3 - i % 4 )
    return xx

if __name__ == '__main__':
    if shutil.which( 'kissat' ) is None:
        print( 'kissat not found on PATH; install a SAT solver to rerun this historical linear key-recovery search.' )
        raise SystemExit(0)

    uknit_bc = UKNITBC()

    CIPHER = uknit_bc

    ATTACK = [ 
        [2, 6, 2, i, j, z] for j in range(20, 32) for i in range(22, 32) for z in range(3) 
               ]

    #ATTACK = [ [1, 7, 2, 26, 20, 0] ]

    for attack in ATTACK:
        r0 = attack[0]
        r1 = attack[1]
        r2 = attack[2]
        obj = attack[3]
        start = attack[5]
        pro = attack[4]

        latex_file = rf'Latex/latex_{r0}_{r1}_{r2}_{obj}_{pro}_{start}.tex' 
        print( 'Round: ', r0, r1, r2, obj, pro, start)

        FILE = 'keyrecovery'
        if os.path.isdir( FILE ) != True:
            os.system( 'mkdir %s' % FILE  )

        DIR = ''
        if CIPHER == uknit_bc:
            DIR = '%s/RES_UKNITBC_%d_%d_%d_%s' % ( FILE, r0, r1, r2, sys.argv[0] )

        if os.path.isdir( DIR ) != True:
            os.system( 'mkdir %s' % DIR )
        else:
            os.system( 'rm %s/*' % DIR )

        #filename = '%s/logfile_round%d_%d_%d_start%d_obj%d.txt' % ( DIR, r0, r1, r2, start, obj )

        res = uknit_bc.linear_keyrecoverydist( start, r0, r1, r2, obj, pro )

        if res not in [-1, 0]:
            pp = res.printPath( latex = False )
            print()
            print( pp )

            for i in range( len(res.X) ):
                res.X[i] = GF2to16( res.X[i] )
            for i in range( len(res.Y) ):
                res.Y[i] = GF2to16( res.Y[i] )

            f = open( latex_file, 'w')
            res.printAttackFigure( r0, r1, r2, file = f )
            f.close()

            os.system( 'pdflatex --output-directory Latex/ %s' % latex_file )
            os.system( 'rm Latex/*.aux')
            os.system( 'rm Latex/*.log')
        else:
            print( "No solution")
