import os

if not os.path.exists( 'differentials.txt' ):
    print( 'differentials.txt not found; run this helper next to a generated differential log.' )
    raise SystemExit(0)

f = open( 'differentials.txt', 'r' )
lines = f.readlines()
L = [ ]
for line in lines:
    x = line.replace( ' ', '' ).split( '-' )
    L.append( eval( x[0] ) )
print( L )
