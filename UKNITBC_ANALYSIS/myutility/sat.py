import os, re, random, shutil

class sat: 
    def __init__( self ):
        self._V = 0 # the index of variables
        self._clause = [] # the sets of clause

    def reset( self ):
        '''
        the function that reset the model
        '''
        self._V = 0
        self._clause = []

    def addVar( self ):
        self._V += 1
        return self._V 

    def addClause( self, c ):
        '''
        declare a new variable
        '''
        self._clause.append( c )

    def exclude_vector( self, X, v ):
        '''
        let the value of X cannot be vector V
        '''
        assert len(X) == len(v), 'the lengths of X and v are not equal'
        s = ''
        for i in range( len(X) ):
            if v[i] == '1' or v[i] == 1:
                s += '-%d ' % ( X[i] ) 
            elif v[i] == '0' or v[i] == 0:
                s += '%d ' % ( X[i] ) 
            else:
                pass
        s += '0' 
        self.addClause( s )

    def exclude_set( self, X, V ):
        '''
        let the value of X cannot be vectors in V
        '''
        for v in V:
            self.exclude_vector( X, v )

    def OR1( self, X ):
        s = ' '.join( list( map( str, X ) ) )
        s += ' 0'
        #print( s )
        self.addClause( s )
        
    def XOR( self, X ):
        '''
        add constraints for a ^ b = c 
        '''
        assert len(X) == 3, 'Length of X is wrong' % X
        L = [ [0, 0, 1], [0, 1, 0], [1, 0, 0], [1, 1, 1] ]
        self.exclude_set( X, L )

    def EQ( self, X ):
        assert len(X) == 2, 'Length of X is wrong'
        L = [ [0, 1], [1, 0] ]
        self.exclude_set( X, L )

    def ASSIGN( self, X, v ):
        if v == 0 or v == '0':
            s = '-%d 0' % X
            self.addClause( s )
        elif v == 1 or v == '1':
            s = '%d 0' % X
            self.addClause( s )

    def XOR3 ( self, X ):
        assert len(X) == 4, 'Length of X is wrong' % X
        L = [ [0, 0, 0, 1], [0, 0, 1, 0], [0, 1, 0, 0], [1, 0, 0, 0], [0, 1, 1, 1], [1, 0, 1, 1], [1, 1, 0, 1], [1, 1, 1, 0] ]
        self.exclude_set( X, L )

    def SEQSUM( self, X, k ):
        if k > 0:
            n = len( X )
            S = [ [ self.addVar() for i in range( k ) ] for j in range( n - 1 ) ]
            s = '-%d %d 0' % ( X[0], S[0][0] )
            self.addClause( s )

            for j in range(1, k):
                s = '-%d 0' % ( S[0][j] )
                self.addClause( s )

            for i in range( 1, n - 1 ):
                s = '-%d %d 0' % ( X[i], S[i][0] )
                self.addClause( s )
                s = '-%d %d 0' % ( S[i - 1][0], S[i][0] )
                self.addClause( s )

                for j in range(1, k):
                    s = '-%d -%d %d 0' % ( X[i], S[i - 1][j - 1], S[i][j] )
                    self.addClause( s )
                    s = '-%d %d 0' % ( S[i - 1][j], S[i][j] )
                    self.addClause( s )

                s = '-%d -%d 0' % ( X[i], S[i- 1][k - 1] )
                self.addClause( s )
            s = '-%d -%d 0' % ( X[n - 1], S[n - 2][k - 1] )
            self.addClause( s )
        else: # the sum is zero
            for x in X:
                s =  '-%d 0' % x
                self.addClause( s )

    def write_to_file( self, filename ):
        with open( filename, 'w' ) as f:
            f.write( 'p cnf %d %d \n' % ( self._V, len( self._clause ) ) ) 
            for clause in self._clause:
                f.write( '%s \n' % clause ) 

    def run_file( self, cnf, seed, time, solver = 'cadical' ):
        res_dict = {}
        os.system( '%s -q --seed=%d --time=%d %s > %s.res' % ( solver, seed, time, cnf, cnf ) )
        flag, resdict = self.parse( '%s.res' % cnf )
        res_dict.update( resdict ) 
        return flag, res_dict

    def parse( self, filename ):
        pattern_sat = re.compile( r's SATISFIABLE' ) 
        pattern_unsat = re.compile( r's UNSATISFIABLE' )

        Flag = None
        with open( filename, 'r' ) as f:
            line = f.readline().replace( '\n', '' )
            #print ( line )
            m = re.match( pattern_sat, line )
            u = re.match( pattern_unsat, line )
            if m:
                Flag = 1
            elif u:
                Flag = -1
            else:
                Flag = 0 # error

            res_dict = {}
            for line in f:
                if line[0] == 'v':
                    X = line[1:].split( )
                    V = list ( map( int, X ) )

                    for v in V:
                        if v < 0:
                            res_dict [ -v ] = 0
                        elif v > 0:
                            res_dict [ v ] = 1
        return Flag, res_dict 

    def solve( self, time, seed, filename = 'sat', solver = 'kissat', delete = True ):
        if os.path.isdir( 'SAT/' ) == False:
            os.system( 'mkdir SAT/')
        v = str( random.randint( 0, 0xffffffffffffffff ) )
        cnfname = 'SAT/' + filename + v
        self.write_to_file( '%s.cnf' % cnfname ) 
        self.run_file( '%s.cnf' % cnfname, seed, time, solver )
        flag, resdict = self.parse( '%s.cnf.res' % cnfname )

        if delete:
            os.system( 'rm %s.cnf' % cnfname )
            os.system( 'rm %s.cnf.res' % cnfname )

        return flag, resdict

if __name__ == '__main__':
    if shutil.which( 'kissat' ) is None:
        print( 'kissat not found on PATH; import sat from analysis scripts or install kissat to run this demo.' )
        raise SystemExit(0)

    V = [ [0, 0, 1], [0, 1, 0], [1, 0, 0], 
          [1, 1, 1], [0, 0, 0], [0, 1, 1], 
          [1, 0, 1] ]

    model = sat()

    X = [ model.addVar() for i in range(3) ]

    model.exclude_set( X, V ) 

    flag, resdict = model.solve( time = 1000, seed = 0, solver = 'kissat', delete = False )

    print( flag )

    for k, v in resdict.items():
        print( k, v )

#if __name__ == '__main__':    
#    sat = sat()
#    sat.OR( [0, 1, 2 ] )
