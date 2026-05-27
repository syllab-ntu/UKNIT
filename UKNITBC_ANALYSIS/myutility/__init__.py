import os
import sys

if __name__ == '__main__' and __package__ in (None, ''):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    __package__ = 'myutility'

from .sbox import sbox
from .sat import sat
from .searchmode import searchmode

__all__ = [ 'sbox', 'sat', 'searchmode' ]
