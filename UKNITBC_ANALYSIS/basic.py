from myutility.espresso import *
from fractions import Fraction

def preceq( x, u, N ):
    X = int_2_bit(x, N)
    U = int_2_bit(u, N)

    for i in range(N):
        if X[i] > U[i]:
            return False
    return True

def bin_2_int( X, n ):
    x = 0
    for i in range(n):
        x ^= X[i] << ( n - 1 - i )
    return x
    for i in range(N):
        if X[i] > U[i]:
            return False
    return True

def succeq( x, u, N ):
    X = int_2_bit(x, N)
    U = int_2_bit(u, N)

    for i in range(N):
        if X[i] < U[i]:
            return False
    return True

def dot( x, v, n = 64 ):
    res = 0
    for i in range(n):
        res ^= ( x >> i & 0x1 ) & ( v >> i & 0x1 )
    return res

def hw( x, n = 64 ):
    res = 0

    for i in range(n):
        res += x >> i & 0x1
    return res

def wt( x, n = 64 ):
    res = 0

    for i in range(n):
        res += x >> i & 0x1
    return res

def int_2_bit( x, n ):
    L = []
    for i in range(n):
        L.append( x >> ( n - 1 - i ) & 0x1 )

    return L

def bin_2_int( X, n ):
    x = 0
    for i in range(n):
        x ^= X[i] << ( n - 1 - i )
    return x

def bit_2_int( X, n ):
    x = 0
    for i in range(n):
        x ^= X[i] << ( n - 1 - i )
    return x

def gen_constr_from_mp_table( T, bits = 2 ):
    DIM = len( T )
    C = []
    for u in range( DIM ):
        for v in range( DIM ):
            if bits == 2 :
                B = None
                if abs( T[v][u] ) == 1:
                    B = int_2_bit(v, 4) + int_2_bit( u, 4 ) + [0, 0]
                elif abs( T[v][u] ) == 2:
                    B = int_2_bit(v, 4) + int_2_bit( u, 4 ) + [0, 1]
                elif abs( T[v][u] ) == 4:
                    B = int_2_bit(v, 4) + int_2_bit( u, 4 ) + [1, 1]
                elif abs( T[v][u] ) == 0:
                    pass
                else:
                    print( f'The item has not been considered! -> {T[v][u]} ' )
                    exit( -1 )
                C.append( B )
    return genConstr( C )

def gen_constr_from_linear_table( T, bits = 2 ):
    DIM = len( T )
    C = []
    for u in range( DIM ):
        for v in range( DIM ):
            if bits == 2 :
                B = None
                if abs( T[v][u] ) == 1:
                    B = int_2_bit(v, 4) + int_2_bit( u, 4 ) + [0, 0]
                elif abs( T[v][u] ) == 2:
                    B = int_2_bit(v, 4) + int_2_bit( u, 4 ) + [0, 1]
                elif abs( T[v][u] ) == 4:
                    B = int_2_bit(v, 4) + int_2_bit( u, 4 ) + [1, 1]
                elif abs( T[v][u] ) == 0:
                    pass
                else:
                    print( f'The item has not been considered! -> {T[v][u]} ' )
                    exit( -1 )
                C.append( B )
    return genConstr( C )

def apply_ineq_from_01_( model, X, C ):
    DIM = len( X )
    for c in C:
        #print( c )
        s = 0
        for i in range( DIM ):
            if c[i] == '0':
                s += X[i]
            elif c[i] == '1':
                s += 1 - X[i]
            else:
                pass
        #print( s )
        model.addConstr( s >= 1 )
    return model


def calculate_2_adic_absolute_value(rational):
    """
    Calculate the 2-adic absolute value of a given rational number.

    Parameters:
        rational (Fraction): A rational number in the form of a Fraction object.

    Returns:
        float: The 2-adic absolute value.
    """
    # Convert to a Fraction object if it's not already
    if not isinstance(rational, Fraction):
        rational = Fraction(rational)

    # Handle the zero case
    if rational == 0:
        return 0

    # Decompose numerator and denominator
    numerator = rational.numerator
    denominator = rational.denominator

    # Count the power of 2 dividing the numerator and denominator
    def count_twos(n):
        count = 0
        while n % 2 == 0 and n != 0:
            n //= 2
            count += 1
        return count

    # Total 2-power in numerator minus denominator
    power_of_2 = count_twos(numerator) - count_twos(denominator)

    # 2-adic absolute value is 2^(-power_of_2)
    return 2 ** (-power_of_2)

if __name__ == '__main__':
    # Test cases
    values = [Fraction(1, 2), Fraction(1, 4), Fraction(1, 8), Fraction(0), 1, Fraction(-32, 9)]
    for val in values:
        print(f"2-adic absolute value of {val}: {calculate_2_adic_absolute_value(val)}")



