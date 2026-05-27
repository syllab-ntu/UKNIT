import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from uknit_bc import UKNITBC
import multiprocessing
import os, sys

def GF2to16( x ):
    xx = [0] * 16
    for i in range(64):
        xx[i // 4] ^= x[i] << ( 3 - i % 4 )
    return xx

def checkpro( C, start, r0, r1, r2, middle, obj, pro, filename ):
    f = open( filename, 'w' )
    print( "Window Start from ", start, file = f )
    print( "Trying obj = ", obj, file = f )
    res = C.boomerangKeyRecovery( start, r0, r1, r2, middle, obj, pro, seed = 1000 )
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
    uknit_bc = UKNITBC()

    OBJS = [ [x, y] for x in range(51, 64) for y in range(20, 30) ]

    OBJS = [ [53, 29] ]

    for objs in OBJS:
        print( objs )
        #!!!!!!!!!!!!!!!!
        CIPHER = uknit_bc
        r0 = 2
        r1 = 7
        r2 = 1
        mid = 3
        START = 0

        OBJ1 = objs[0]
        OBJ2 = objs[1]

        #res = uknit_bc.MITM( START, START + ROUND, OBJ )
        res = uknit_bc.boomerangKeyRecovery( START, r0, r1, r2, mid, OBJ1, OBJ2 )

        if res == -1:
            print( 'No solution' )
            continue
        if res == 0:
            print( 'Time Out' )
            continue

        res.printPath()
        os.makedirs( 'LATEX', exist_ok = True )
        latex_file = rf'LATEX/latex3_{r0}_{r1}_{r2}_{mid}_{OBJ1}_{OBJ2}.tex' 
        f = open( latex_file, 'w' )
        print( '--' * 20 )

        res.printPath( )

        for i in range( len(res.X) ):
            res.X[i] = GF2to16( res.X[i] )
        for i in range( len(res.Y) ):
            res.Y[i] = GF2to16( res.Y[i] )


        res.printAttackFigure( r0, r1, r2, f )

        print()
        print()
        f.close()
        os.system( 'pdflatex --output-directory LATEX/ %s' % latex_file )
        os.system( 'rm LATEX/*.aux')
        os.system( 'rm LATEX/*.log')
