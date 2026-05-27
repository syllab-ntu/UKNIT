import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from uknit_bc import UKNITBC
import numpy as np
import galois as gl

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

def printState( s, x = 0, y = 0, latex = False, color = 'white', value = True ):
    if latex == False:
        print( f'{s[0]:x} {s[4]:x} {s[8]:x} {s[12]:x}' )
        print( f'{s[1]:x} {s[5]:x} {s[9]:x} {s[13]:x}' )
        print( f'{s[2]:x} {s[6]:x} {s[10]:x} {s[14]:x}' )
        print( f'{s[3]:x} {s[7]:x} {s[11]:x} {s[15]:x}' )
    else:
        for i in range(16):
            if s[i] == 0:
                pass
            else:
                print( rf'\fill[{color}] ({x+i//4},{y + 3 - i % 4}) rectangle  ++(1,1);' )
                if value:
                    print( rf'\node at ( {x + i // 4 + 0.5}, {y} + {3 - i % 4 + 0.5 } ) {{ \small \tt \textcolor{{white}} {{{s[i]:x}}} }};' )
                #print( rf'\{\small \tt \textcolor\{white}\{ {s[i]} \} \};' )

def Linear( M, Pattern ):
    A = [0] * 16
    test = 0
    while test < 1000:
        x = [0] * 16
        for i in range(16):
            if Pattern[i] == 1:
                x[i] = np.random.randint(0, 15)
        
        xx = GF16to2( x[::-1] )
        yy = M.dot( GF2(xx) )
        y = GF2to16( yy.tolist() )[::-1]

        for i in range(16):
            if y[i] != 0:
                A[i] = 1
        test+=1
    return A

if __name__ == '__main__':
    cipher = UKNITBC()
    matrix = cipher.matrix( 1 )
    GF2 = gl.GF( 2 )
    M = GF2( matrix )
    Minv = np.linalg.inv( M )

    #pattern = [1, 0, 1, 1, 0, 0,0,0, 1, 0, 1, 1, 1, 0, 1, 1]
    #pattern = [0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0]

    x = [0,0,0,0xa,0,0,0,0,0,0,0,2,0,0,0,0x2]
    #x = [0,1,0,0,0,0,0,0,0,0,0,8,0,0,1,0]

    x = x[::-1]

    xx = GF16to2( x )

    print ( 'xx', xx )

    y = Minv.dot( GF2( xx ) )

    yy = GF2to16( y.tolist() )[::-1]

    printState( yy )
    #yy = GF2to16( y )
    #print( yy )

    #y = Linear( M, pattern )
    #print( y )

    #print( x )
    #printState( x )
    #printState( x, 18, -8, latex = True, color = 'DarkOrchid', value = True )
    #printState( y, 6, -8, latex = True, color = 'DarkOrchid', value = False )
    # printState( x, latex = Fal, color = 'DodgerBlue' )

    #print( GF2to16( M.dot(xx) ) )
