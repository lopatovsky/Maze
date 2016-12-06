import maze
import numpy
A = numpy.array([[-1,1],[0,0]])
B =maze.analyze( A )
print(A)
print(B.directions)
print(B.distances)
print(B.is_reachable)
print(B.path(1,1))
