import os

if not os.path.exists( 'linearhullcount.txt' ):
    print( 'linearhullcount.txt not found; run this helper next to a generated linear-hull log.' )
    raise SystemExit(0)

f = open( 'linearhullcount.txt', 'r' )
lines = f.readlines()
L = [ ]
for line in lines:
    x = line.replace( ' ', '' ).split( '-' )
    L.append( eval( x[0] ) )
print( L )
