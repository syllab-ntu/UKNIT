import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import LATEX

class path:
    def __init__(self, roundx, X, Y, P0, P1, P2 ):
        self.roundx = roundx
        self.X = X
        self.Y = Y
        self.P0 = P0
        self.P1 = P1
        self.P2 = P2

    def printPath( self, f = sys.stdout, latex = False ):
        if latex == False:
            PP = 0
            for r in range( self.roundx ):
                S = []
                for i in range(16):
                    S.append( ( self.X[r][4 * i] << 3 ) ^ ( self.X[r][4*i+1] << 2) ^ ( self.X[r][4*i+2] << 1)^ self.X[r][4*i+3]  )
                print( "R%2d" % r, end = '\t', file = f )
                for i in range(16):
                    print( '%x ' % S[i], end = '', file = f )
                P = 0
                for i in range(16):
                    P += self.P0[r][i] + self.P1[r][i] + self.P2[r][i]
                PP += P
                print( "\t %d" % P, end = '\t', file = f )
                print( file = f)
                S = []
                for i in range(16):
                    S.append( ( self.Y[r][4 * i] << 3 ) ^ ( self.Y[r][4*i+1] << 2) ^ ( self.Y[r][4*i+2] << 1)^ self.Y[r][4*i+3]  )
                print( "   ",  end = '\t', file = f )
                for i in range(16):
                    print( '%x ' % S[i], end = '', file = f )
                print( file = f)
            print( "Pro = ", PP, file = f)
            return PP
        else:
            PP = 0
            for r in range( self.roundx ):
                S = []
                for i in range(16):
                    S.append( ( self.X[r][4 * i] << 3 ) ^ ( self.X[r][4*i+1] << 2) ^ ( self.X[r][4*i+2] << 1)^ self.X[r][4*i+3]  )
                print( r, end = r' & ', file = f )
                for i in range(16):
                    if S[i] == 0:
                        print( r'\textcolor{lightgray}{\tt{%x}}' % S[i], end = '', file = f )
                    else:
                        print( r'\tt{%x}' % S[i], end = '', file = f )
                #---------------------------------------
                P = 0
                for i in range(16):
                    P += self.P0[r][i] + self.P1[r][i] + self.P2[r][i]
                PP += P
                print( r"& %d" % P, end = r' \\ ', file = f )
                print( file = f)
                #---------------------------------------
                S = []
                for i in range(16):
                    S.append( ( self.Y[r][4 * i] << 3 ) ^ ( self.Y[r][4*i+1] << 2) ^ ( self.Y[r][4*i+2] << 1)^ self.Y[r][4*i+3]  )
                print( "   ",  end = r' & ', file = f )
                for i in range(16):
                    if S[i] == 0:
                        print( r'\textcolor{lightgray}{\tt{%x}}' % S[i], end = '', file = f )
                    else:
                        print( r'\tt{%x}'  % S[i], end = '', file = f )
                print( r"&  ", end = r' \\ ', file = f )
                print( file = f )
            print( r'\hline ', file = f)
            print( r' & & %d \\ ' % PP, file = f )
            print( file = f)
                #print( file = f)
            return PP

class relatedkeypathW:
    def __init__( self, roundx, X, Y, K0, K1 ):
        self.roundx = roundx
        self.X = X
        self.Y = Y
        self.K0 = K0
        self.K1 = K1

    def printRelatedKeyPath( self ):
        for r in range( self.roundx ):
            S = []
            for i in range(16):
                S.append( self.X[r][i]  )

            print( "R%2d" % r, end = '\t' )
            for i in range(16):
                print( '%x ' % S[i], end = '' )

            print( '\t', end = '' )

            S = []
            for i in range(16):
                S.append( self.K0[r][i] )

            print( "R%2d" % r, end = '\t' )
            for i in range(16):
                print( '%x ' % S[i], end = '' )

            print( '\t', end = '' )

            S = []
            for i in range(16):
                S.append( self.K1[r][i]  )

            print( "R%2d" % r, end = '\t' )
            for i in range(16):
                print( '%x ' % S[i], end = '' )

            print()
            S = []
            for i in range(16):
                S.append( self.Y[r][i]  )

            print( "   ",  end = '\t' )
            for i in range(16):
                print( '%x ' % S[i], end = '' )
            print()

            print()

