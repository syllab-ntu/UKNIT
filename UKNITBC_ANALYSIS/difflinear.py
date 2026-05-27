import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from myutility.sat import sat
from myutility.sbox import sbox as sbox
from path import path, keyrecoverypath
from myutility.espresso import genConstr
import galois
import numpy as np

class difflinear:
    def __init__(self):
        pass

    def DLAttack( self, start, end, middle, obj, seed = 0, time = 30 * 24 * 3600 ):
        '''
        Sbox -> L -> Sbox --> Sbox, (end - start) sboxes
        '''
        partcipher = []
        for i in range( start, end ):
            S = []
            for j in range(16):
                S.append( self.sbox( i, j ) )
            partcipher.append( S )
            if i < self.roundx - 1:
                partcipher.append( self.matrix( i ) )

        ROUND = end - start
        model = sat()
        X  = [ [ model.addVar() for i in range( 64 ) ] for j in range( ROUND ) ]
        Y  = [ [ model.addVar() for i in range( 64 ) ] for j in range( ROUND ) ]
        P0 = [ [ model.addVar() for i in range( 16 ) ] for j in range( ROUND ) ]
        P1 = [ [ model.addVar() for i in range( 16 ) ] for j in range( ROUND ) ]
        P2 = [ [ model.addVar() for i in range( 16 ) ] for j in range( ROUND ) ]

        for r in range( ROUND ):
            if r < middle:
                for i in range(16):
                    csbox = sbox( partcipher[2*r][i], 4, 4 )
                    constr = csbox.gen_cnf_for_DDT( BIT = 4 )
                    L = []
                    L += X[r][4*i: 4*i+4]
                    L += Y[r][4*i: 4*i+4]
                    L += [ P0[r][i] ]
                    L += [ P1[r][i] ]
                    L += [ P2[r][i] ]

                    model.exclude_set( L, constr )

            elif r == middle:
                for i in range(16):
                    csbox = sbox( partcipher[2*r][i], 4, 4 )
                    print( csbox._sbox )

                    constr = csbox.gen_cnf_for_DLCT( BIT = 4 )
                    L = []
                    L += X[r][4*i: 4*i+4]
                    L += Y[r][4*i: 4*i+4]
                    L += [ P0[r][i] ]
                    L += [ P1[r][i] ]
                    L += [ P2[r][i] ]

                    model.exclude_set( L, constr )

            else:
                # Sbox layer
                for i in range(16):
                    csbox = sbox( partcipher[2*r][i], 4, 4 )
                    constr = csbox.gen_cnf_for_LAT( BIT = 4 )
                    L = []
                    L += X[r][4*i: 4*i+4]
                    L += Y[r][4*i: 4*i+4]
                    #L += [ P0[r][i] ]
                    L += [ P1[r][i] ]
                    L += [ P2[r][i] ]

                    model.ASSIGN( P0[r][i], 0 )
                    model.exclude_set( L, constr )

            if r < ROUND - 1:
                for i in range(64):
                    L = [ X[r+1][i] ]
                    for j in range(64):
                        if partcipher[2*r+1][i][j] == 1:
                            L.append( Y[r][j] )
                    #print( L )
                    model.XOR3( L )

        model.exclude_vector( X[0], [0 for i in range(64) ] )
        model.exclude_vector( Y[ROUND-1], [0 for i in range(64) ] )

        P = []
        for r in range(ROUND):
            if r <= middle:
                for i in range(16):
                    P.append( P0[r][i] )
                    P.append( P1[r][i] )
                    P.append( P2[r][i] )
            else:
                for i in range(16):
                    P.append( P0[r][i] )
                    P.append( P0[r][i] )
                    P.append( P1[r][i] )
                    P.append( P1[r][i] )
                    P.append( P2[r][i] )
                    P.append( P2[r][i] )

        model.SEQSUM( P, obj )

        # run the model
        flag, resdict = model.solve( seed = seed, time = time )

        if flag == 1:
            for r in range( ROUND ):
                for i in range( 64 ):
                    X[r][i] = resdict[ X[r][i] ]
                    Y[r][i] = resdict[ Y[r][i] ]
            for r in range( ROUND ):
                for i in range( 16 ):
                    P0[r][i] = resdict[ P0[r][i] ]
                    P1[r][i] = resdict[ P1[r][i] ]
                    P2[r][i] = resdict[ P2[r][i] ]

            p = path( ROUND, X, Y, P0, P1, P2 )
            return p

        elif flag == -1:
            return -1
        else:
            return 0
