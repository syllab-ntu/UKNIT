import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import path
import os
from path import keyrecoverypath

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
    X = [ [ 0 for i in range(16) ] for j in range(11) ] 
    Y = [ [ 0 for i in range(16) ] for j in range(11) ] 
    P0 = [ [0 for i in range(16)] for i in range(11) ]
    P1 = [ [0 for i in range(16)] for i in range(11) ]
    P2 = [ [0 for i in range(16)] for i in range(11) ]

    X0 = [0] * 64
    for i in range(0, 64):
        if i >= 4:
            X0[i] = 1
    X[0] = GF2to16( X0 )

    X0 = [0] * 64
    for i in range(0, 16):
        if i in [8, 9, 10, 11]:
            for j in range(4):
                X0[4 * i + j] = 1
    X[1] = GF2to16( X0 )

    X0 = [0] * 64
    for i in range(0, 16):
        if i in [15]:
            for j in range(4):
                X0[4 * i + j] = 1
    X[2] = GF2to16( X0 )

    X0 = [0] * 64
    for i in range(0, 16):
        if i in [7, 10, 13]:
            for j in range(4):
                X0[4 * i + j] = 1
    X[9] = GF2to16( X0 )

    X0 = [0] * 64
    for i in range(0, 16):
        if i in [1, 2, 3,   4, 5, 6,   9, 10, 11,  12, 15]:
            for j in range(4):
                X0[4 * i + j] = 1
    X[10] = GF2to16( X0 )

    # Y
    X0 = [0] * 64
    for i in range(0, 64):
        if i >= 4:
            X0[i] = 1
    Y[0] = GF2to16( X0 )

    X0 = [0] * 64
    for i in range(0, 16):
        if i in [8, 9, 10, 11]:
            for j in range(4):
                X0[4 * i + j] = 1
    Y[1] = GF2to16( X0 )

    X0 = [0] * 64
    for i in range(0, 16):
        if i in [0]:
            for j in range(4):
                X0[4 * i + j] = 1
    Y[8] = GF2to16( X0 )

    X0 = [0] * 64
    for i in range(0, 16):
        if i in [7, 10, 13]:
            for j in range(4):
                X0[4 * i + j] = 1
    Y[9] = GF2to16( X0 )

    X0 = [0] * 64
    for i in range(0, 16):
        if i in [1, 2, 3,   4, 5, 6,   9, 10, 11,  12, 15]:
            for j in range(4):
                X0[4 * i + j] = 1
    Y[10] = GF2to16( X0 )

    path = keyrecoverypath( 2, 7, 2, X, Y, P0, P1, P2 )

    #print( path.X )

    Latex = 'IDKEY/path.tex'
    os.makedirs( os.path.dirname( Latex ), exist_ok = True )

    f = open( Latex, 'w' )
    print( path.printAttackFigure( 2, 7, 2, file = f ) )
    f.close()

    os.system( 'pdflatex --output-directory IDKEY/ %s' % Latex )
    os.system( 'rm IDKEY/*.aux')
    os.system( 'rm IDKEY/*.log')


