import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from uknit_bc import UKNITBC
import galois
import numpy as np
from basic import *

F2 = galois.GF(2)

def gen_related_input_bits( M, outvec ):
    '''
    outvec = M * vec
    '''
    invec = M.T.dot( outvec ) 

    print( f'{bit_2_int( invec.tolist(), 64 ):016x}' )

    return invec

def gen_related_input_bits_from_pat( M, outvecpat ):
    '''
    outvec = M * vec
    '''
    res = F2( [ 0 ] * 64 )
    for i in range(16):
        if outvecpat[i] == 1:
            for j in range(4):
                tmp = F2( [ 0 ] * 64 )
                tmp[4*i+j] = 1
                invec = M.T.dot( tmp ) 
                #print( invec )
                res = res | invec

    return res

def gen_pattern( vec ):
    pat = [ 0 ] * 16
    for i in range(16):
        for j in range(4):
            if vec[4*i+j] == 1:
                pat[i] = 1
    return pat

def print_pattern( pat ):
    print( f'{pat[0]} \t {pat[4]} \t {pat[8]} \t {pat[12]} \n', end = '' )
    print( f'{pat[1]} \t {pat[5]} \t {pat[9]} \t {pat[13]} \n', end = '' )
    print( f'{pat[2]} \t {pat[6]} \t {pat[10]} \t {pat[14]} \n', end = '' )
    print( f'{pat[3]} \t {pat[7]} \t {pat[11]} \t {pat[15]} \n', end = '' )

def auto_print_pattern( M, vec ):
    if len(vec) == 16:
        x = gen_related_input_bits_from_pat( M, vec )
        pat = gen_pattern ( x ) 
        print_pattern( pat )

        return pat
    else:
        x = gen_related_input_bits( M, vec )
        pat = gen_pattern ( x ) 
        print_pattern( pat )

        return pat

def gen_key_recovery_pattern_plaintext( start, value ): 
    uknit_bc = UKNITBC()
    M1 = F2( uknit_bc.matrix( start - 1 ) )
    M2 = F2( uknit_bc.matrix( start - 2 ) )

    x2 = F2( int_2_bit ( value, 64 ) )
    print( f"The active sbox in x{start - 1}" )
    x1_pat = auto_print_pattern( M1, x2 )

    print( f"The active sbox in x{start - 2}" )
    x0_pat = auto_print_pattern( M2, x1_pat )

def gen_key_recovery_pattern_ciphertext( start, value ): 
    uknit_bc = UKNITBC()
    M1 = np.linalg.inv( F2( uknit_bc.matrix( start ) ) )
    M2 = np.linalg.inv( F2( uknit_bc.matrix( start + 1 ) ) )

    x2 = F2( int_2_bit ( value, 64 ) )
    print( f"The active sbox in x{start+1}" )
    x1_pat = auto_print_pattern( M1, x2 )

    print( f"The active sbox in x{start+2}" )
    x0_pat = auto_print_pattern( M2, x1_pat )


if __name__ == '__main__':
    uknit_bc = UKNITBC()

    gen_key_recovery_pattern_plaintext(  2,  0x0000480400000000 )


    gen_key_recovery_pattern_ciphertext( 8,  0x000100000400a000 )

