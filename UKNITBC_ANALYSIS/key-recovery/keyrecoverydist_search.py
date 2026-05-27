import os
import sys
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

def printState( x, y, X, color, value = True ):
    S = []
    for i in range(16):
        if X[i] == 0:
            pass
        else:
            s =  rf'\fill[{color}] ({x + i//4},{y + 3 - i % 4}) rectangle  ++(1,1);' 
            S.append( s )
            if value:
                s = rf'\node at ( {x + i // 4 + 0.5}, {y + 3 - i % 4 + 0.5 } ) {{\textcolor{{white}}{{{X[i]:x}}}}};'
                S.append( s )

    s = rf'\foreach \x in {{0,1,2,3}}{{'
    S.append( s )
    s = rf'\foreach \y in {{0,1,2,3}} {{'
    S.append( s )
    s = rf'\draw ({x} + \x, {y} + \y) rectangle ++(1,1);'
    S.append( s )
    s = rf'}}'
    S.append( s )
    s = rf'}}'
    S.append( s )

    return S

def drawArrow( start, end, pos, text ):
    S = []
    s = rf'\draw[-latex] ({start}) -- node[ {pos} ] {text} ({end});'
    S.append( s )
    return S

def printFigure( r0, r1, r2, X, Y, color1 = 'DodgerBlue', color2 = 'DarkSlateGrey', color3 = 'DarkOrchid' ):
    S = []
    s = r'\begin{tikzpicture}[scale=0.3]'
    S.append( s )

    S += printState(0, 0, X[0], color1, False)
    S += printState(6, 0, Y[0], color2, True)
    S += printState(12, 0, X[1], color2, True)
    S += printState(12, -8, Y[7], color2, True)
    S += printState(6, -8, X[8], color2, True)
    S += printState(0, -8, Y[8], color3, False)
    S += printState(-6, -8, X[9], color3, False)
    S += printState(-12, -8, Y[9], color3, False)

    S += drawArrow( (4, 2), (6, 2), "above", r'$S$' )
    S += drawArrow( (10, 2), (12, 2), "above", r'$L$' )
    S += drawArrow( (14, 0), (14, -4), "right", r'$p$' )
    S += drawArrow( (12, -6), (10, -6), "above", r'$L$' )
    S += drawArrow( (6, -6), (4, -6), "above", r'$S$' )
    S += drawArrow( (0, -6), (-2, -6), "above", r'$L$' )
    S += drawArrow( (-6, -6), (-8, -6), "above", r'$S$' )

    s = r'\end{tikzpicture}'
    S.append( s )
    return S

