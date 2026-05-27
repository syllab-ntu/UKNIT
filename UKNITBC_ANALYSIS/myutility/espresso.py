import random, os, re, shutil

def int_2_bin( x, n = 4 ):
    B = []
    for i in range(n):
        B.append( x >> ( n - 1 - i ) & 0x1 )
    return B

def genCompVectors( vec, dim ):
    com = []
    for x in range( 1 << dim ):
        v = int_2_bin( x, dim )
        if v not in vec:
            com.append( v )
    return com

def genConstrFromComp( L, option ):
    if os.path.isdir( 'ESPRESSO/' ) == False:
        os.system( 'mkdir ESPRESSO/')

    index = random.randint(0, 0xffffffffffffffff)
    filename = '%s/e_%s.txt' % ( 'ESPRESSO', str( index ) )

    with open( filename, 'w' ) as f:
        print( '.i %d' % len( L[0] ), file = f )
        print( '.o 1 ', file = f )
        print( '.p %d ' % len( L ), file = f )
        for l in L:
            for ll in l:
                print( ll, end = '', file = f )
            print( ' 1', file = f )

        print( '.e', file = f )

    os.system( 'espresso %s %s > %s.res' % ( option, filename, filename ) )

    L = []

    pattern = re.compile( r'([01-]+) 1' )
    P = []
    with open( '%s.res' % filename, 'r' ) as f:
        lines = f.readlines()
        for line in lines:
            m = re.match( pattern, line )
            if m:
                P.append( list ( m.group( 1 ) ) )

    os.system( 'rm %s' % filename )
    os.system( 'rm %s.res' % filename )
    return P

def genConstr( X, option = '' ):
    #print( [0,0,1,0,0,1,0,0,0,0,1] in X )
    L = genCompVectors( X, len( X[0] ) )
    P = genConstrFromComp( L, option )
    return P

if __name__ == '__main__':
    if shutil.which( 'espresso' ) is None:
        print( 'espresso not found on PATH; import genConstr from analysis scripts or install espresso to run this demo.' )
        raise SystemExit(0)

    X = [ [0,0,0,0] ]
    Y = genCompVectors( X, 4 )
    P = genConstr( Y )
    print( P )
