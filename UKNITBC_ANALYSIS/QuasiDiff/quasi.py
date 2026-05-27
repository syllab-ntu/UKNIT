import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from uknit_bc import UKNITBC
from basic import *
import numpy as np
from myutility.sat import *
from myutility.espresso import *
from gurobipy import *

def gen_quasi_table( model, u, v, pro, sbox, indiff, outdiff ):
    qLAT = np.zeros( (16, 16), dtype = np.float32 )
    for inmask in range(16):
        for outmask in range(16):
            for x in range(16):
                if ( sbox[x] ^ sbox[ x ^ indiff ] ) == outdiff:
                    if dot( inmask, x, 4 ) == dot( outmask, sbox[x], 4 ):
                        qLAT[inmask][outmask] += 1
                    else:
                        qLAT[inmask][outmask]  -= 1
    qLAT /= 16.0

    C = []
    for outx in range( 16 ):
        for inx in range( 16 ):
            if qLAT[outx][inx] != 0:
                #print( indiff, outdiff, outx, inx, qLAT[outx][inx] )
                target = - np.log2( abs( qLAT[outx][inx] ) ) 
                if target == 0:
                    C.append( int_2_bit( outx, 4 ) + int_2_bit( inx, 4 ) + [0,0,0] )
                elif target == 1:
                    C.append( int_2_bit( outx, 4 ) + int_2_bit( inx, 4 ) + [0,0,1] )
                elif target == 2:
                    C.append( int_2_bit( outx, 4 ) + int_2_bit( inx, 4 ) + [0,1,1] )
                elif target == 3:
                    C.append( int_2_bit( outx, 4 ) + int_2_bit( inx, 4 ) + [1,1,1] )
                else:
                    raise Exception( f"No Value Support {target} {outx} {inx} {sbox} " )

    assert len(C) > 0, 'There are no constraint in C'

    CS = genConstr( C )

    #print( v, u , pro )

    apply_ineq_from_01_( model, v + u + pro, CS )

def gen_xor_constr():
    C = []
    for x in range(16):
        X = int_2_bit(x, 4)
        if sum(X) == 0:
            C.append( X )
    return genConstr( C )

def pass_diffusion( model, X, Y, mat, C ):
    # X = M^T Y
    matT = [ [ 0 for i in range(64) ] for j in range(64) ]
    for i in range(64):
        for j in range(64):
            matT[i][j] = mat[j][i] 
    
    for i in range(64):
        L = [ X[i] ]
        for j in range(64):
            if matT[i][j] == 1:
                L.append( Y[j] )
        apply_ineq_from_01_( model, L, C )

def search_quasi( path, start, rdx, Cipher, obj ):
    '''
    search for quasi-differential paths for a given differential
    '''

    xor_constr = gen_xor_constr()

    part_cipher = []
    for i in range( start, start + rdx ):
        S = []
        for j in range(16):
            S.append( Cipher.sbox( i, j ) )
        part_cipher.append( S )
        if i < start + rdx - 1:
            part_cipher.append( Cipher.matrix( i ) )

    model = Model()
    model.setParam( 'PoolSearchMode', 2 )
    model.setParam( 'PoolSolutions', 100 )

    X  = [ [ model.addVar() for i in range( 64 ) ] for j in range( rdx ) ]
    Y  = [ [ model.addVar() for i in range( 64 ) ] for j in range( rdx ) ]
    P0 = [ [ model.addVar() for i in range( 16 ) ] for j in range( rdx ) ]
    P1 = [ [ model.addVar() for i in range( 16 ) ] for j in range( rdx ) ]
    P2 = [ [ model.addVar() for i in range( 16 ) ] for j in range( rdx ) ]

    for r in range( rdx ):
        # Sbox
        for i in range( 16 ):
            #print( path[2*r][i], path[2*r+1][i] )
            try:
                gen_quasi_table( model, 
                Y[r][4*i:4*i+4], X[r][4*i:4*i+4], [ P0[r][i], P1[r][i], P2[r][i] ], 
                part_cipher[2*r][i], path[2*r][i], path[2*r+1][i] )
            except Exception as e:
                print( e, "Exception", len(path), "length of part cipher", len( part_cipher ), 2*r+1, i  )
                exit(0)
        
        # diffusion layer
        if r < rdx - 1:
            pass_diffusion( model, Y[r], X[r+1], part_cipher[ 2 * r + 1 ], xor_constr )
    
    PP = []
    for r in range( rdx ):
        for i in range(16):
            PP.append( P0[r][i] )
            PP.append( P1[r][i] )
            PP.append( P2[r][i] )

    model.setObjective( sum( PP ), GRB.MINIMIZE )

    model.optimize()

    status = model.status

    if status == GRB.OPTIMAL:
        print( model.getObjective().getValue() )

        nsol = model.SolCount

        print( nsol )


            
if __name__ == '__main__':
    uknit_bc = UKNITBC()

    #search_quasi( None, 1, 7, uknit_bc, None )

    x0 = 0x0000be0700000000
    y0 = 0x00007d0e00000000

    x1 = 0x0000000000000070
    y1 = 0x00000000000000a0

    x2 = 0x0004000001000000
    y2 = 0x0004000008000000

    x3 = 0x0000040480200808
    y3 = 0x00000808a0a00802

    x4 = 0x02a4000034040000
    y4 = 0x0444000024040000

    x5 = 0x0000000020400000
    y5 = 0x0000000080200000

    x6 = 0x0000080000000002
    y6 = 0x0000080000000008

    x7 = 0x0004802000082040
    y7 = 0x000c204000028010

    X = [ x0, y0, x1, y1, x2, y2, x3, y3, x4, y4, x5, y5, x6, y6, x7, y7]

    path = []

    for r in range(16):
        x = []
        for i in range(16):
            x.append( X[r] >> (60 - 4 * i) & 0xf )
        path.append( x )

    search_quasi( path, 2, 8, uknit_bc, 10 )