class relatedkeypathB:
    def __init__( self, roundx, X, Y, Z, K0, K1, RK, P0, P1, P2 ):
        self.roundx = roundx
        self.X = X
        self.Y = Y
        self.Z = Z
        self.K0 = K0
        self.K1 = K1
        self.RK = RK
        self.P0 = P0
        self.P1 = P1
        self.P2 = P2

    def printRelatedKeyPath( self ):
        for r in range( self.roundx ):
            S = []
            for i in range(16):
                S.append( ( self.X[r][4 * i] << 3 ) ^ ( self.X[r][4*i+1] << 2) ^ ( self.X[r][4*i+2] << 1)^ self.X[r][4*i+3]  )

            print( "R%2d" % r, end = '\t' )
            for i in range(16):
                print( '%x ' % S[i], end = '' )

            print( end = '\t' )
            for i in range(16):
                print( '%x ' % self.K0[r][i], end = '' )

            print( end = '\t' )
            for i in range(16):
                print( '%x ' % self.K1[r][i], end = '' )

            print( end = '\t' )
            for i in range(16):
                print( '%x ' % self.RK[r][i], end = '' )

            print()

            S = []
            for i in range(16):
                S.append( ( self.Y[r][4 * i] << 3 ) ^ ( self.Y[r][4*i+1] << 2) ^ ( self.Y[r][4*i+2] << 1)^ self.Y[r][4*i+3]  )

            print( "   ",  end = '\t' )
            for i in range(16):
                print( '%x ' % S[i], end = '' )
            print( end = '\t' )

            P = 0
            for i in range(16):
                P += self.P0[r][i] * 4 + self.P1[r][i] * 2 + self.P2[r][i]
            print( "\t %d" % P, end = '\t' )
            print()

            S = []
            for i in range(16):
                S.append( ( self.Z[r][4 * i] << 3 ) ^ ( self.Z[r][4*i+1] << 2) ^ ( self.Z[r][4*i+2] << 1)^ self.Z[r][4*i+3]  )
            print( "   ",  end = '\t' )
            for i in range(16):
                print( '%x ' % S[i], end = '' )
            print()

            print()

class relatedkeypathFullBit2P:
    def __init__( self, roundx, X, Y, Z, K0, K1, P0, P1, P2 ):
        self.roundx = roundx
        self.X = X
        self.Y = Y
        self.Z = Z
        self.K0 = K0
        self.K1 = K1
        self.P0 = P0
        self.P1 = P1
        self.P2 = P2

    def printRelatedKeyPath( self, f = sys.stdout ):
        for r in range( self.roundx ):
            S = []
            for i in range(16):
                S.append( ( self.X[r][4 * i] << 3 ) ^ ( self.X[r][4*i+1] << 2) ^ ( self.X[r][4*i+2] << 1)^ self.X[r][4*i+3]  )

            print( "R%2d" % r, end = '\t', file = f )
            for i in range(16):
                print( '%x ' % S[i], end = '', file = f )

            print( end = '\t', file = f )

            S = []
            for i in range(16):
                S.append( ( self.K0[r][4 * i] << 3 ) ^ ( self.K0[r][4*i+1] << 2) ^ ( self.K0[r][4*i+2] << 1)^ self.K0[r][4*i+3]  )

            for i in range(16):
                print( '%x ' % S[i], end = '', file = f )

            print( end = '\t', file = f )

            S = []
            for i in range(16):
                S.append( ( self.K1[r][4 * i] << 3 ) ^ ( self.K1[r][4*i+1] << 2) ^ ( self.K1[r][4*i+2] << 1)^ self.K1[r][4*i+3]  )
            for i in range(16):
                print( '%x ' % S[i], end = '', file = f )

            print( file = f)

            S = []
            for i in range(16):
                S.append( ( self.Y[r][4 * i] << 3 ) ^ ( self.Y[r][4*i+1] << 2) ^ ( self.Y[r][4*i+2] << 1)^ self.Y[r][4*i+3]  )

            print( "   ",  end = '\t', file = f )
            for i in range(16):
                print( '%x ' % S[i], end = '', file = f )
            print( end = '\t', file = f )

            P = 0
            for i in range(16):
                P += self.P0[r][i] + self.P1[r][i] + self.P2[r][i]
            print( "\t %d" % P, end = '\t', file = f )
            print( file = f)

            S = []
            for i in range(16):
                S.append( ( self.Z[r][4 * i] << 3 ) ^ ( self.Z[r][4*i+1] << 2) ^ ( self.Z[r][4*i+2] << 1)^ self.Z[r][4*i+3]  )
            print( "   ",  end = '\t', file = f )
            for i in range(16):
                print( '%x ' % S[i], end = '', file = f )
            print( file = f)

            print( file = f)


