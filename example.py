import maze
import numpy
A = numpy.array([[-1,1],[0,0]])
B =maze.analyze( A )
print(B.directions)
print(B.distances)
