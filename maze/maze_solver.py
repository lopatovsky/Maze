import queue
import numpy
from maze import maze_generator

class Solved_maze:

    def __init__(self, array):

        sx, sy = array.shape
        #create frame
        self.__a = numpy.full( (sx+2, sy+2), -1, dtype=int )

        #copy data
        self.__a[1:-1,1:-1] = array

        start_point = numpy.where(self.__a == 1)

        #init matrices
        self.distances  = numpy.full( self.__a.shape, -1, dtype=int )
        self.directions = numpy.full( self.__a.shape, b'#', dtype=('a',1))
        #set blank spaces

        self.directions[ numpy.where(  self.__a >= 0 ) ] = b' ';

        self.__bfs( start_point )

        #destroy frame
        self.distances = self.distances[1:-1,1:-1]
        self.directions = self.directions[1:-1,1:-1]

        self.is_reachable =  len( self.__a[ self.__a >= 0 ] ) == 0


    def __update_queue( self, q, point , ch, time ):
        if self.__a[point] >= 0:
            q.put( ( time , point ) )
            self.directions[ point ] = ch
            self.distances[ point ] = time
            self.__a[ point ] = -1 #visited

    def __bfs( self, point ):

        q = queue.PriorityQueue()
        self.__update_queue(q, point, b'X', 0 )

        while not q.empty():
            time , ( x , y ) = q.get()
            self.__update_queue( q, (x-1, y), b'v', time + 1 )
            self.__update_queue( q, (x+1, y), b'^', time + 1 )
            self.__update_queue( q, (x, y-1), b'>', time + 1 )
            self.__update_queue( q, (x, y+1), b'<', time + 1 )

    def __move_step( self, ch , x, y ):

        if ch == b'v': return (x+1, y)
        if ch == b'^': return (x-1, y)
        if ch == b'>': return (x, y+1)
        if ch == b'<': return (x, y-1)
        raise Exception("Wrong move")

    def path(self, *point ):

        print( type(point) )

        if self.directions[point] == b'#':  raise Exception("Unreachable point")
        p = []

        while True:

            p.append( point )
            ch = self.directions[point]
            if ch == b'X': break;
            point = self.__move_step( ch, *point )

        return p

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
