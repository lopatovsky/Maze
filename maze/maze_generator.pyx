import numpy
import random
cimport numpy
cimport cython
import matplotlib.pyplot as pyplot
from libc.stdlib cimport rand, srand
from libc.time cimport time

@cython.wraparound(False)
@cython.boundscheck(False)
def generate_maze(width=81, height=51, _complexity=.75, _density=.75):

    srand(time(NULL))
    # Only odd shapes
    origin_shape = (height, width)
    shape = ((height // 2) * 2 + 1, (width // 2) * 2 + 1)  #can be bigger then original but it doesn't matter
    # Adjust complexity and density relative to maze size
    cdef int complexity = int(_complexity * (5 * (shape[0] + shape[1])))
    cdef int density    = int(_density * ((shape[0] // 2) * (shape[1] // 2)))

    if complexity > 607: compexity = 607
    if density > 1200: density = 1200

    # Build actual maze
    cpdef numpy.ndarray[numpy.int32_t, ndim=2] Z = numpy.full( origin_shape, 0, dtype=numpy.int32 )
    # Fill borders
    Z[0, :] = Z[-1, :] = -1
    Z[:, 0] = Z[:, -1] = -1

    cdef int i,j, x, y, x_, y_

    # Make aisles
    for i in range(density):
        x = rand()%( shape[1] // 2) * 2
        y = rand()%(shape[0] // 2) * 2
        Z[y, x] = -1
        for j in range(complexity):
            neighbours = []
            if x > 1:             neighbours.append((y, x - 2))
            if x < shape[1] - 2:  neighbours.append((y, x + 2))
            if y > 1:             neighbours.append((y - 2, x))
            if y < shape[0] - 2:  neighbours.append((y + 2, x))
            if len(neighbours):
                y_,x_ = neighbours[rand()%( len(neighbours) - 1)]
                if Z[y_, x_] == 0:
                    Z[y_, x_] = -1
                    Z[ y_ + (y - y_) // 2,x_ + (x - x_) // 2 ] = -1
                    x = x_
                    y = y_

    # Make start point
    #x, y = random.randint(0, shape[1] // 2) * 2, random.randint(0, shape[0] // 2) * 2
    x, y = random.choice( numpy.column_stack(numpy.where(Z == 0)) )
    Z[x,y] = 1

    return Z

def remove_frame( array ):
    return array[1:-1,1:-1]

def val_to_rand( val ):
    if random.randint(0,2) == 1: return val
    if val == 1: return 1
    if val < 0: return - random.randint(1,10)
    if val >=0: return random.randint(2,10)

def randomize( array ):
    f = numpy.vectorize( val_to_rand )
    return f( array )

def print_maze( Z ):
    pyplot.figure(figsize=(10, 5))
    pyplot.imshow( -Z, cmap=pyplot.cm.binary, interpolation='nearest')
    pyplot.xticks([]), pyplot.yticks([])
    pyplot.show()
