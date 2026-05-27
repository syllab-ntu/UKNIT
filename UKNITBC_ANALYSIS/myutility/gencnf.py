from sat import *
import shutil

if __name__ == '__main__':
    if shutil.which( 'kissat' ) is None:
        print( 'kissat not found on PATH; install kissat to run this CNF demo.' )
        raise SystemExit(0)

    V = [ [0, 0, 1], [0, 1, 0], [1, 0, 0], 
          [1, 1, 1], [0, 0, 0], [0, 1, 1], 
          [1, 0, 1] ]

    model = sat()

    X = [ model.addVar() for i in range(4) ]

    model.ASSIGN( X[0], 0 )
    model.ASSIGN( X[1], 0 )
    model.ASSIGN( X[2], 0 )
    model.ASSIGN( X[3], 1 )

    #model.exclude_vector( X, V[0] ) 
    model.XOR3( X ) 

    flag, resdict = model.solve( time = 1000, seed = 0, solver = 'kissat', delete = False )

    print( flag )
    for k, v in resdict.items():
        print( k, v )
