import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from myutility.sat import sat
from myutility.sbox import sbox as sbox
#from path import path, relatedkeypathW, relatedkeypathB, relatedkeypathFullBit2P, linear_path, keyrecoverypath
#from myutility.espresso import genConstr
#import galois
#import numpy as np
from linearattack import linearattack
from differentialattack import differentialattack
from divisionproperty import divisionproperty
from rkdiffattack import rkdiffattack
from mitm import mitmattack
from boomerang import boomerang
from difflinear import difflinear

class newcipher( linearattack, difflinear, boomerang, differentialattack, rkdiffattack, divisionproperty, mitmattack ):
    def __init__( self, name, roundx ):
        self.name = name
        self.roundx = roundx

    def sbox( self, rx, sx ):
        raise NotImplementedError( 'This method should be overridden by subclasses' )

    def matrix( self, rx ):
        raise NotImplementedError( 'This method should be overridden by subclasses' )

if __name__ == '__main__':
    pass
