import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from myutility.sat import sat
from myutility.sbox import sbox
from path import path,  linear_path, keyrecoverypath, MITMPath, MITMPathKey
from myutility.espresso import genConstr
import galois
import numpy as np

class mitmattack:
    def __init__(self):
        pass

        # get the part of the cipher
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
        FX  = [ [ model.addVar() for i in range( 64 ) ] for j in range( ROUND ) ]
        FY  = [ [ model.addVar() for i in range( 64 ) ] for j in range( ROUND ) ]

        SBOXC = genConstr( [ [0,0,0,0, 0,0,0,0], [1,1,1,1, 1,1,1,1] ] )
        LC = genConstr( [ [0, 0, 0, 0], 
               [0, 0, 0, 1], 
               [0, 0, 1, 1], 
               [0, 1, 0, 1], 
               [0, 1, 1, 1], 
               [1, 0, 0, 1], 
               [1, 0, 1, 1], 
               [1, 1, 0, 1], 
               [1, 1, 1, 1], 
              ] )

        for r in range( ROUND ):
            # Sbox layer
            for i in range(16):
                #csbox = sbox( partcipher[2*r][i], 4, 4 )
                #constr = csbox.gen_cnf_for_LAT( BIT = 4 )
                L = []
                L += FX[r][4*i: 4*i+4]
                L += FY[r][4*i: 4*i+4]

                #print( L, SBOXC )
                model.exclude_set( L, SBOXC )

            if r < ROUND - 1:
                GF2 = galois.GF(2)
                M = GF2( partcipher[2 * r + 1], dtype = int )

                for i in range(64):
                    L = []
                    for j in range(64):
                        if M[i][j] == 1:
                            L.append( FY[r][j] )
                    L.append( FX[r + 1][i] )
                    model.exclude_set( L, LC )

        model.exclude_vector( FX[0], [ 0 for i in range(64) ] )

        '''
        for i in range(16):
            if i == 2:
                for j in range(4):
                    model.ASSIGN( FX[0][4 * i + j], 1 )
            else:
                for j in range(4):
                    model.ASSIGN( FX[0][4 * i + j], 0 )
        '''

        # backward

        BX  = [ [ model.addVar() for i in range( 64 ) ] for j in range( ROUND ) ]
        BY  = [ [ model.addVar() for i in range( 64 ) ] for j in range( ROUND ) ]

        for r in range( ROUND - 1, -1, -1 ):
            # Sbox layer
            for i in range(16):
                L = []
                L += BY[r][4*i: 4*i+4]
                L += BX[r][4*i: 4*i+4]
                model.exclude_set( L, SBOXC )
            if r > 0:
                GF2 = galois.GF(2)
                M = np.linalg.inv( GF2( partcipher[2 * r + 1], dtype = int ) )

                for i in range(64):
                    L = []
                    for j in range(64):
                        if M[i][j] == 1:
                            L.append( BX[r][j] )
                    L.append( BY[r-1][i] )
                    model.exclude_set( L, LC )

        model.exclude_vector( BX[ROUND-1], [0 for i in range(64) ] )

        '''
        for i in range(16):
            if i == B:
                for j in range(4):
                    model.ASSIGN( BX[ROUND-1][4 * i + j], 1 )
            else:
                for j in range(4):
                    model.ASSIGN( BX[ROUND-1][4 * i + j], 0 )
        '''

        ZX  = [ [ model.addVar() for i in range( 64 ) ] for j in range( ROUND ) ]
        ZC = genConstr( [ [1,1,1], 
                          [0,0,0], 
                          [0,1,0], 
                          [1,0,0], 
                          ] )

        for r in range( ROUND ):
            for i in range(64):
                L = [ FX[r][i], BX[r][i], ZX[r][i] ]
                model.exclude_set( L, ZC )

        L = []
        for r in range( 0, ROUND ):
            for i in range(64):
                L.append( ZX[r][i] )

        model.SEQSUM( L, obj )

        # run the model
        flag, resdict = model.solve( seed = seed, time = time, delete = True )

        #print( resdict )

        if flag == 1:
            for r in range( ROUND ):
                for i in range( 64 ):
                    ZX[r][i] = resdict[ ZX[r][i] ]
                    FX[r][i] = resdict[ FX[r][i] ]
                    BX[r][i] = resdict[ BX[r][i] ]

            mpath = MITMPath( ZX, ROUND )
            mpath.printPath()

            print()

            mpath = MITMPath( FX, ROUND )
            mpath.printPath()

            print()

            mpath = MITMPath( BX, ROUND )
            mpath.printPath()
            return 1
        elif flag == -1:
            return -1
        else:
            return 0

    def MITM_Attack( self, start, r0, r1, r2, obj1, obj2, A = -1, B = -1, seed = 0, time = 30 * 24 * 3600 ):
        # get the part of the cipher
        partcipher = []
        for i in range( start, start + r0 + r1 + r2 ):
            S = []
            for j in range(16):
                S.append( self.sbox( i, j ) )
            partcipher.append( S )
            if i < self.roundx - 1:
                partcipher.append( self.matrix( i ) )

        model = sat()
        
        X  = [ [ model.addVar() for i in range( 64 ) ] for j in range( r0 + 1 ) ]
        Y  = [ [ model.addVar() for i in range( 64 ) ] for j in range( r0 ) ]

        # sbox active pattern
        Pattern = []
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
                elif xx >= 0 and yy == 0:
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

            # get inverse of matrix
            matrix = partcipher[2 * r + 1]
            for i in range(64):
                L = []
                for j in range(64):
                    if matrix[i][j] == 1:
                        L.append( Y[r][j] )
                L.append( X[r+1][i] )
                model.exclude_set( L, C1 )
                #print( INDEX )
    

        Z  = [ [ model.addVar() for i in range( 64 ) ] for j in range( r2 + 1 ) ]
        W  = [ [ model.addVar() for i in range( 64 ) ] for j in range( r2 ) ]

        for r in range( r0 + r1, r0 + r1 + r2 ):
            rr = r - r0 - r1

            # get inverse of matrix
            GF2 = galois.GF(2)
            matrix = partcipher[2 * (r-1) + 1]
            M = GF2( np.array( matrix ) )
            Minv = np.linalg.inv( M ).tolist() 

            # Z --> W
            for i in range(64):
                L = []
                for j in range(64):
                    if Minv[i][j] == 1:
                        L.append( W[rr][j] )
                L.append( Z[rr][i] )
                model.exclude_set( L, C1 )

            # Sbox
            for i in range(16):
                L = []
                L += Z[rr + 1][4*i: 4*i+4]
                L += W[rr][4*i: 4*i+4]
                model.exclude_set( L, C0 )

        FX  = [ [ model.addVar() for i in range( 64 ) ] for j in range(r1 ) ]
        FY  = [ [ model.addVar() for i in range( 64 ) ] for j in range(r1 ) ]

        ActiveC = genConstr( [ [0,0,0,0,1], [1,1,1,1,0] ] )

        A = [ model.addVar() for i in range(16) ]
        for i in range(16):
            model.exclude_set( FX[0][4 * i : 4 * i + 4] + [ A[i] ], ActiveC ) 

        model.SEQSUM( A, 15 )

        SBOXC = genConstr( [ [0,0,0,0, 0,0,0,0], [1,1,1,1, 1,1,1,1] ] )

        LC = genConstr( [ [0, 0, 0, 0], 
               [0, 0, 0, 1], 
               [0, 0, 1, 1], 
               [0, 1, 0, 1], 
               [0, 1, 1, 1], 
               [1, 0, 0, 1], 
               [1, 0, 1, 1], 
               [1, 1, 0, 1], 
               [1, 1, 1, 1], 
              ] )

        for r in range( r0, r0 + r1 ):
            rr = r - r0 
            #print( r, rr )
            # Sbox layer
            for i in range(16):
                #csbox = sbox( partcipher[2*r][i], 4, 4 )
                #constr = csbox.gen_cnf_for_LAT( BIT = 4 )
                L = []
                L += FX[rr][4*i: 4*i+4]
                L += FY[rr][4*i: 4*i+4]

                #print( L, SBOXC )
                model.exclude_set( L, SBOXC )

            if r < r0 + r1 - 1:
                GF2 = galois.GF(2)
                M = GF2( partcipher[2 * r + 1], dtype = int )

                for i in range(64):
                    L = []
                    for j in range(64):
                        if M[i][j] == 1:
                            L.append( FY[rr][j] )
                    L.append( FX[rr + 1][i] )
                    model.exclude_set( L, LC )

        model.exclude_vector( FX[0], [ 0 for i in range(64) ] )

        # keyrecovery forward and forward differential
        C = []
        for x in range(16):
            for y in range(16):
                if x == 0 and y == 0:
                    C.append( [ 0, 0, 0, 0, 0, 0, 0, 0 ] )
                elif x > 0 and y == 0xf:
                    C.append( [ x >> 3 & 0x1, x >> 2 & 1, x >> 1 & 1, x >> 0 & 1, 1, 1, 1, 1 ] )
        Cconstr = genConstr( C )

        for i in range(16):
            model.exclude_set( X[r0][ 4 * i: 4 * i + 4 ] + FX[0][ 4 * i: 4 * i + 4 ], Cconstr )
        

        # backward
        BX  = [ [ model.addVar() for i in range( 64 ) ] for j in range( r1 ) ]
        BY  = [ [ model.addVar() for i in range( 64 ) ] for j in range( r1 ) ]

        for r in range( r0 + r1 - 1, r0 - 1, -1 ):
            rr = r - r0
            # Sbox layer
            for i in range(16):
                L = []
                L += BY[rr][4*i: 4*i+4]
                L += BX[rr][4*i: 4*i+4]
                model.exclude_set( L, SBOXC )

            if r > r0:
                GF2 = galois.GF(2)
                M = np.linalg.inv( GF2( partcipher[2 * r + 1], dtype = int ) )

                for i in range(64):
                    L = []
                    for j in range(64):
                        if M[i][j] == 1:
                            L.append( BX[rr][j] )
                    L.append( BY[rr-1][i] )
                    model.exclude_set( L, LC )

        model.exclude_vector( BY[r1 -1], [0 for i in range(64) ] )

        for i in range(16):
            model.exclude_set( Z[0][ 4 * i : 4 * i + 4 ] + BY[r1 - 1][ 4 * i: 4 * i + 4 ], Cconstr )

        ZX  = [ [ model.addVar() for i in range( 64 ) ] for j in range( r1 ) ]
        ZC = genConstr( [ [1,1,1], 
                          [0,0,0], 
                          [0,1,0], 
                          [1,0,0], 
                          ] )

        for r in range( r1 ):
            for i in range(64):
                L = [ FX[r][i], BX[r][i], ZX[r][i] ]
                model.exclude_set( L, ZC )

        L = []
        for r in range( 0, r1 ):
            for i in range(64):
                L.append( ZX[r][i] )

        model.SEQSUM( L, obj1 )

        L = []
        for r in range( 0, r0 ):
            for i in range(64):
                L.append( X[r][i] )

        for r in range( r2, 0, -1 ):
            for i in range(64):
                L.append( Z[r][i] )

        model.SEQSUM( L, obj2 )

        # run the model
        flag, resdict = model.solve( seed = seed, time = time, delete = True )

        #print( resdict )

        if flag == 1:
            for r in range( r1 ):
                for i in range( 64 ):
                    ZX[r][i] = resdict[ ZX[r][i] ]
                    FX[r][i] = resdict[ FX[r][i] ]
                    BX[r][i] = resdict[ BX[r][i] ]

            for r in range( r0 + 1 ):
                for i in range( 64 ):
                    X[r][i] = resdict[ X[r][i] ]
                    if r < r0:
                        Y[r][i] = resdict[ Y[r][i] ]

            for r in range( r2 + 1 ):
                for i in range( 64 ):
                    Z[r][i] = resdict[ Z[r][i] ]
                    if r < r2:
                        W[r][i] = resdict[ W[r][i] ]

            mpath = MITMPathKey( X, Y, ZX, Z, W, r0, r1, r2 )

            return mpath

        elif flag == -1:
            return -1
        else:
            return 0

if __name__ == '__main__':
    pass




        