class linear_path:
    def __init__(self, roundx, X, Y, P0, P1 ):
        self.roundx = roundx
        self.X = X
        self.Y = Y
        self.P0 = P0
        self.P1 = P1

    def printPath( self, f = sys.stdout, latex = False ):
        if latex == False:
            PP = 0
            for r in range( self.roundx ):
                S = []
                for i in range(16):
                    S.append( ( self.X[r][4 * i] << 3 ) ^ ( self.X[r][4*i+1] << 2) ^ ( self.X[r][4*i+2] << 1)^ self.X[r][4*i+3]  )
                print( "R%2d" % r, end = '\t', file = f )
                for i in range(16):
                    print( '%x ' % S[i], end = '', file = f )
                P = 0
                for i in range(16):
                    P += self.P0[r][i] + self.P1[r][i] 
                PP += P
                print( "\t %d" % P, end = '\t', file = f )
                print( file = f)
                S = []
                for i in range(16):
                    S.append( ( self.Y[r][4 * i] << 3 ) ^ ( self.Y[r][4*i+1] << 2) ^ ( self.Y[r][4*i+2] << 1)^ self.Y[r][4*i+3]  )
                print( "   ",  end = '\t', file = f )
                for i in range(16):
                    print( '%x ' % S[i], end = '', file = f )
                print( file = f)
                print( file = f)
            return PP
        else:
            PP = 0
            for r in range( self.roundx ):
                S = []
                for i in range(16):
                    S.append( ( self.X[r][4 * i] << 3 ) ^ ( self.X[r][4*i+1] << 2) ^ ( self.X[r][4*i+2] << 1)^ self.X[r][4*i+3]  )
                print( r, end = r' & ', file = f )
                for i in range(16):
                    if S[i] == 0:
                        print( r'\textcolor{lightgray}{%x} ' % S[i], end = '', file = f )
                    else:
                        print( '%x ' % S[i], end = '', file = f )
                P = 0
                for i in range(16):
                    P += self.P0[r][i] + self.P1[r][i] 
                PP += P
                print( r"& %d" % P, end = r' \\ ', file = f )
                print( file = f)
                S = []
                for i in range(16):
                    S.append( ( self.Y[r][4 * i] << 3 ) ^ ( self.Y[r][4*i+1] << 2) ^ ( self.Y[r][4*i+2] << 1)^ self.Y[r][4*i+3]  )
                print( "   ",  end = r' & ', file = f )
                for i in range(16):
                    if S[i] == 0:
                        print( r'\textcolor{lightgray}{%x} ' % S[i], end = '', file = f )
                    else:
                        print( '%x ' % S[i], end = '', file = f )
                print( r"&  ", end = r' \\ ', file = f )
                print( file = f)
                #print( file = f)
            return PP