if __name__ == '__main__':
    if shutil.which( 'kissat' ) is None:
        print( 'kissat not found on PATH; install a SAT solver to rerun this historical differential key-recovery search.' )
        raise SystemExit(0)

    uknit_bc = UKNITBC()

    CIPHER = uknit_bc

    '''

    # 1 + 7 + 2
    ATTACK = [ 
        [1, 7, 2, 53, 31, 0], 
        [1, 7, 2, 53, 31, 1], 
        [1, 7, 2, 53, 31, 2], 
        [1, 7, 2, 52, 31, 0], 
        [1, 7, 2, 52, 31, 1], 
        [1, 7, 2, 52, 31, 2], 
               ]
    '''

    '''
    # 2 + 7 + 1
    ATTACK = [ 
        [2, 7, 1, 53, 31, 0], 
        [2, 7, 1, 53, 31, 1], 
        [2, 7, 1, 53, 31, 2], 
        [2, 7, 1, 52, 31, 0], 
        [2, 7, 1, 52, 31, 1], 
        [2, 7, 1, 52, 31, 2], 
               ]
    '''

    '''
    # 3 + 5 + 2
    ATTACK = [ 
        [3, 5, 2, 54, 31, 0], 
        [3, 5, 2, 54, 31, 1], 
        [3, 5, 2, 54, 31, 2], 
        [3, 5, 2, 53, 31, 0], 
        [3, 5, 2, 53, 31, 1], 
        [3, 5, 2, 53, 31, 2], 
        [3, 5, 2, 52, 31, 0], 
        [3, 5, 2, 52, 31, 1], 
        [3, 5, 2, 52, 31, 2], 
               ]
    '''

    '''
    # 2 + 5 + 3
    ATTACK = [ 
        [2, 5, 3, 54, 31, 0], 
        [2, 5, 3, 54, 31, 1], 
        [2, 5, 3, 54, 31, 2], 
        [2, 5, 3, 53, 31, 0], 
        [2, 5, 3, 53, 31, 1], 
        [2, 5, 3, 52, 31, 2], 
        [2, 5, 3, 52, 31, 0], 
        [2, 5, 3, 52, 31, 1], 
        [2, 5, 3, 52, 31, 2], 
               ]
    '''
    '''
    ATTACK = [ 
        [2, 7, 2, 63, 32, 0],
        [2, 7, 2, 63, 32, 1],
        [2, 7, 2, 63, 32, 0],
        [2, 7, 2, 63, 32, 1],
    ]
    '''

    # 2 + 6 + 2
    ATTACK = [ [2, 7, 2, x, y, z] for x in range(52, 64) for y in range(20, 32) for z in range(2) ] 


    '''
    # 2 + 5 + 3
    ATTACK = [ 
        [2, 5, 3, 54, 31, 0], 
        [2, 5, 3, 54, 31, 1], 
        [2, 5, 3, 54, 31, 2], 
        [2, 5, 3, 53, 31, 0], 
        [2, 5, 3, 53, 31, 1], 
        [2, 5, 3, 52, 31, 2], 
        [2, 5, 3, 52, 31, 0], 
        [2, 5, 3, 52, 31, 1], 
        [2, 5, 3, 52, 31, 2], 
               ]

    # 2 + 5 + 3
    ATTACK = [ 
        [2, 5, 3, 54, 31, 0], 
        [2, 5, 3, 54, 31, 1], 
        [2, 5, 3, 54, 31, 2], 
        [2, 5, 3, 53, 31, 0], 
        [2, 5, 3, 53, 31, 1], 
        [2, 5, 3, 52, 31, 2], 
        [2, 5, 3, 52, 31, 0], 
        [2, 5, 3, 52, 31, 1], 
        [2, 5, 3, 52, 31, 2], 
               ]

    ATTACK = [ 
        [2, 7, 1, 54, 31, 0], 
        [2, 7, 1, 54, 31, 1], 
        [2, 7, 1, 54, 31, 2], 
        [2, 7, 1, 53, 31, 0], 
        [2, 7, 1, 53, 31, 1], 
        [2, 7, 1, 53, 31, 2], 
    ]

    ATTACK = [ 
        [1, 7, 2, 54, 31, 0], 
        [1, 7, 2, 54, 31, 1], 
        [1, 7, 2, 54, 31, 2], 
        [1, 7, 2, 53, 31, 0], 
        [1, 7, 2, 53, 31, 1], 
        [1, 7, 2, 53, 31, 2], 
    ]

    # 2 + 6 + 2
    ATTACK = [ 
        [2, 6, 2, 55, 28, 0], 
        [2, 6, 2, 55, 28, 1], 
        [2, 6, 2, 55, 28, 2], 
               ]

    ATTACK = [ 
        [2, 6, 2, 55, 30, 0], 
        [2, 6, 2, 55, 30, 1], 
        [2, 6, 2, 55, 30, 2], 
               ]
    '''

    for attack in ATTACK:
        r0 = attack[0]
        r1 = attack[1]
        r2 = attack[2]
        obj = attack[3]
        start = attack[5]
        pro = attack[4]

        latex_file = rf'Latex/diff/latex_uknitbc_{r0}_{r1}_{r2}_{obj}_{pro}_{start}.tex'

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

        res = uknit_bc.keyrecoverydist( start, r0, r1, r2, obj, pro )

        if res not in [-1, 0]:
            #pp = res.printPath( latex = False )
            #print()
            #print( pp )
            for i in range( len(res.X) ):
                res.X[i] = GF2to16( res.X[i] )
            for i in range( len(res.Y) ):
                res.Y[i] = GF2to16( res.Y[i] )

            #f = open( latex_file, 'w' )
            f = open( latex_file, 'w')
            res.printAttackFigure( r0, r1, r2, file = f )
            #res.printAttackFigure( r0, r1, r2 )
            f.close()

            os.system( 'pdflatex --output-directory Latex/diff/ %s' % latex_file )
            os.system( 'rm Latex/diff/*.aux')
            os.system( 'rm Latex/diff/*.log')

            #figure = printFigure( r0, r1, r2, res.X, res.Y )
            #print( '\n'.join( figure ) )
        else:
            #filename = '%s/logfile_round%d_%d_%d_start%d_obj%d.txt' % ( DIR, r0, r1, r2, start, obj )
            #f = open( filename, 'w' )
            #f = open( latex_file, 'w')
            #print( "No solution", file = f )
            print( "No solution" )
            #f.close()
