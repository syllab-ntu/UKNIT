'''
this file is for producing the basic tables and constraints for Sbox
'''
import os
import sys

if __name__ == '__main__' and __package__ in (None, ''):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    __package__ = 'myutility'

from .searchmode import searchmode
from math import log
from .espresso import genConstr

class sbox ():
    def __init__(self, sbox, row, col):
        self._sbox = sbox
        self._row = row
        self._col = col

        self._invSbox = self.genInvSbox( sbox ) 

    def genInvSbox( self, sbox ):
        SboxInv = [0] * 16
        for i in range(16):
            SboxInv[ sbox[i] ] = i
        return SboxInv

    def dot( self, x, y, size = 4 ):
        z = x & y 
        res = 0
        for i in range(size):
            res ^= z >> ( size - 1 - i ) & 0x1
        return res

    def wt( self, x, size = 4 ):
        res = 0
        for i in range(4):
            res += x >> i & 0x1
        return res

    def mul( self, x, y, size = 4 ):
        if self.wt( x & y ) == self.wt( x ):
            return 1
        else:
            return 0

    def genLAT(self):
        '''
        #0 - #1 / 2^n
        2 * ( #0 / 2^n ) - 1 = #0 / 2^{n-1} - 1 = #0 - 2^{n-1} / 2^{n-1} = #0 - (2^n - )
        '''

        table = [ [ 0  for i in range(2**self._col) ] for j in range(2 ** self._row) ]  
        for maskin in range(2 ** self._row):
            for maskout in range(2**self._col):
                for x in range(2**self._row):
                    if self.dot( maskin, x ) == self.dot( maskout, self._sbox[x] ):
                        table[maskin][maskout] += 1
                    else:
                        table[maskin][maskout] -= 1
        return table

    def genChi2Delta(self):
        table = [ [ 0  for i in range(2**self._col) ] for j in range(2 ** self._row) ]  
        for maskin in range(2 ** self._row):
            for diff in range(2**self._col):
                for x in range(2**self._row):
                    for y in range(2**self._row):
                        if self._sbox[x] ^ self._sbox[y] == diff:
                            if self.dot( maskin, x ^ y ) == 0:
                                table[maskin][diff] += 1
                            else:
                                table[maskin][diff] -= 1
        return table

    def genDDT(self):
        table = [ [ 0 for i in range(2**self._row) ] for j in range(2**self._col) ]
        for xorin in range(2**self._row):
            for x in range(2**self._row):
                table[ xorin ] [ self._sbox[x] ^ self._sbox[x ^ xorin] ] += 1

        return table

    def Moebius(self, X ):
        for i in range( 0, 4 ):
            Sz = 2**i
            Pos = 0
            while Pos < 16:
                for j in range(0, Sz):
                    X[ Pos + Sz + j ] = X[ Pos + j] ^ X[ Pos + j + Sz ]
                Pos = Pos + 2 * Sz

    def genMPT(self):
        T = [ [0 for i in range(16) ] for j in range(16) ] 
        T[0][0] = 1
        for v in range(1, 16):
            X = []
            for x in range(16):
                X.append( self.mul( v, self._sbox[x] ) )
            self.Moebius( X )
            for u in range(16):
                if X[u] == 1:
                    T[u][v] = 1 
        return T

    def genBCT(self):
        T = [ [0 for i in range(16) ] for j in range(16) ] 

        for u in range(0, 16):
            for v in range(0, 16):
                for x in range(16):
                    if self._invSbox[ self._sbox[x] ^ v ] ^ self._invSbox[ self._sbox[x ^ u] ^v ] == u:
                        T[u][v] += 1
        return T

    def genDLCT(self):
        T = [ [0 for i in range(16) ] for j in range(16) ] 

        for d in range(0, 16):
            for u in range(0, 16):
                for x in range(16):
                    if self.dot ( u, self._sbox[x] ^ self._sbox[ x ^ d ] ) == 0:
                        T[d][u] += 1
                    else:
                        T[d][u] -= 1
        return T

    def gen_cnf_for_BCT( self, BIT = 4, mode = searchmode.designer ):
        # pro = 0, pro = -1, pro = -2 
        # in a total, 4 + 4 + 2 bits
        if BIT == 4:
            table = self.genBCT()
            V = []
            for i in range( 2 ** self._row ):
                B0 = self.int_2_bin( i, self._row )
                for j in range(2 ** self._col):
                    B1 = self.int_2_bin( j, self._col )
                    B = []
                    if abs( table[i][j] ) == 2: # 2 / 16 = 2^-3
                        # pro = 3
                        B += B0 + B1 + [1, 1, 1]
                    elif abs( table[i][j] ) == 4: # 4 / 16 = 2 ^-2
                        B += B0 + B1 + [0, 1, 1]
                    elif abs( table[i][j] ) == 6: 
                        if mode == searchmode.designer:
                            B += B0 + B1 + [0, 0, 1]
                        else:
                            B += B0 + B1 + [0, 1, 1]
                    elif abs( table[i][j] ) == 8: # 6 / 16 ~ 2^-1
                        B += B0 + B1 + [0, 0, 1]
                    elif abs( table[i][j] ) == 16:
                        B += B0 + B1 + [0, 0, 0]
                    if len(B) > 0:
                        V.append( B )

            P = genConstr( V )
            return P

    def gen_cnf_for_DLCT( self, BIT = 4, mode = searchmode.designer ):
        # pro = 0, pro = -1, pro = -2 
        # in a total, 4 + 4 + 2 bits
        if BIT == 4:
            table = self.genDLCT()
            V = []
            for i in range( 2 ** self._row ):
                B0 = self.int_2_bin( i, self._row )
                for j in range(2 ** self._col):
                    B1 = self.int_2_bin( j, self._col )
                    B = []
                    if abs( table[i][j] ) == 2: # 2 / 16 = 2^-3
                        # pro = 3
                        B += B0 + B1 + [1, 1, 1]
                    elif abs( table[i][j] ) == 4: # 4 / 16 = 2 ^-2
                        B += B0 + B1 + [0, 1, 1]
                    elif abs( table[i][j] ) == 6: 
                        if mode == searchmode.designer:
                            B += B0 + B1 + [0, 0, 1]
                        else:
                            B += B0 + B1 + [0, 1, 1]
                    elif abs( table[i][j] ) == 8: # 6 / 16 ~ 2^-1
                        B += B0 + B1 + [0, 0, 1]
                    elif abs( table[i][j] ) == 16:
                        B += B0 + B1 + [0, 0, 0]
                    elif abs( table[i][j] ) == 0:
                        pass
                    else:
                        raise Exception( "Value Error", table[i][j] )
                    if len(B) > 0:
                        V.append( B )

            P = genConstr( V )
            return P

    def print2DTable(self, table, row, col):
        print( '\t', end = '' )
        for i in range(2**col):
            print( '%2x\t' % i, end ='' )
        print()

        for i in range(2**row):
            print( '%2x\t' % i, end = '' )
            for j in range(2**col):
                print( '%2d\t'  % table[i][j], end = '' )
            print()

    def int_2_bin( self, x, num ):
        X = []
        for i in range(num):
            X.append( x >> ( num -1 - i ) & 0x1 )
        return X

    def gen_cnf_for_DDT( self, BIT = 4, mode = searchmode.designer ):
        # pro = 0, pro = -1, pro = -2 
        # in a total, 4 + 4 + 2 bits
        if BIT == 4:
            table = self.genDDT()
            V = []
            for i in range( 2 ** self._row ):
                B0 = self.int_2_bin( i, self._row )
                for j in range(2 ** self._col):
                    B1 = self.int_2_bin( j, self._col )
                    B = []
                    if abs( table[i][j] ) == 2: # 2 / 16 = 2^-3
                        # pro = 3
                        B += B0 + B1 + [1, 1, 1]
                    elif abs( table[i][j] ) == 4: # 4 / 16 = 2 ^-2
                        B += B0 + B1 + [0, 1, 1]
                    elif abs( table[i][j] ) == 6: 
                        if mode == searchmode.designer:
                            B += B0 + B1 + [0, 0, 1]
                        else:
                            B += B0 + B1 + [0, 1, 1]
                    elif abs( table[i][j] ) == 8: # 6 / 16 ~ 2^-1
                        B += B0 + B1 + [0, 0, 1]
                    elif abs( table[i][j] ) == 16:
                        B += B0 + B1 + [0, 0, 0]
                    if len(B) > 0:
                        V.append( B )

            P = genConstr( V )
            return P

    def gen_cnf_for_DDT_withoutP( self, BIT = 4 ):
        # pro = 0, pro = -1, pro = -2 
        # in a total, 4 + 4 + 2 bits
        if BIT == 4:
            table = self.genDDT()
            V = []
            for i in range( 2 ** self._row ):
                B0 = self.int_2_bin( i, self._row )
                for j in range(2 ** self._col):
                    B1 = self.int_2_bin( j, self._col )
                    B = []
                    if abs( table[i][j] ) > 0: # 2 / 16 = 2^-3
                        B += B0 + B1
                    if len(B) > 0:
                        V.append( B )

            P = genConstr( V )
            return P


    def gen_cnf_for_LAT( self, BIT = 4, mode = searchmode.designer ):
        # pro = 0, pro = -1, pro = -2 
        # in a total, 4 + 4 + 2 bits
        if BIT == 4:
            table = self.genLAT()
            V = []
            for i in range( 2 ** self._row ):
                B0 = self.int_2_bin( i, self._row )
                for j in range(2 ** self._col):
                    B1 = self.int_2_bin( j, self._col )
                    B = []
                    if abs( table[i][j] ) == 4: # 2 / 16 = 2^-3
                        # pro = 3
                        B += B0 + B1 + [1, 1]
                    elif abs( table[i][j] ) == 8: # 4 / 16 = 2 ^-2
                        B += B0 + B1 + [0, 1]
                    elif abs( table[i][j] ) == 16:
                        B += B0 + B1 + [0, 0]
                    if len(B) > 0:
                        V.append( B )

            P = genConstr( V )
            return P

    def gen_cnf_for_LAT_withoutC( self, BIT = 4, mode = searchmode.designer ):
        # without C
        # pro = 0, pro = -1, pro = -2 
        # in a total, 4 + 4 + 2 bits
        if BIT == 4:
            table = self.genLAT()
            V = []
            for i in range( 2 ** self._row ):
                B0 = self.int_2_bin( i, self._row )
                for j in range(2 ** self._col):
                    B1 = self.int_2_bin( j, self._col )
                    B = []
                    if abs( table[i][j] ) > 0: # 2 / 16 = 2^-3
                        # pro = 3
                        B += B0 + B1
                    if len(B) > 0:
                        V.append( B )

            P = genConstr( V )
            return P

    def gen_cnf_for_MPT( self, BIT = 4 ):
        # pro = 0, pro = -1, pro = -2 
        # in a total, 4 + 4 + 2 bits
        if BIT == 4:
            table = self.genMPT()
            V = []
            for i in range( 2 ** self._row ):
                B0 = self.int_2_bin( i, self._row )
                for j in range(2 ** self._col):
                    B1 = self.int_2_bin( j, self._col )
                    B = []
                    if table[i][j] == 1: # 2 / 16 = 2^-3
                        B = B0 + B1
                    #print( B )
                    if len(B) > 0:
                        V.append( B )
            P = genConstr( V )
            return P

    def gen_cnf_for_Chi2Delta( self, BIT = 4 ):
        # pro = 0, pro = -1, pro = -2 
        # in a total, 4 + 4 + 2 bits
        S = set()
        if BIT == 4:
            table = self.genChi2Delta()
            V = []
            for i in range( 2 ** self._row ):
                B0 = self.int_2_bin( i, self._row )
                for j in range(2 ** self._col):
                    B1 = self.int_2_bin( j, self._col )

                    #print( table[i][j] )
                    S.add( table[i][j] )

                    print( table[i][j] )

            #P = genConstr( V )
            #return P
            return S

if __name__ == '__main__':
    print( 'myutility.sbox is a helper module; import sbox with an explicit S-box table.' )