class keyrecoverypath:
    def __init__( self, r0, r1, r2, X, Y, P0, P1, 
                 P2 = [ [0 for i in range(64)] for j in range(12)] )  :
        self.X = X
        self.Y = Y
        self.P0 = P0
        self.P1 = P1
        self.P2 = P2
        self.r0 = r0
        self.r1 = r1
        self.r2 = r2

    def printPath( self, f = sys.stdout, latex = False ):
        if latex == False:
            PP = 0
            for r in range( self.r0 + self.r1 + self.r2 ):
                #print( r, self.X[r] )
                S = []
                for i in range(16):
                    S.append( ( self.X[r][4 * i] << 3 ) ^ ( self.X[r][4*i+1] << 2) ^ ( self.X[r][4*i+2] << 1) ^ self.X[r][4*i+3]  )

                print( "R%2d" % r, end = '\t', file = f )
                for i in range(16):
                    print( '%x ' % S[i], end = '', file = f )
                #print( file = f )
                if self.r0 <= r < self.r0 + self.r1:
                    P = 0
                    for i in range(16):
                        P += self.P0[r - self.r0][i] + self.P1[r - self.r0][i] + self.P2[r - self.r0][i]
                    PP += P
                    print( "\t %d" % P, end = '\t', file = f )
                    print( file = f)
                else:
                    print( file = f )

                S = []
                for i in range(16):
                    S.append( ( self.Y[r][4 * i] << 3 ) ^ ( self.Y[r][4*i+1] << 2) ^ ( self.Y[r][4*i+2] << 1)^ self.Y[r][4*i+3]  )
                print( "   ",  end = '\t', file = f )
                for i in range(16):
                    print( '%x ' % S[i], end = '', file = f )
                print( file = f)
            print( "Pro = ", PP, file = f)
            return PP
        else:
            PP = 0
            for r in range( self.r0 + self.r1 + self.r2 ):
                S = []
                for i in range(16):
                    S.append( ( self.X[r][4 * i] << 3 ) ^ ( self.X[r][4*i+1] << 2) ^ ( self.X[r][4*i+2] << 1)^ self.X[r][4*i+3]  )
                print( r, end = r' & ', file = f )
                for i in range(16):
                    if S[i] == 0:
                        print( r'\textcolor{lightgray}{\tt{%x}}' % S[i], end = '', file = f )
                    else:
                        print( r'\tt{%x}' % S[i], end = '', file = f )
                
                if self.r0 <= r < self.r0 + self.r1:
                    P = 0
                    for i in range(16):
                        P += self.P0[r - self.r0][i] + self.P1[r - self.r0][i] + self.P2[r - self.r0][i]
                    PP += P
                    print( r"& %d" % P, end = r' \\ ', file = f )
                    print( file = f)
                else:
                    print( r"& ", end = r' \\ ', file = f )
                    print( file = f)

                S = []
                for i in range(16):
                    S.append( ( self.Y[r][4 * i] << 3 ) ^ ( self.Y[r][4*i+1] << 2) ^ ( self.Y[r][4*i+2] << 1)^ self.Y[r][4*i+3]  )
                print( "   ",  end = r' & ', file = f )
                for i in range(16):
                    if S[i] == 0:
                        print( r'\textcolor{lightgray}{\tt{%x}}' % S[i], end = '', file = f )
                    else:
                        print( r'\tt{%x}' % S[i], end = '', file = f )
                print( r"&  ", end = r' \\ ', file = f )
                print( file = f )
            print( r'\hline')
            print( r' & & %d \\ ' % PP )
            print( file = f)

            return PP

    def printAttackFigure( self, r0, r1, r2, file = sys.stdout ):
        latex = LATEX.latex()

        for r in range( r0 ):
            C = [ None for i in range(16) ]

            print( self.X[r] )
            for i in range(16):
                
                if self.X[r][i] != 0:
                    C[i] = 'DodgerBlue'
            latex.rectangleGuess( (18 * r, 0), self.X[r], C, name = r'$X_{%d}$' % r )
            latex.rectangleKey( (18 * r + 3, 5), self.X[r], name = r'$K_{%d}$' % r )
            latex.rectangleGuess( (18 * r + 6, 0), self.X[r], C, name = r"$X'_{%d}$" % r  )
            latex.line( (18 * r + 10, 2), '++(2,0)', arrowtype="-latex", node = r'node[above]{$S$}' )

            latex.xor( (18 * r + 5, 2), '(xor1_%d)' % r )
            latex.line( '(xor1_%d)' % r, '++(1,0)' )
            latex.line( '(xor1_%d)' % r, '++(-1,0)' )
            latex.line( (18*r+5, 5), '(xor1_%d)' % r, arrowtype= '-latex' )

            if r == r0 - 1:
                for i in range(16):
                    if self.Y[r][i] != 0:
                        C[i] = 'Navy'
                latex.rectangle( (18 * r + 12, 0), self.Y[r], C, name = r'$Y_{%d}$'% r )
                latex.line( (18 * r + 16, 2), '++(2,0)', arrowtype="-latex", node = 'node [above] {$L$}' )
            else:
                C = [ None for i in range(16) ]
                for i in range(16):
                    if self.Y[r][i] != 0:
                        C[i] = 'DodgerBlue'
                latex.rectangleGuess( (18 * r + 12, 0), self.Y[r], C, name = r'$Y_{%d}$' % r )
                latex.line( (18 * r + 16, 2), '++(2,0)', arrowtype="-latex", node = 'node[above]{$L$}' )

        for r in range( r0, r0 + 1 ):
            C = [ None for i in range(16) ]
            for i in range(16):
                if self.X[r][i] != 0:
                    C[i] = 'Navy'
            latex.rectangle( (18 * r, 0),  self.X[r], C )

            P = 0
            for rr in range(r1):
                P += sum ( self.P0[rr] )
                P += sum ( self.P1[rr] )
                P += sum ( self.P2[rr] )

            latex.line( (18 * r + 2, 0), (18 * r +2, -6 ), arrowtype= '-latex', node = r'node[left]{$P_{R = %d} = 2^{-%d}$}' % ( r1, P
                ) )

            C = [ None for i in range(16) ]
            for i in range(16):
                if self.Y[r0 + r1 - 1][i] != 0:
                    C[i] = 'Navy'
            latex.rectangle( (18 * r, -10), self.Y[r0 + r1 - 1], C )
            latex.line( (18 * r, -10 + 2), '++(-2, 0)', arrowtype= '-latex', node = 'node[above]{$L$}') 

            C = [ None for i in range(16) ]
            for i in range(16):
                if self.X[r0 + r1][i] != 0:
                    C[i] = 'Navy'
            latex.rectangle( (18 * r - 18 + 12, -10), self.X[r0 + r1], C, name = r'$X_{%d}$'%(r0+r1) )
            latex.line( (18 * r - 18 + 12, -10 + 2), '++(-2, 0)', arrowtype= '-latex', node = 'node[above]{$S$}') 


        for r in range( r2 ):
            C = [ None for i in range(16) ]
            for i in range(16):
               if self.Y[r0 + r1 + r][i] != 0:
                   C[i] = 'DodgerBlue'
            latex.rectangleGuess( (18 * r0 - 18 * (r+1) + 6, -10),  self.Y[r0 + r1 + r], C, name = r'$Y_{%d}$' % (r0+r1+r) )
            latex.rectangleKey( (18 * r0 - 18 * (r+1) + 3, -5),  self.Y[r0 + r1 + r], name = r"$K'_{%d}$" % (r0+r1+r) )
            latex.rectangleGuess( (18 * r0 - 18 * (r+1) + 0, -10),  self.Y[r0 + r1 + r], C, name =  r"$Y'_{%d}$" % (r0+r1+r) )

            latex.xor( (18 * r0 - 18 * (r+1) + 5, -10 + 2 ), '(xorr2%d)'% r )
            latex.line( '(xorr2%d)'%r, '++(1,0)' )
            latex.line( '(xorr2%d)'%r, '++(-1,0)' )
            latex.line( (18 * r0 - 18 * (r+1) + 5, -5), '(xorr2%d)'%r )

            if r < r2 - 1:
                C = [ None for i in range(16) ]
                for i in range(16):
                    if self.X[r0 + r1 + r + 1][i] != 0:
                        C[i] = 'DodgerBlue'

                latex.rectangleGuess( (18 * r0 - 18 * (r+1) - 6, -10),  self.X[r0 + r1 + r + 1], C, name = r'$X_{%d}$' % (r0+r1+r+1) )
                latex.line( (18 * r0 - 18 * (r+1) - 6, -8 ), '++(-2,0)', arrowtype= '-latex', node = 'node[above]{$S$}' )
                latex.line( (18 * r0 - 18 * (r+1) - 2, -8 ), '++(2,0)', arrowtype= 'latex-',  node = 'node[above]{$L$}' )


        pic = latex.draw( standalone= True )

        print( pic, file = file )

