import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from myutility.sat import sat
from myutility.sbox import sbox as sbox
from path import path,  linear_path, keyrecoverypath
from myutility.espresso import genConstr
import galois
import numpy as np

class linearattack:
    def __init__(self):
        pass

    def linearModel( self, start, end, obj, seed = 0, time = 30 * 24 * 3600 ):
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

        for r in range( ROUND ):
            # Sbox layer
            for i in range(16):
                csbox = sbox( partcipher[2*r][i], 4, 4 )
                constr = csbox.gen_cnf_for_LAT( BIT = 4 )
                L = []
                L += X[r][4*i: 4*i+4]
                L += Y[r][4*i: 4*i+4]
                L += [ P0[r][i] ]
                L += [ P1[r][i] ]
                model.exclude_set( L, constr )
            if r < ROUND - 1:
                for i in range(64):
                    L = [ Y[r][i] ]
                    for j in range(64):
                        if partcipher[2*r+1][j][i] == 1:
                            L.append( X[r + 1][j] )
                    #print( L )
                    model.XOR3( L )

        model.exclude_vector( X[0], [0 for i in range(64) ] )

        P = []
        for r in range(ROUND):
            for i in range(16):
                P.append( P0[r][i] )
                P.append( P1[r][i] )

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

            p = linear_path( ROUND, X, Y, P0, P1 )
            return p
        elif flag == -1:
            return -1
        else:
            return 0

    def linearhullModel( self, start, end, obj, INPUT, OUTPUT, PATH, seed = 0, time = 30 * 24 * 3600 ):
        '''
        given IPUT and OUTPUT, we should search for the first path with obj 
        then we exclude the whole path, search again
        in this case, we need a function that can exclude some solutions
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

        # input and output constraints
        if len(INPUT) > 0:
            for i in range(64):
                model.ASSIGN( X[0][i], INPUT[i] )
                model.ASSIGN( Y[ROUND-1][i], OUTPUT[i] )

        for r in range( ROUND ):
            # Sbox layer
            for i in range(16):
                csbox = sbox( partcipher[2*r][i], 4, 4 )
                constr = csbox.gen_cnf_for_LAT( BIT = 4 )
                L = []
                L += X[r][4*i: 4*i+4]
                L += Y[r][4*i: 4*i+4]
                L += [ P0[r][i] ]
                L += [ P1[r][i] ]
                model.exclude_set( L, constr )

            if r < ROUND - 1:
                for i in range(64):
                    L = [ Y[r][i] ]
                    for j in range(64):
                        if partcipher[2*r+1][j][i] == 1:
                            L.append( X[r + 1][j] )
                    #print( L )
                    model.XOR3( L )

        model.exclude_vector( X[0], [0 for i in range(64) ] )

        if len( PATH ) != 0:
            V = []
            for r in range( ROUND ):
                for i in range(64):
                    V.append( X[r][i] )

            for r in range( ROUND ):
                for i in range(64):
                    V.append( Y[r][i] )

            model.exclude_set (V, PATH) 

        P = []

        for r in range(ROUND):
            for i in range(16):
                P.append( P0[r][i] )
                P.append( P1[r][i] )

        model.SEQSUM( P, obj )

        # run the model
        flag, resdict = model.solve( seed = seed, time = time, delete = False )

        if flag == 1:
            for r in range( ROUND ):
                for i in range( 64 ):
                    X[r][i] = resdict[ X[r][i] ]
                    Y[r][i] = resdict[ Y[r][i] ]
            for r in range( ROUND ):
                for i in range( 16 ):
                    P0[r][i] = resdict[ P0[r][i] ]
                    P1[r][i] = resdict[ P1[r][i] ]

            p = linear_path( ROUND, X, Y, P0, P1 )
            PATH = []
            for r in range( ROUND ):
                for i in range(64):
                    PATH.append( X[r][i] )
            for r in range( ROUND ):
                for i in range(64):
                    PATH.append( Y[r][i] )
            return p, PATH
        elif flag == -1:
            return -1
        else:
            return 0

    def linear_keyrecoverydist( self, start, r0, r1, r2, obj, pro, seed = 0, time = 30 * 24 * 3600 ):
        partcipher = []
        for i in range( start, start + r0 + r1 + r2 ):
            S = []
            for j in range(16):
                S.append( self.sbox( i, j ) )
            partcipher.append( S )
            if i < self.roundx - 1:
                partcipher.append( self.matrix( i ) )

        model = sat()
        X  = [ [ model.addVar() for i in range( 64 ) ] for j in range( r0 + r1 + r2 ) ]
        Y  = [ [ model.addVar() for i in range( 64 ) ] for j in range( r0 + r1 + r2 ) ]
        P0 = [ [ model.addVar() for i in range( 16 ) ] for j in range( r1 ) ]
        P1 = [ [ model.addVar() for i in range( 16 ) ] for j in range( r1 ) ]

        # sbox active pattern
        # if input is active, output is also active
        Pattern = [] # [ [ 1, 1, 1 ], [0, 0, 0 ] ]
        for xx in range(16):
            for yy in range(16):
                if xx == 0xf and yy > 0:
                    L = []
                    L.append( xx >> 3 & 0x1 )
                    L.append( xx >> 2 & 0x1 )
                    L.append( xx >> 1 & 0x1 )
                    L.append( xx >> 0 & 0x1 )
                    L.append( yy >> 3 & 0x1 )
                    L.append( yy >> 2 & 0x1 )
                    L.append( yy >> 1 & 0x1 )
                    L.append( yy >> 0 & 0x1 )
                    Pattern.append( L )
                elif xx == 0 and yy == 0:
                    L = []
                    L.append( xx >> 3 & 0x1 )
                    L.append( xx >> 2 & 0x1 )
                    L.append( xx >> 1 & 0x1 )
                    L.append( xx >> 0 & 0x1 )
                    L.append( yy >> 3 & 0x1 )
                    L.append( yy >> 2 & 0x1 )
                    L.append( yy >> 1 & 0x1 )
                    L.append( yy >> 0 & 0x1 )
                    Pattern.append( L )
        C0 = genConstr( Pattern )

        # the linear layer, for linear cryptanalysis, the matrix should be the inverse transpose
        Pattern = []
        for xx in range(8):
            for yy in range(2):
                if xx == 7 and yy > 0:
                    L = []
                    L.append( xx >> 2 & 0x1 )
                    L.append( xx >> 1 & 0x1 )
                    L.append( xx >> 0 & 0x1 )
                    L.append( yy )
                    Pattern.append( L )
                elif xx == 0 and yy == 0:
                    L = []
                    L.append( xx >> 2 & 0x1 )
                    L.append( xx >> 1 & 0x1 )
                    L.append( xx >> 0 & 0x1 )
                    L.append( yy )
                    Pattern.append( L )
        C1 = genConstr( Pattern )

        for r in range(0, r0):
            # Sbox
            for i in range(16):
                L = []
                L += X[r][4*i: 4*i+4]
                L += Y[r][4*i: 4*i+4]
                model.exclude_set( L, C0 )
            if r < r0 - 1:
                # this is for passing of the value
                matrix = partcipher[2 * r + 1]
                for i in range(64):
                    L = []
                    for j in range(64):
                        if matrix[i][j] == 1:
                            L.append( Y[r][j] )
                    L.append( X[r+1][i] )
                    model.exclude_set( L, C1 )
            else:
                print( 'r = %d' % r)
                GF2 = galois.GF(2)
                matrix = partcipher[2 * r + 1]
                M = GF2( np.array( matrix ) )

                Mtinv = np.linalg.inv(M.transpose() ).tolist()


                for i in range(64):
                    L = []
                    for j in range(64):
                        if Mtinv[i][j] == 1:
                            L.append( Y[r][j] )
                    L.append( X[r+1][i] )
                    model.XOR3( L )

        for r in range( r0, r0 + r1 ):
            # linear layer
            # Sbox layer
            for i in range(16):
                csbox = sbox( partcipher[2*r][i], 4, 4 )
                constr = csbox.gen_cnf_for_LAT( BIT = 4 )
                L = []
                L += X[r][4*i: 4*i+4]
                L += Y[r][4*i: 4*i+4]
                L += [ P0[r - r0][i] ]
                L += [ P1[r - r0][i] ]
                model.exclude_set( L, constr )

            # linear layer
            GF2 = galois.GF(2)
            matrix = partcipher[2 * r + 1]
            M = GF2( np.array( matrix ) )
            Mtinv = np.linalg.inv( M.transpose() ).tolist()
            for i in range(64):
                L = [ X[r+1][i] ]
                for j in range(64):
                    if Mtinv[i][j] == 1:
                        L.append( Y[r][j] )
                #print( L )
                model.XOR3( L )

        for r in range(r0 + r1, r0 + r1 + r2):
            # Sbox
            for i in range(16):
                L = []
                L += Y[r][4*i: 4*i+4]
                L += X[r][4*i: 4*i+4]
                model.exclude_set( L, C0 )
            if r < r0 + r1 + r2 - 1:
                # get inverse of matrix
                GF2 = galois.GF(2)
                matrix = partcipher[2 * r + 1]
                M = GF2( np.array( matrix ) )
                Minv = np.linalg.inv( M ).tolist() 

                for i in range(64):
                    L = []
                    for j in range(64):
                        if Minv[i][j] == 1:
                            L.append( X[r + 1][j] )
                    L.append( Y[r][i] )
                    model.exclude_set( L, C1 )

        model.exclude_vector( X[r0], [0 for i in range(64) ] )

        P = []
        for r in range(r1):
            for i in range(16):
                P.append( P0[r][i] )
                P.append( P1[r][i] )

        model.SEQSUM( P, obj )

        # active -> 1
        Pattern = []
        for x in range(16):
            for y in range(2):
                if x == 0 and y == 0:
                    L = []
                    L.append( x >> 3 & 0x1 )
                    L.append( x >> 2 & 0x1 )
                    L.append( x >> 1 & 0x1 )
                    L.append( x >> 0 & 0x1 )
                    L.append( y  )
                    Pattern.append( L )
                if x > 0 and y == 1:
                    L = []
                    L.append( x >> 3 & 0x1 )
                    L.append( x >> 2 & 0x1 )
                    L.append( x >> 1 & 0x1 )
                    L.append( x >> 0 & 0x1 )
                    L.append( y  )
                    Pattern.append( L )
        C2 = genConstr( Pattern )

        A = [ [ model.addVar() for i in range(16) ] for j in range( r0 + r2 ) ]

        for r in range(r0):
            for i in range(16):
                L = []
                for j in range(4):
                    L.append( X[r][4*i+j] )
                L.append( A[r][i] )
                model.exclude_set( L, C2 )

        for r in range(r2):
            for i in range(16):
                L = []
                for j in range(4):
                    L.append( Y[-1 - r][4*i+j] )
                L.append( A[-1-r][i] )
                model.exclude_set( L, C2 )

        AA = []
        for r in range( r0 + r2 ):
            AA += A[r]
        model.SEQSUM( AA, pro )

        # run the model
        flag, resdict = model.solve( seed = seed, time = time, delete = True )

        if flag == 1:
            for r in range( r0 + r1 + r2 ):
                for i in range( 64 ):
                    X[r][i] = resdict[ X[r][i] ]
                    Y[r][i] = resdict[ Y[r][i] ]
            for r in range( r1 ):
                for i in range( 16 ):
                    P0[r][i] = resdict[ P0[r][i] ]
                    P1[r][i] = resdict[ P1[r][i] ]
            
            #print( X[2] )
            #input()
            p = keyrecoverypath( r0, r1, r2, X, Y, P0, P1)
            return p
        elif flag == -1:
            return -1
        else:
            return 0

    def zerocorrelation( self, start, end, inpos, outpos, seed = 0, time = 30 * 24 * 3600 ):
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

        for r in range( ROUND ):
            # Sbox layer
            for i in range(16):
                csbox = sbox( partcipher[2*r][i], 4, 4 )
                constr = csbox.gen_cnf_for_LAT_withoutC( BIT = 4 )
                L = []
                L += X[r][4*i: 4*i+4]
                L += Y[r][4*i: 4*i+4]
                model.exclude_set( L, constr )
            if r < ROUND - 1:
                for i in range(64):
                    L = [ Y[r][i] ]
                    for j in range(64):
                        if partcipher[2*r+1][j][i] == 1:
                            L.append( X[r + 1][j] )
                    #print( L )
                    model.XOR3( L )

        #model.exclude_vector( X[0], [0 for i in range(64) ] )

        for i in range(64):
            if i == inpos:
                model.ASSIGN( X[0][i], 1 )
            else:
                model.ASSIGN( X[0][i], 0 )

        for i in range(64):
            if i == outpos:
                model.ASSIGN( Y[ROUND-1][i], 1 )
            else:
                model.ASSIGN( Y[ROUND-1][i], 0 )

        # run the model
        flag, resdict = model.solve( seed = seed, time = time )

        if flag == 1:
            return 1
        elif flag == -1:
            return -1
        else:
            return 0
