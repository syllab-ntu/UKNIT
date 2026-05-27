import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from myutility.sat import sat
from myutility.sbox import sbox as sbox
from path import path, relatedkeypathW, relatedkeypathB, relatedkeypathFullBit2P, linear_path
from myutility.espresso import genConstr
#import galois
#import numpy as np

class rkdiffattack:
    def __init__(self):
        pass

    def relatedkeydiff_word( self, perm0, perm1, start, end, obj, seed = 0, time = 30 * 24 * 3600 ):
        '''
        Sbox -> L -> Sbox --> Sbox, (end - start) sboxes
        '''
        # generate the word xor
        XORS = []
        for x in range(16):
            x0 = x >> 3 & 0x1
            x1 = x >> 2 & 0x1
            x2 = x >> 1 & 0x1
            x3 = x >> 0 & 0x1
            if (x0 + x1 + x2 + x3) % 2 == 0:
                XORS.append( [ x0, x1, x2, x3 ] )
        XORS = genConstr( XORS )

        # generate the transform
        # bit -> vector
        IN = []
        for x in range(16):
            x0 = x >> 3 & 0x1
            x1 = x >> 2 & 0x1
            x2 = x >> 1 & 0x1
            x3 = x >> 0 & 0x1
            if x > 0:
                IN.append( [1, x0, x1, x2, x3] )
            else:
                IN.append( [0, x0, x1, x2, x3] )
        IN = genConstr( IN )

        OUT = []
        for x in range(16):
            x0 = x >> 3 & 0x1
            x1 = x >> 2 & 0x1
            x2 = x >> 1 & 0x1
            x3 = x >> 0 & 0x1

            if x > 0:
                OUT.append( [x0, x1, x2, x3, 1] )
            else:
                OUT.append( [x0, x1, x2, x3, 0] )
        OUT = genConstr( OUT )

        partcipher = []
        for i in range( start, end ):
            partcipher.append( self.matrix( i ) )

        ROUND = end - start

        model = sat()
        X  = [ [ model.addVar() for i in range( 16 ) ] for j in range( ROUND ) ]
        Y  = [ [ model.addVar() for i in range( 16 ) ] for j in range( ROUND ) ]
        YI  = [ [ model.addVar() for i in range( 64 ) ] for j in range( ROUND ) ]
        YO  = [ [ model.addVar() for i in range( 64 ) ] for j in range( ROUND ) ]
        K0  = [ model.addVar() for i in range( 16 )  ]
        K1  = [ model.addVar() for i in range( 16 )  ]

        KK0 = []
        KK1 = []

        KK0.append( K0[:] )
        KK1.append( K1[:] )

        for r in range( ROUND ):
            # xor key
            for i in range(16):
                L = []
                L.append( X[r][i] )
                L.append( K0[i] )
                L.append( K1[i] )
                L.append( Y[r][i] )
                model.exclude_set( L, XORS )

            K0x = []
            K1x = []
            for i in range(16):
                K0x.append( K0[i] )
                K1x.append( K1[i] )

            for i in range(16).append( X[r][i] ):
                K0[ perm0[i] ] = K0x[i]
                K1[ perm1[i] ] = K1x[i]

            KK0.append( K0[:] )
            KK1.append( K1[:] )

            if r < ROUND - 1:
                # transform
                for i in range(16):
                    L = [ Y[r][i], YI[r][4*i], YI[r][4*i+1], YI[r][4*i+2], YI[r][4*i+3] ]
                    model.exclude_set( L, IN )
                    L = [ YO[r][4*i], YO[r][4*i+1], YO[r][4*i+2], YO[r][4*i+3], X[r+1][r+1] ]
                    model.exclude_set( L, OUT )

                # Linear Layer
                for i in range(64):
                    L = [ YO[r][i] ]
                    for j in range(64):
                        if partcipher[r][i][j] == 1:
                            L.append( YI[r][j] )
                model.XOR3( L )

        model.exclude_vector( X[0], [0 for i in range(16) ] )

        P = []
        for r in range(ROUND):
            for i in range(16):
                P.append( Y[r][i] )

        model.SEQSUM( P, obj )

        # run the model
        flag, resdict = model.solve( seed = seed, time = time )

        if flag == 1:
            for r in range( ROUND ):
                for i in range( 16 ):
                    X[r][i] = resdict[ X[r][i] ]
                    Y[r][i] = resdict[ Y[r][i] ]
                    KK0[r][i] = resdict[ KK0[r][i] ]
                    KK1[r][i] = resdict[ KK1[r][i] ]
                    p = relatedkeypathW( ROUND, X, Y, KK0, KK1 )
            return p
        elif flag == -1:
            return -1
        else:
            return 0

    def relatedkeydiff_bit( self, perm0, perm1, start, end, obj, seed = 0, time = 30 * 24 * 3600 ):
        '''
        Sbox -> L -> Sbox --> Sbox, (end - start) sboxes
        '''
        # xor key
        L = []
        for k in range(2):
            if k == 0:
                for x in range(16):
                    LL = [ x >> 3 & 0x1, x >> 2 & 0x1, x >> 1 & 0x1, x >> 0 & 0x1, \
                                0, x >> 3 & 0x1, x >> 2 & 0x1, x >> 1 & 0x1, x & 0x1 ]
                    L.append( LL )
            elif k == 1:
                for x in range(16):
                    if x == 0:
                        for y in range(1, 16):
                            LL = [0, 0, 0, 0, 1, y>>3 & 0x1, y >> 2 & 0x1, y >> 1 & 0x1, y & 0x1 ]
                            L.append (LL)
                    else:
                        for y in range(0, 16):
                            LL = [x >> 3 & 0x1, x >> 2 & 1, x >> 1 & 1, x & 1, 1, y>>3 & 0x1, y >> 2 & 0x1, y >> 1 & 0x1, y & 0x1 ]
                            L.append (LL)

        XORS = genConstr( L )
        XOR2 = [ [0, 0, 0], [0, 1, 1], [1, 0, 1], [1, 1, 1], [1, 1, 0] ]
        XOR2 = genConstr( XOR2 )

        # generate the word xor
        partcipher = []
        for i in range( start, end ):
            S = []
            for j in range(16):
                S.append( self.sbox( i,  j ) )
            partcipher.append( S )
            if i < self.roundx - 1:
                partcipher.append( self.matrix( i ) )

        ROUND = end - start

        model = sat()
        X  =  [ [ model.addVar() for i in range( 64 ) ] for j in range( ROUND ) ]
        Y  =  [ [ model.addVar() for i in range( 64 ) ] for j in range( ROUND ) ]
        Z  =  [ [ model.addVar() for i in range( 64 ) ] for j in range( ROUND ) ]
        P0 =  [ [ model.addVar() for i in range( 16 ) ] for j in range( ROUND ) ]
        P1 =  [ [ model.addVar() for i in range( 16 ) ] for j in range( ROUND ) ]
        P2 =  [ [ model.addVar() for i in range( 16 ) ] for j in range( ROUND ) ]
        K0  = [ model.addVar() for i in range( 16 )  ]
        K1  = [ model.addVar() for i in range( 16 )  ]

        RK  = [ [ model.addVar() for i in range( 16 ) ] for j in range(ROUND)  ]

        KK0 = []
        KK1 = []

        for r in range( ROUND ):
            # XOR Round Key
            for i in range(16):
                L = [ K0[i], K1[i], RK[r][i] ]                #L.append( K0[i] )
                #L.append( K1[i] ):]
                model.exclude_set( L, XOR2 )

            # xor key
            for i in range(16):
                L = []
                L += [ X[r][4 * i], X[r][4*i+1], X[r][4*i+2], X[r][4*i+3] ]
                L.append( RK[r][i] )
                L += [ Y[r][4 * i], Y[r][4*i+1], Y[r][4*i+2], Y[r][4*i+3] ]

                #print( L )

                model.exclude_set( L, XORS )

            KK0.append( K0[:] )
            KK1.append( K1[:] )

            K0x = []
            K1x = []
            for i in range(16):
                K0x.append( K0[i] )
                K1x.append( K1[i] )

            for i in range(16):
                K0[ perm0[i] ] = K0x[i]
                K1[ perm1[i] ] = K1x[i]

            # transform
            # Sbox
            for i in range(16):
                csbox = sbox( partcipher[2*r][i], 4, 4 )
                constr = csbox.gen_cnf_for_DDT( BIT = 4 )
                L = []
                L += Y[r][4*i: 4*i+4]
                L += Z[r][4*i: 4*i+4]
                L += [ P0[r][i] ]
                L += [ P1[r][i] ]
                L += [ P2[r][i] ]
                model.exclude_set( L, constr )

            if r < ROUND - 1:
                # Linear Layer
                #for m in partcipher[2 * r + 1]:
                #    print( m )
                #print()
                for i in range(64):
                    L = [ X[r + 1][i] ]
                    for j in range(64):
                        if partcipher[2 * r + 1][i][j] == 1:
                            L.append( Z[r][j] )
                    model.XOR3( L )

        model.exclude_vector( X[0], [0 for i in range(64) ] )

        for r in range( ROUND - 1 ):
            for rr in range( r + 1, ROUND ):
                model.OR1( RK[r] + RK[rr] )
        P = []
        for r in range(ROUND):
            for i in range(16):
                P.append( P0[r][i] )
                P.append( P1[r][i] )
                P.append( P2[r][i] )

        model.SEQSUM( P, obj )

        # run the model
        flag, resdict = model.solve( seed = seed, time = time )

        if flag == 1:
            for r in range( ROUND ):
                for i in range( 64 ):
                    X[r][i] = resdict[ X[r][i] ]
                    Y[r][i] = resdict[ Y[r][i] ]
                    Z[r][i] = resdict[ Z[r][i] ]

                for i in range(16):
                    RK[r][i] = resdict[ RK[r][i] ]
                    KK0[r][i] = resdict[ KK0[r][i] ]
                    KK1[r][i] = resdict[ KK1[r][i] ]
                    P0[r][i] = resdict[ P0[r][i] ]
                    P1[r][i] = resdict[ P1[r][i] ]
                    P2[r][i] = resdict[ P2[r][i] ]

                    p = relatedkeypathB( ROUND, X, Y, Z, KK0, KK1, RK, P0, P1, P2 )
            return p
        elif flag == -1:
            return -1
        else:
            return 0

    def relatedkeydiff_fullybit_2P( self, perm0, perm1, start, end, obj, seed = 0, time = 30 * 24 * 3600 ):
        '''
        Sbox -> L -> Sbox --> Sbox, (end - start) sboxes
        '''
        # generate the word xor
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
        X  =  [ [ model.addVar() for i in range( 64 ) ] for j in range( ROUND ) ]
        Y  =  [ [ model.addVar() for i in range( 64 ) ] for j in range( ROUND ) ]
        Z  =  [ [ model.addVar() for i in range( 64 ) ] for j in range( ROUND ) ]
        P0 =  [ [ model.addVar() for i in range( 16 ) ] for j in range( ROUND ) ]
        P1 =  [ [ model.addVar() for i in range( 16 ) ] for j in range( ROUND ) ]
        P2 =  [ [ model.addVar() for i in range( 16 ) ] for j in range( ROUND ) ]
        K0  = [ model.addVar() for i in range( 64 )  ]
        K1  = [ model.addVar() for i in range( 64 )  ]

        KK0 = []
        KK1 = []

        for r in range( ROUND ):
            # XOR Round Key
            for i in range(64):
                L = []
                L.append( X [r][i] )
                L.append( K0[i] )
                L.append( K1[i] )
                L.append( Y [r][i] )
                #print( L )
                model.XOR3( L )

            KK0.append( K0[:] )
            KK1.append( K1[:] )

            # K0 --> LFSR
            for i in range(16):
                T = K0[4*i:4*i+4]
                K0[4*i] = T[1]
                K0[4*i+1] = T[2]
                K0[4*i+2] = T[3]
                a = model.addVar()
                model.XOR( [a, T[0], T[1] ] )
                K0[4*i+3] = a

            K0x = []
            K1x = []
            for i in range(64):
                K0x.append( K0[i] )
                K1x.append( K1[i] )

            for i in range(16):
                for j in range(4):
                    K0[ 4*perm0[i] + j ] = K0x[4 * i + j]
                    K1[ 4*perm1[i] + j ] = K1x[4 * i + j]

            # transform
            # Sbox
            for i in range(16):
                csbox = sbox( partcipher[2*r][i], 4, 4 )
                constr = csbox.gen_cnf_for_DDT( BIT = 4 )
                L = []
                L += Y[r][4*i: 4*i+4]
                L += Z[r][4*i: 4*i+4]
                L += [ P0[r][i] ]
                L += [ P1[r][i] ]
                L += [ P2[r][i] ]
                model.exclude_set( L, constr )

            if r < ROUND - 1:
                # Linear Layer
                #for m in partcipher[2 * r + 1]:
                #    print( m )
                #print()
                for i in range(64):
                    L = [ X[r + 1][i] ]
                    for j in range(64):
                        if partcipher[2 * r + 1][i][j] == 1:
                            L.append( Z[r][j] )
                    model.XOR3( L )

        model.exclude_vector( X[0], [0 for i in range(64) ] )

        P = []
        for r in range(ROUND):
            for i in range(16):
                P.append( P0[r][i] )
                P.append( P1[r][i] )
                P.append( P2[r][i] )

        model.SEQSUM( P, obj )

        # run the model
        flag, resdict = model.solve( seed = seed, time = time )

        if flag == 1:
            for r in range( ROUND ):
                for i in range( 64 ):
                    X[r][i] = resdict[ X[r][i] ]
                    Y[r][i] = resdict[ Y[r][i] ]
                    Z[r][i] = resdict[ Z[r][i] ]
                    KK0[r][i] = resdict[ KK0[r][i] ]
                    KK1[r][i] = resdict[ KK1[r][i] ]

                for i in range(16):
                    P0[r][i] = resdict[ P0[r][i] ]
                    P1[r][i] = resdict[ P1[r][i] ]
                    P2[r][i] = resdict[ P2[r][i] ]

                    p = relatedkeypathFullBit2P( ROUND, X, Y, Z, KK0, KK1, P0, P1, P2 )
            return p
        elif flag == -1:
            return -1
        else:
            return 0

    def relatedkeydiff_fullybit_M( self, M, start, end, obj, seed = 123, time = 30 * 24 * 3600 ):
        '''
        Sbox -> L -> Sbox --> Sbox, (end - start) sboxes
        parameters:
        M: the matrix used in the key schedule
        '''

        # generate the word xor
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
        X  =  [ [ model.addVar() for i in range( 64 ) ] for j in range( ROUND ) ]
        Y  =  [ [ model.addVar() for i in range( 64 ) ] for j in range( ROUND ) ]
        Z  =  [ [ model.addVar() for i in range( 64 ) ] for j in range( ROUND ) ]

        P0 =  [ [ model.addVar() for i in range( 16 ) ] for j in range( ROUND ) ]
        P1 =  [ [ model.addVar() for i in range( 16 ) ] for j in range( ROUND ) ]
        P2 =  [ [ model.addVar() for i in range( 16 ) ] for j in range( ROUND ) ]

        K0  = [ model.addVar() for i in range( 64 )  ]
        K1  = [ model.addVar() for i in range( 64 )  ]

        KK0 = []
        KK1 = []

        for r in range( ROUND ):

            # XOR Round Key
            for i in range(64):
                L = []
                L.append( X [r][i] )
                L.append( K0[i] )
                L.append( K1[i] )
                L.append( Y [r][i] )
                #print( L )
                model.XOR3( L )

            KK0.append( K0[:] )
            KK1.append( K1[:] )

            # K0 --> LFSR
            for i in range(16):
                T = K0[4*i:4*i+4]
                K0[4*i]   = T[1]
                K0[4*i+1] = T[2]
                K0[4*i+2] = T[3]
                a = model.addVar()
                model.XOR( [a, T[0], T[1] ] )
                K0[4*i+3] = a

            K0x = []
            K1x = []
            for i in range(64):
                K0x.append( K0[i] )
                K1x.append( K1[i] )

            for i in range(16):
                L = []
                for j in range(16):
                    if M[i][j] == 1:
                        L.append( j )
                if len(L) == 1:
                    K0[4 * i: 4 * i + 4] = K0x[ 4 * L[0]: 4 * L[0] + 4 ]
                elif len(L) == 2:
                    for j in range(4):
                        a = model.addVar()
                        model.XOR( [ a, K0x[ 4 * L[0] + j ], K0x[ 4 * L[1] + j ] ] )
                        K0[4 * i + j] = a
                elif len(L) == 3:
                    for j in range(4):
                        a = model.addVar()
                        model.XOR3( [ a, K0x[ 4 * L[0] + j ], K0x[ 4 * L[1] + j ], K0x[4 * L[2] + j] ] )
                        K0[4 * i + j] = a
                else:
                    print( "the hamming weight of the matrix has not been considered ")
                    exit(-1)


            for i in range(16):
                L = []
                for j in range(16):
                    if M[i][j] == 1:
                        L.append( j )
                if len(L) == 1:
                    K1[4 * i: 4 * i + 4] = K1x[ 4 * L[0]: 4 * L[0] + 4 ]
                elif len(L) == 2:
                    for j in range(4):
                        a = model.addVar()
                        model.XOR( [ a, K1x[ 4 * L[0] + j ], K1x[ 4 * L[1] + j ] ] )
                        K1[4 * i + j] = a
                elif len(L) == 3:
                    for j in range(4):
                        a = model.addVar()
                        model.XOR3( [ a, K1x[ 4 * L[0] + j ], K1x[ 4 * L[1] + j ], K1x[4 * L[2] + j] ] )
                        K1[4 * i + j] = a
                else:
                    print( "the hamming weight of the matrix has not been considered ")
                    exit(-1)


            # transform
            # Sbox
            for i in range(16):
                csbox = sbox( partcipher[2*r][i], 4, 4 )
                constr = csbox.gen_cnf_for_DDT( BIT = 4 )

                L = []
                L += Y[r][4*i: 4*i+4]
                L += Z[r][4*i: 4*i+4]
                L += [ P0[r][i] ]
                L += [ P1[r][i] ]
                L += [ P2[r][i] ]
                model.exclude_set( L, constr )

            if r < ROUND - 1:
                # Linear Layer
                #for m in partcipher[2 * r + 1]:
                #    print( m )
                #print()
                for i in range(64):
                    L = [ X[r + 1][i] ]
                    for j in range(64):
                        if partcipher[2 * r + 1][i][j] == 1:
                            L.append( Z[r][j] )
                    model.XOR3( L )

        model.exclude_vector( X[0], [0 for i in range(64) ] )

        P = []
        for r in range(ROUND):
            for i in range(16):
                P.append( P0[r][i] )
                P.append( P1[r][i] )
                P.append( P2[r][i] )

        model.SEQSUM( P, obj )

        # run the model
        flag, resdict = model.solve( seed = seed, time = time )

        if flag == 1:
            for r in range( ROUND ):
                for i in range( 64 ):
                    X[r][i] = resdict[ X[r][i] ]
                    Y[r][i] = resdict[ Y[r][i] ]
                    Z[r][i] = resdict[ Z[r][i] ]
                    KK0[r][i] = resdict[ KK0[r][i] ]
                    KK1[r][i] = resdict[ KK1[r][i] ]

                for i in range(16):
                    P0[r][i] = resdict[ P0[r][i] ]
                    P1[r][i] = resdict[ P1[r][i] ]
                    P2[r][i] = resdict[ P2[r][i] ]

                    p = relatedkeypathFullBit2P( ROUND, X, Y, Z, KK0, KK1, P0, P1, P2 )
            return p
        elif flag == -1:
            return -1
        else:
            return 0

    # a 64x64 bit-level matrix such as Prince's matrix 
    def relatedkeydiff_fullybit_Matrix( self, M, start, end, obj, roundx, pos, value, seed = 0, time = 30 * 24 * 3600 ):
        '''
        Sbox -> L -> Sbox --> Sbox, (end - start) sboxes
        '''

        # generate the word xor
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
        X  =  [ [ model.addVar() for i in range( 64 ) ] for j in range( ROUND ) ]
        Y  =  [ [ model.addVar() for i in range( 64 ) ] for j in range( ROUND ) ]
        Z  =  [ [ model.addVar() for i in range( 64 ) ] for j in range( ROUND ) ]
        P0 =  [ [ model.addVar() for i in range( 16 ) ] for j in range( ROUND ) ]
        P1 =  [ [ model.addVar() for i in range( 16 ) ] for j in range( ROUND ) ]
        P2 =  [ [ model.addVar() for i in range( 16 ) ] for j in range( ROUND ) ]
        K0  = [ model.addVar() for i in range( 64 )  ]
        K1  = [ model.addVar() for i in range( 64 )  ]

        KK0 = []
        KK1 = []

        for r in range( ROUND ):
            '''
            condition
            '''
            # XOR Round Key
            for i in range(64):
                L = []
                L.append( X [r][i] )
                L.append( K0[i] )
                L.append( K1[i] )
                L.append( Y [r][i] )
                #print( L )
                model.XOR3( L )

            KK0.append( K0[:] )
            KK1.append( K1[:] )

            # K0 --> LFSR
            for i in range(16):
                T = K0[4*i:4*i+4]
                K0[4*i]   = T[1]
                K0[4*i+1] = T[2]
                K0[4*i+2] = T[3]
                a = model.addVar()
                model.XOR( [a, T[0], T[1] ] )
                K0[4*i+3] = a

            K0x = []
            K1x = []
            for i in range(64):
                K0x.append( K0[i] )
                K1x.append( K1[i] )

            for i in range(64):
                L = []
                for j in range(64):
                    if M[i][j] == 1:
                        L.append( j )
                if len(L) == 1:
                    K0[i] = K0x[ L[0] ]
                elif len(L) == 2:
                    a = model.addVar()
                    model.XOR( [ a, K0x[ L[0] ], K0x[ L[1] ] ] )
                    K0[i] = a
                elif len(L) == 3:
                    a = model.addVar()
                    model.XOR3( [ a, K0x[ L[0] ], K0x[ L[1] ], K0x[ L[2] ] ] )
                    K0[i] = a
                else:
                    print( L )
                    print( "the hamming weight of the matrix has not been considered, %d " % len(L) )
                    exit(-1)

            for i in range(64):
                L = []
                for j in range(64):
                    if M[i][j] == 1:
                        L.append( j )
                if len(L) == 1:
                    K1[i] = K1x[ L[0] ]
                elif len(L) == 2:
                    a = model.addVar()
                    model.XOR( [ a, K1x[ L[0] ], K1x[  L[1] ] ] )
                    K1[ i ] = a
                elif len(L) == 3:
                    a = model.addVar()
                    model.XOR3( [ a, K1x[ L[0] ], K1x[  L[1] ], K1x[ L[2]  ] ] )
                    K1[i ] = a
                else:
                    print( "the hamming weight of the matrix has not been considered ")
                    exit(-1)

            # transform
            # Sbox
            for i in range(16):
                csbox = sbox( partcipher[2*r][i], 4, 4 )
                constr = csbox.gen_cnf_for_DDT( BIT = 4 )

                L = []
                L += Y[r][4*i: 4*i+4]
                L += Z[r][4*i: 4*i+4]
                L += [ P0[r][i] ]
                L += [ P1[r][i] ]
                L += [ P2[r][i] ]
                model.exclude_set( L, constr )

            if r < ROUND - 1:
                # Linear Layer
                #for m in partcipher[2 * r + 1]:
                #    print( m )
                #print()
                for i in range(64):
                    L = [ X[r + 1][i] ]
                    for j in range(64):
                        if partcipher[2 * r + 1][i][j] == 1:
                            L.append( Z[r][j] )
                    model.XOR3( L )

        model.exclude_vector( X[0], [0 for i in range(64) ] )

        P = []
        for r in range(ROUND):
            for i in range(16):
                P.append( P0[r][i] )
                P.append( P1[r][i] )
                P.append( P2[r][i] )

        model.SEQSUM( P, obj )

        # run the model
        flag, resdict = model.solve( seed = seed, time = time )

        if flag == 1:
            for r in range( ROUND ):
                for i in range( 64 ):
                    X[r][i] = resdict[ X[r][i] ]
                    Y[r][i] = resdict[ Y[r][i] ]
                    Z[r][i] = resdict[ Z[r][i] ]
                    KK0[r][i] = resdict[ KK0[r][i] ]
                    KK1[r][i] = resdict[ KK1[r][i] ]

                for i in range(16):
                    P0[r][i] = resdict[ P0[r][i] ]
                    P1[r][i] = resdict[ P1[r][i] ]
                    P2[r][i] = resdict[ P2[r][i] ]

                    p = relatedkeypathFullBit2P( ROUND, X, Y, Z, KK0, KK1, P0, P1, P2 )
            return p
        elif flag == -1:
            return -1
        else:
            return 0
