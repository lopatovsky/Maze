
import queue
import numpy
cimport numpy
cimport cython
from maze import maze_generator
from cpython.mem cimport PyMem_Malloc, PyMem_Realloc, PyMem_Free

cdef struct coords:
    int x
    int y

cdef class Solved_maze:


    cdef readonly char [:,:] directions
    cdef readonly int [:,:] distances
    cdef readonly int [:,:] __a
    cdef readonly bint is_reachable

    def __init__(self, array):

        sx, sy = array.shape
        #create frame
        self.__a = numpy.full( (sx+2, sy+2), -1, dtype=numpy.int32 )

        #copy data
        numpy.asarray(self.__a)[1:-1,1:-1] = array

        start_point = numpy.where(  numpy.asarray(self.__a) == 1)

        sx = self.__a.shape[0]
        sy = self.__a.shape[1]

        #init matrices
        self.distances  = numpy.full( (sx,sy), -1, dtype=numpy.int32 )
        self.directions = numpy.full( (sx,sy), b'#', dtype=('a',1))
        #set blank spaces

        print('*')
        print(self.directions )

        numpy.asarray(self.directions)[ numpy.asarray(self.__a) >= 0  ] = b' ';


        x , y = start_point
        self.__bfs( x, y , sx, sy)

        #destroy frame
        self.distances = self.distances[1:-1,1:-1]
        self.directions = self.directions[1:-1,1:-1]

        print( numpy.asarray(self.__a)[ numpy.asarray(self.__a) >= 0 ] )

        self.is_reachable =  len( numpy.asarray(self.__a)[ numpy.asarray(self.__a) >= 0 ] ) == 0

    @cython.wraparound(False)
    @cython.boundscheck(False)
    cdef int __update_queue( self, int size, int * q, int x , int y, char ch, int time ):

        #print(ch)
        if self.__a[x,y] >= 0:
            q[ size * 2 ] = x
            q[ size * 2 + 1 ] = y

            self.directions[ x,y ] = ch
           # print("*")
           # print(ch)
           # print( self.directions[x,y].dtype )
           # print(self.directions[ x,y ])
            self.distances[ x,y ] = time
            self.__a[ x,y ] = -1 #visited
            return size + 1
        else:
            return size

    @cython.wraparound(False)
    @cython.boundscheck(False)
    cdef __bfs( self, int x, int y, int sx, int sy ):

        cdef int ** q = <int **>PyMem_Malloc( (2) *sizeof(int * ))
        q[0] = <int *>PyMem_Malloc( (sx*sy) *sizeof(int))
        q[1] = <int *>PyMem_Malloc( (sx*sy) *sizeof(int))
        cdef int time = 0
        cdef int p0 = 0, p1 = 0
        cdef int i
        cdef int[2] size
        size[0] = size[1] = 0

        size[0] =  self.__update_queue(size[0], q[0], x,y, b'X',0 )

        while True:

            time += 1
            p1 = time & 1
            p0 = p1 ^ 1
            size[p1] = 0
            if size[p0] == 0: break

            for i in range( size[p0] ):
                x = q[p0][ i*2 ]
                y = q[p0][ i*2 + 1 ]

                size[p1] = self.__update_queue( size[p1], q[p1], x-1, y, b'v', time )
                size[p1] = self.__update_queue( size[p1], q[p1], x+1, y, b'^', time )
                size[p1] = self.__update_queue( size[p1], q[p1], x, y-1, b'>', time )
                size[p1] = self.__update_queue( size[p1], q[p1], x, y+1, b'<', time )


        PyMem_Free(q[0])
        PyMem_Free(q[1])
        PyMem_Free(q)

    cdef coords __move_step( self, char ch , int x, int y ):

        if ch == ord('v'): return coords(x+1, y)
        if ch == ord('^'): return coords(x-1, y)
        if ch == ord('>'): return coords(x, y+1)
        if ch == ord('<'): return coords(x, y-1)
        raise Exception("Wrong move")
    
    @cython.wraparound(False)
    @cython.boundscheck(False)
    def path(self, _x, _y ):
        
        cdef coords p = coords(_x,_y)
  

        if self.directions[p.x,p.y] == ord('#'):  raise Exception("Unreachable point")
        ret = []

        while True:
            
            ret.append( (p.x,p.y) )
            ch = self.directions[p.x,p.y]
            if ch == ord('X'): break;
            p = self.__move_step( ch, p.x, p.y )
           
        return ret

def analyze(array):
    return Solved_maze( array )

def main():
    Z = maze_generator.generate_maze(10,10,1,1)
    maze_generator.print_maze( Z )
    sol = analyze( Z )
    print(sol.is_reachable)
    maze_generator.print_maze( sol.distances )
    print(sol.distances)
    print(sol.directions)
    sol.path(6,1)