class MITMPath:
    def __init__( self, Z, r ):  
        self.Z = Z
        self.ROUND = r

    def printPath( self, f = sys.stdout, latex = False ):
        if latex == False:
            for r in range( self.ROUND ):
                S = []
                for i in range(16):
                    S.append( ( self.Z[r][4 * i] << 3 ) 
                            ^ ( self.Z[r][4*i+1] << 2 ) 
                            ^ ( self.Z[r][4*i+2] << 1 ) 
                            ^ self.Z[r][4*i+3]  )

                print( "R%2d" % r, end = '\t', file = f )

                for i in range(16):
                    print( '%x ' % S[i], end = '', file = f )
                print( file = f )

    def printAttackFigure( self, r0, r1, r2, file = sys.stdout ):
        latex = LATEX.latex()

        for r in range( r0 ):
            C = [ None for i in range(16) ]

            for i in range(16):
                if self.X[r][i] != 0:
                    C[i] = 'DodgerBlue'

            latex.rectangleGuess( (18 * r, 0), self.X[r], C, name = r'$X_{%d}$' % r )
            latex.rectangleKey( (18 * r + 3, 5), self.X[r], name = r'$K_{%d}$' % r )
            latex.rectangleGuess( (18 * r + 6, 0), self.X[r], C, name = r"$X'_{%d}$" % r  )
            latex.line( (18 * r + 10, 2), '++(2,0)', arrowtype="-latex", node = r'node[above]{$S$}' )

            latex.xor( (18 * r + 5, 2), '(xor1_%d)' % r )
            latex.line( '(xor1_%d)' % r, '++(1,0)' )
            latex.line( '(xor1_%d)' % r, '++(-1,0)' )
            latex.line( (18*r+5, 5), '(xor1_%d)' % r, arrowtype= '-latex' )

            if r == r0 - 1:
                for i in range(16):
                    if self.Y[r][i] != 0:
                        C[i] = 'Navy'
                latex.rectangle( (18 * r + 12, 0), self.Y[r], C, name = r'$Y_{%d}$'% r )
                latex.line( (18 * r + 16, 2), '++(2,0)', arrowtype="-latex", node = 'node [above] {$L$}' )
            else:
                C = [ None for i in range(16) ]
                for i in range(16):
                    if self.Y[r][i] != 0:
                        C[i] = 'DodgerBlue'
                latex.rectangleGuess( (18 * r + 12, 0), self.Y[r], C, name = r'$Y_{%d}$' % r )
                latex.line( (18 * r + 16, 2), '++(2,0)', arrowtype="-latex", node = 'node[above]{$L$}' )

        for r in range( r0, r0 + 1 ):
            C = [ None for i in range(16) ]
            for i in range(16):
                if self.X[r][i] != 0:
                    C[i] = 'Navy'
            latex.rectangle( (18 * r, 0),  self.X[r], C )

            P = 0
            for rr in range(r1):
                P += sum ( self.P0[rr] )
                P += sum ( self.P1[rr] )
                P += sum ( self.P2[rr] )

            latex.line( (18 * r + 2, 0), (18 * r +2, -6 ), arrowtype= '-latex', node = r'node[left]{$P_{R = %d} = 2^{-%d}$}' % ( r1, P
                ) )

            C = [ None for i in range(16) ]
            for i in range(16):
                if self.Y[r0 + r1 - 1][i] != 0:
                    C[i] = 'Navy'
            latex.rectangle( (18 * r, -10), self.Y[r0 + r1 - 1], C )
            latex.line( (18 * r, -10 + 2), '++(-2, 0)', arrowtype= '-latex', node = 'node[above]{$L$}') 

            C = [ None for i in range(16) ]
            for i in range(16):
                if self.X[r0 + r1][i] != 0:
                    C[i] = 'Navy'
            latex.rectangle( (18 * r - 18 + 12, -10), self.X[r0 + r1], C, name = r'$X_{%d}$'%(r0+r1) )
            latex.line( (18 * r - 18 + 12, -10 + 2), '++(-2, 0)', arrowtype= '-latex', node = 'node[above]{$S$}') 


        for r in range( r2 ):
            C = [ None for i in range(16) ]
            for i in range(16):
               if self.Y[r0 + r1 + r][i] != 0:
                   C[i] = 'DodgerBlue'
            latex.rectangleGuess( (18 * r0 - 18 * (r+1) + 6, -10),  self.Y[r0 + r1 + r], C, name = r'$Y_{%d}$' % (r0+r1+r) )
            latex.rectangleKey( (18 * r0 - 18 * (r+1) + 3, -5),  self.Y[r0 + r1 + r], name = r"$K'_{%d}$" % (r0+r1+r) )
            latex.rectangleGuess( (18 * r0 - 18 * (r+1) + 0, -10),  self.Y[r0 + r1 + r], C, name =  r"$Y'_{%d}$" % (r0+r1+r) )

            latex.xor( (18 * r0 - 18 * (r+1) + 5, -10 + 2 ), '(xorr2%d)'% r )
            latex.line( '(xorr2%d)'%r, '++(1,0)' )
            latex.line( '(xorr2%d)'%r, '++(-1,0)' )
            latex.line( (18 * r0 - 18 * (r+1) + 5, -5), '(xorr2%d)'%r )

            if r < r2 - 1:
                C = [ None for i in range(16) ]
                for i in range(16):
                    if self.X[r0 + r1 + r + 1][i] != 0:
                        C[i] = 'DodgerBlue'

                latex.rectangleGuess( (18 * r0 - 18 * (r+1) - 6, -10),  self.X[r0 + r1 + r + 1], C, name = r'$X_{%d}$' % (r0+r1+r+1) )
                latex.line( (18 * r0 - 18 * (r+1) - 6, -8 ), '++(-2,0)', arrowtype= '-latex', node = 'node[above]{$S$}' )
                latex.line( (18 * r0 - 18 * (r+1) - 2, -8 ), '++(2,0)', arrowtype= 'latex-',  node = 'node[above]{$L$}' )


        pic = latex.draw( standalone= True )

        print( pic, file = file )

