import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from myutility.sat import sat
from myutility.sbox import sbox as sbox
from path import path, keyrecoverypath
from myutility.espresso import genConstr
#import galois
#import numpy as np


class divisionproperty:
    def __init__(self):
        pass

    def ModelMatrix(self, model, M, X, Y): 
        # model the division property from X to Y
        # copy for each columns
        COPYL = [ [0, 0, 0, 0], 
                  [1, 0, 0, 1], [1, 0, 1, 0], [1, 0, 1, 1], 
                  [1, 1, 0, 0], [1, 1, 0, 1], [1, 1, 1, 0], [1, 1, 1, 1] ]
        COPYC = genConstr( COPYL )

        XORL = [  [0, 0, 0, 0], 
                  [1, 0, 0, 1], [0, 1, 0, 1], [0, 0, 1, 1] ]
        XORC = genConstr( XORL )

        XL = {}
        for i in range(64):
            XL[i] = []
            X0 = model.addVar()
            XL[i].append(X0)
            X1 = model.addVar()
            XL[i].append(X1)
            X2 = model.addVar()
            XL[i].append(X2)
            model.exclude_set( [ X[i], X0, X1, X2 ], COPYC )

        for i in range(64):
            L = []
            for j in range(64):
                if M[i][j] == 1:
                    L.append( XL[j][-1] )
                    XL[j] = XL[j][0:-1]
            L.append( Y[i] )
            assert len(L) == 4, 'the length is not correct'

            model.exclude_set( L, XORC )

    def division( self, start, end, inpos, outpos, seed = 0, time = 30 * 24 * 3600 ):
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
        Z  = [ [ model.addVar() for i in range( 64 ) ] for j in range( ROUND ) ]

        K = [ [ model.addVar() for i in range(64) ] for r in range(ROUND) ]

        XORL = [ [0,0,0], [0,1,1], [1,0,1] ]
        XORC = genConstr( XORL )
        for r in range( ROUND ):
            # XOR keys
            for i in range(64):
                model.exclude_set( [ X[r][i], K[r][i], Y[r][i] ], XORC )

            # Sbox layer
            for i in range(16):
                csbox = sbox( partcipher[2*r][i], 4, 4 )
                #print( partcipher[2*r][i] )
                constr = csbox.gen_cnf_for_MPT( BIT = 4 )
                #csbox.print2DTable( csbox.genMPT(), 4,4 )

                L = []
                L += Y[r][4*i: 4*i+4]
                L += Z[r][4*i: 4*i+4]
                model.exclude_set( L, constr )

            if r < ROUND - 1:
                #pass
                matrix = partcipher[2 * r + 1]
                #print( matrix )
                self.ModelMatrix( model, matrix, Z[r], X[r + 1] )

        for i in range(64):
            if i == inpos:
                model.ASSIGN( X[0][i], 0 )
            else:
                model.ASSIGN( X[0][i], 1 )
        
        for i in range(64):
            if i == outpos:
                model.ASSIGN( Z[ROUND-1][i], 1 )
            else:
                model.ASSIGN( Z[ROUND-1][i], 0 )
        # run the model

        flag, resdict = model.solve( seed = seed, time = time )

        if flag == 1:
            return 1
        elif flag == -1:
            return -1
        else:
            return 0
