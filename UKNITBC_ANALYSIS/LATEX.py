import random

class latex:
    def __init__(self):
        self.drawer = []

    def addstate( self, s ):
        self.drawer.append( s )

    def draw(self, standalone = False, scale = 0.3):
        if standalone == False:
            return '\n'.join( self.drawer )
        else:
            front = []
            s = r'\documentclass[svgnames]{standalone}'
            front.append( s )
            s = r'\usepackage{tikz}'
            front.append( s )
            s = r'\input avanzi-tikz-defs.tex'
            front.append( s )
            s = r'\usepackage{xcolor}'
            front.append( s )
            s = r'\begin{document}'
            front.append( s )
            s = rf'\begin{{tikzpicture}}[scale = {scale}]'
            front.append( s )
            front.append( self.draw( standalone= False ) )
            s = r'\end{tikzpicture}'
            front.append( s )
            s = r'\end{document}'
            front.append( s )
            return '\n'.join( front )

    def rectangle( self, pos:tuple, X:list, color = [ None for i in range(16)], name = '')-> None:
        '''use the bottom-left point as the basis'''
        for i in range(4):
            for j in range(4):
                if color[4 * i + j] != None:
                    s = rf'\draw[thick, fill = {color[4 * i + j]}] ({ i + pos[0]}, { pos[1] + 3 - j}) rectangle node {{\textcolor{{white}}{{$\tt {X[4 * i + j]:x}$}}}} ++(1,1);'
                    self.addstate( s )
                else:
                    s = rf'\draw[thick] ({ i + pos[0]}, { pos[1] + 3 - j}) rectangle ++(1,1);'
                    self.addstate( s )
        if name != '':
            s = rf'\node at {pos[0]+2, pos[1]-1} {{{name}}};'
            self.addstate( s )

    def rectangleGuess( self, pos:tuple, X:list, color = [ None for i in range(16)], name = '')-> None:
        '''use the bottom-left point as the basis'''
        for i in range(4):
            for j in range(4):
                if color[4 * i + j] != None:
                    s = rf'\draw[thick, fill = {color[4 * i + j]}] ({ i + pos[0]}, { pos[1] + 3 - j }) rectangle node {{}} ++(1,1);'
                    self.addstate( s )
                else:
                    s = rf'\draw[thick] ({ i + pos[0]}, { pos[1] + 3 - j }) rectangle ++(1,1);'
                    self.addstate( s )
        if name != '':
            s = rf'\node at {pos[0]+2, pos[1]-1} {{{name}}};'
            self.addstate( s )

    def rectangleKey( self, pos:tuple, X:list, name = '' )-> None:
        '''use the bottom-left point as the basis'''
        for i in range(4):
            for j in range(4):
                if X[4 * i + j] != 0:
                    s = rf'\draw[thick] ({ i + pos[0]}, { pos[1] + 3 - j }) rectangle node {{$\star$}} ++(1,1);'
                    self.addstate( s )
                else:
                    s = rf'\draw[thick] ({ i + pos[0]}, { pos[1] + 3 - j}) rectangle ++(1,1);'
                    self.addstate( s )
        if name != '':
            s = rf'\node at {pos[0]+2, pos[1]+5} {{{name}}};'
            self.addstate( s )

    def xor( self, pos:tuple, name = '' )-> None:
        '''use the bottom-left point as the basis'''
        s = rf'\node[XOR] at ({pos[0]}, {pos[1]}) {name} {{}};'
        self.addstate( s )

    def line( self, pos1, pos2, arrowtype = '', node = '' )-> None:
        if arrowtype != '':
            s = rf'\draw[thick, {arrowtype}] {pos1} -- {node} {pos2};'
            self.addstate( s )
        else:
            s = rf'\draw[thick] {pos1} -- {node} {pos2};'
            self.addstate( s )

if __name__ == '__main__':
    latex = latex()
    X = [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    C = [None for i in range(16)]
    for i in range(16):
        if X[i] == 1:
            C[i] = 'ForestGreen'

    latex.rectangle( (0,0), X, C )

    latex.xor( (5, 2), '(XOR1)' )
    latex.line( '(XOR1)', '++(1,0)', arrowtype = '' )
    latex.line( '(XOR1)', '++(-1,0)', arrowtype = '' )

    latex.rectangle( (3,-5), X, C )
    latex.line( (5,-1), '(XOR1.south)', arrowtype='-latex' )

    latex.rectangle( (6,0), X, C )
    latex.rectangle( (12,0), X, C )
    latex.rectangle( (18,0), X, C )
    latex.rectangle( (24,0), X, C )

    pic = latex.draw( standalone= True )

    print( pic )