class MITMPathKey:
    def __init__( self, X, Y, FZ, Z, W, r0, r1, r2 ):  
        self.X = X
        self.Y = Y
        self.FZ = FZ

        self.Z = Z
        self.W = W

        self.r0 = r0
        self.r1 = r1
        self.r2 = r2

    def printPath( self, f = sys.stdout, latex = False ):
        if latex == False:
            for r in range( self.r0 + 1 ):
                S = []
                for i in range( 16 ):
                    S.append( ( self.X[r][4 * i] << 3 ) 
                            ^ ( self.X[r][4*i+1] << 2 ) 
                            ^ ( self.X[r][4*i+2] << 1 ) 
                            ^   self.X[r][4*i+3]  )

                print( "R%2d" % r, end = '\t', file = f )
                for i in range(16):
                    print( '%x ' % S[i], end = '', file = f )
                print( file = f )

                if r < self.r0:
                    S = []
                    for i in range( 16 ):
                        S.append( ( self.Y[r][4 * i] << 3 ) 
                                ^ ( self.Y[r][4*i+1] << 2 ) 
                                ^ ( self.Y[r][4*i+2] << 1 ) 
                                ^   self.Y[r][4*i+3]  )

                    print( "R%2d" % r, end = '\t', file = f )
                    for i in range(16):
                        print( '%x ' % S[i], end = '', file = f )
                    print( file = f )
            print()

            for r in range( self.r1 ):
                S = []
                for i in range(16):
                    S.append( ( self.FZ[r][4 * i] << 3 ) 
                            ^ ( self.FZ[r][4*i+1] << 2 ) 
                            ^ ( self.FZ[r][4*i+2] << 1 ) 
                            ^ self.FZ[r][4*i+3]  )

                print( "R%2d" % ( self.r0 + r ), end = '\t', file = f )

                for i in range(16):
                    print( '%x ' % S[i], end = '', file = f )
                print( file = f )
            
            print()

            for r in range( self.r2 + 1 ):
                S = []
                for i in range( 16 ):
                    S.append( ( self.Z[r][4 * i] << 3 ) 
                            ^ ( self.Z[r][4*i+1] << 2 ) 
                            ^ ( self.Z[r][4*i+2] << 1 ) 
                            ^   self.Z[r][4*i+3]  )

                print( "R%2d" % ( self.r0 + self.r1 + r - 1 ), end = '\t', file = f )
                for i in range(16):
                    print( '%x ' % S[i], end = '', file = f )
                print( file = f )

                if r < self.r2:
                    S = []
                    for i in range( 16 ):
                        S.append( ( self.W[r][4 * i] << 3 ) 
                                ^ ( self.W[r][4*i+1] << 2 ) 
                                ^ ( self.W[r][4*i+2] << 1 ) 
                                ^   self.W[r][4*i+3]  )

                    print( "R%2d" % ( self.r0 + self.r1 + r ), end = '\t', file = f )
                    for i in range(16):
                        print( '%x ' % S[i], end = '', file = f )
                    print( file = f )

    def printAttackFigure( self, r0, r1, r2, file = sys.stdout ):
        latex = LATEX.latex()

        for r in range( r0 ):
            C = [ None for i in range(16) ]
            for i in range(16):
                if self.X[r][i] != 0:
                    C[i] = 'DodgerBlue'
            latex.rectangleGuess( (18 * r, 0), self.X[r], C, name = r'$X_{%d}$' % r )
            latex.rectangleKey( (18 * r + 3, 5), self.X[r], name = r'$K_{%d}$' % r )
            latex.rectangleGuess( (18 * r + 6, 0), self.X[r], C, name = r"$X'_{%d}$" % r  )
            latex.line( (18 * r + 10, 2), '++(2,0)', arrowtype="-latex", node = r'node[above]{$S$}' )

            latex.xor( (18 * r + 5, 2), '(xor1_%d)' % r )
            latex.line( '(xor1_%d)' % r, '++(1,0)' )
            latex.line( '(xor1_%d)' % r, '++(-1,0)' )
            latex.line( (18*r+5, 5), '(xor1_%d)' % r, arrowtype= '-latex' )

            if r == r0 - 1:
                for i in range(16):
                    if self.Y[r][i] != 0:
                        C[i] = 'Navy'
                latex.rectangle( (18 * r + 12, 0), self.Y[r], C, name = r'$Y_{%d}$'% r )
                latex.line( (18 * r + 16, 2), '++(2,0)', arrowtype="-latex", node = 'node [above] {$L$}' )
            else:
                C = [ None for i in range(16) ]
                for i in range(16):
                    if self.Y[r][i] != 0:
                        C[i] = 'DodgerBlue'
                latex.rectangleGuess( (18 * r + 12, 0), self.Y[r], C, name = r'$Y_{%d}$' % r )
                latex.line( (18 * r + 16, 2), '++(2,0)', arrowtype="-latex", node = 'node[above]{$L$}' )

        for rr in range( r0, r0 + 1 ):
            r = rr - r0
            C = [ None for i in range(16) ]
            for i in range(16):
                if self.FZ[r][i] != 0:
                    C[i] = 'Navy'
            latex.rectangle( (18 * r, 0),  self.FZ[r], C )

            #P = 0
            #for rr in range(r1):
            #    P += sum ( self.P0[rr] )
            #    P += sum ( self.P1[rr] )
            #    P += sum ( self.P2[rr] )

            #latex.line( (18 * r + 2, 0), (18 * r +2, -6 ), arrowtype= '-latex', node = r'node[left]{$P_{R = %d} = 2^{-%d}$}' % ( r1, P
            #    ) )

            #C = [ None for i in range(16) ]
            #for i in range(16):
            #    if self.[r0 + r1 - 1][i] != 0:
            #        C[i] = 'Navy'
            #latex.rectangle( (18 * r, -10), self.Y[r0 + r1 - 1], C )
            #latex.line( (18 * r, -10 + 2), '++(-2, 0)', arrowtype= '-latex', node = 'node[above]{$L$}') 

            C = [ None for i in range(16) ]
            for i in range(16):
                if self.FZ[r1 - 1][i] != 0:
                    C[i] = 'Navy'
            latex.rectangle( (18 * r - 18 + 12, -10), self.FZ[r1 - 1], C, name = r'$X_{%d}$'%(r0+r1) )
            latex.line( (18 * r - 18 + 12, -10 + 2), '++(-2, 0)', arrowtype= '-latex', node = 'node[above]{$S$}') 


        for r in range( r2 ):
            C = [ None for i in range(16) ]
            for i in range(16):
               if self.Z[r][i] != 0:
                   C[i] = 'DodgerBlue'
            latex.rectangleGuess( (18 * r0 - 18 * (r+1) + 6, -10),  self.Z[r], C, name = r'$Y_{%d}$' % (r0+r1+r) )
            latex.rectangleKey( (18 * r0 - 18 * (r+1) + 3, -5),  self.Z[r], name = r"$K'_{%d}$" % (r0+r1+r) )
            latex.rectangleGuess( (18 * r0 - 18 * (r+1) + 0, -10),  self.Z[r], C, name =  r"$Y'_{%d}$" % (r0+r1+r) )

            latex.xor( (18 * r0 - 18 * (r+1) + 5, -10 + 2 ), '(xorr2%d)'% r )
            latex.line( '(xorr2%d)'%r, '++(1,0)' )
            latex.line( '(xorr2%d)'%r, '++(-1,0)' )
            latex.line( (18 * r0 - 18 * (r+1) + 5, -5), '(xorr2%d)'%r )

            if r < r2 - 1:
                C = [ None for i in range(16) ]
                for i in range(16):
                    if self.W[r + 1][i] != 0:
                        C[i] = 'DodgerBlue'

                latex.rectangleGuess( (18 * r0 - 18 * (r+1) - 6, -10),  self.W[r + 1], C, name = r'$X_{%d}$' % (r0+r1+r+1) )
                latex.line( (18 * r0 - 18 * (r+1) - 6, -8 ), '++(-2,0)', arrowtype= '-latex', node = 'node[above]{$S$}' )
                latex.line( (18 * r0 - 18 * (r+1) - 2, -8 ), '++(2,0)', arrowtype= 'latex-',  node = 'node[above]{$L$}' )


        pic = latex.draw( standalone= True )

        print( pic, file = file )
