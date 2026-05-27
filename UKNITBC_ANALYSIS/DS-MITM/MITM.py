import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from uknit_bc import UKNITBC
from newcipher import newcipher
import multiprocessing
import shutil
import os, sys
#from myutility.sbox import *

if __name__ == '__main__':
    if shutil.which( 'kissat' ) is None:
        print( 'kissat not found on PATH; install a SAT solver to rerun this historical DS-MITM search.' )
        raise SystemExit(0)

    uknit_bc = UKNITBC()

    ATTACK = [ (x, y) for x in range(10, 32) for y in range(25, 32) ]

    ROUND = 5
    R0 = 2
    R2 = 2
    START = 0

    SUC = []

    for attack in ATTACK:
        print( attack )
        OBJ1 = 4 * attack[0]
        OBJ2 = 4 * attack[1]

        #res = uknit_bc.MITM( START, START + ROUND, OBJ )
        res = uknit_bc.MITM_Attack( START, R0, ROUND, R2, OBJ1, OBJ2 )

        if res not in [-1, 0]:
            flag = False
            for suc in SUC:
                if suc[0] <= attack[0] and suc[1] <= attack[1]:
                    flag = True
            
            if flag == False:
                latex_file = rf'LATEX/latex3_{R0}_{ROUND}_{R2}_{OBJ1}_{OBJ2}.tex' 
                f = open( latex_file, 'w' )
                print( '--' * 20 )
                print( attack )
                res.printPath( )
                res.printAttackFigure( R0, ROUND, R2, f )
                SUC.append( attack )
                print()
                print()
                f.close()
                os.system( 'pdflatex --output-directory LATEX/ %s' % latex_file )
                os.system( 'rm LATEX/*.aux')
                os.system( 'rm LATEX/*.log')
                break
