import maze
import random
import numpy
import pytest


def gen_norm():
    random.seed(11)
    array = maze.generate_maze(10,10)
    return maze.analyze(array)

def gen_noframe():
    random.seed(42)
    array = maze.generate_maze(10,10)
    array = maze.remove_frame( array )
    return maze.analyze(array)

def gen_randomized():
    random.seed(66)
    array = maze.generate_maze(10,10)
    array = maze.remove_frame( array )
    array = maze.randomize( array )
    return maze.analyze(array)

def gen_notreachable():
    random.seed(89)
    array = maze.generate_maze(8,8)
    array = maze.remove_frame( array )
    array[5,4] = -1
    array = maze.randomize( array )
    return maze.analyze(array)

##### NORMAL #####

def test_normaldist():
    """Test distances"""
    A = gen_norm().distances

    print( repr(A) )

    B = numpy.array( [[-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
       [-1,  5,  4,  3,  2,  1,  2,  3,  4,  5, -1],
       [-1,  6, -1, -1, -1,  0, -1, -1, -1,  6, -1],
       [-1,  7, -1, 17, -1,  1,  2,  3, -1,  7, -1],
       [-1,  8, -1, 16, -1, -1, -1, -1, -1,  8, -1],
       [-1,  9, -1, 15, 14, 13, 12, 11, 10,  9, -1],
       [-1, 10, -1, 16, -1, -1, -1, -1, -1, 10, -1],
       [-1, 11, -1, 17, -1, 19, 20, 21, -1, 11, -1],
       [-1, 12, -1, -1, -1, 18, -1, -1, -1, 12, -1],
       [-1, 13, 14, 15, 16, 17, 16, 15, 14, 13, -1],
       [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]] )

    assert numpy.array_equal( A , B )

def test_normaldir():
    """Test directions"""
    A = gen_norm().directions

    print( repr(A) )

    B = numpy.array( [[b'#', b'#', b'#', b'#', b'#', b'#', b'#', b'#', b'#', b'#', b'#'],
       [b'#', b'>', b'>', b'>', b'>', b'v', b'<', b'<', b'<', b'<', b'#'],
       [b'#', b'^', b'#', b'#', b'#', b'X', b'#', b'#', b'#', b'^', b'#'],
       [b'#', b'^', b'#', b'v', b'#', b'^', b'<', b'<', b'#', b'^', b'#'],
       [b'#', b'^', b'#', b'v', b'#', b'#', b'#', b'#', b'#', b'^', b'#'],
       [b'#', b'^', b'#', b'>', b'>', b'>', b'>', b'>', b'>', b'^', b'#'],
       [b'#', b'^', b'#', b'^', b'#', b'#', b'#', b'#', b'#', b'^', b'#'],
       [b'#', b'^', b'#', b'^', b'#', b'v', b'<', b'<', b'#', b'^', b'#'],
       [b'#', b'^', b'#', b'#', b'#', b'v', b'#', b'#', b'#', b'^', b'#'],
       [b'#', b'^', b'<', b'<', b'<', b'<', b'>', b'>', b'>', b'^', b'#'],
       [b'#', b'#', b'#', b'#', b'#', b'#', b'#', b'#', b'#', b'#', b'#']] )

    assert numpy.array_equal( A , B )

def test_normalpath():
    """Test directions"""
    A = gen_norm().path(9,5)

    print( repr(A) )

    B = numpy.array( [(9, 5), (9, 4), (9, 3), (9, 2), (9, 1), (8, 1), (7, 1), (6, 1),
                (5, 1), (4, 1), (3, 1), (2, 1), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (2, 5)] )

    assert numpy.array_equal( A , B )


def test_normalisrechable():
    """Test is reachable"""
    A = gen_norm().is_reachable

    print( repr(A) )
    B = True

    assert numpy.array_equal( A , B )


###### NO FRAME #####

def test_noframedist():
    """Test distances"""
    A = gen_noframe().distances

    print( repr(A) )

    B = numpy.array( [[16, 15, 14, 13, 12, 11, 10,  9,  8],
                       [15, -1, 13, -1, -1, -1, 11, -1,  7],
                       [14, -1, 12, -1, 10, -1, 12, -1,  6],
                       [13, -1, 11, -1,  9, -1, -1, -1,  5],
                       [12, -1, 10,  9,  8,  7,  6,  5,  4],
                       [11, -1, -1, -1, -1, -1,  7, -1,  3],
                       [10, 11, 12, 13, 14, -1,  8, -1,  2],
                       [ 9, -1, -1, -1, -1, -1, -1, -1,  1],
                       [ 8,  7,  6,  5,  4,  3,  2,  1,  0]] )

    assert numpy.array_equal( A , B )

def test_noframedir():
    """Test directions"""
    A = gen_noframe().directions

    print( repr(A) )

    B = numpy.array( [[b'>', b'>', b'>', b'>', b'>', b'>', b'>', b'>', b'v'],
       [b'v', b'#', b'v', b'#', b'#', b'#', b'^', b'#', b'v'],
       [b'v', b'#', b'v', b'#', b'v', b'#', b'^', b'#', b'v'],
       [b'v', b'#', b'v', b'#', b'v', b'#', b'#', b'#', b'v'],
       [b'v', b'#', b'>', b'>', b'>', b'>', b'>', b'>', b'v'],
       [b'v', b'#', b'#', b'#', b'#', b'#', b'^', b'#', b'v'],
       [b'v', b'<', b'<', b'<', b'<', b'#', b'^', b'#', b'v'],
       [b'v', b'#', b'#', b'#', b'#', b'#', b'#', b'#', b'v'],
       [b'>', b'>', b'>', b'>', b'>', b'>', b'>', b'>', b'X']] )

    assert numpy.array_equal( A , B )

def test_noframepath():
    """Test directions"""
    A = gen_noframe().path(6,4)

    print( repr(A) )

    B = numpy.array( [(6, 4), (6, 3), (6, 2), (6, 1), (6, 0), (7, 0), (8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5), (8, 6), (8, 7), (8, 8)] )

    assert numpy.array_equal( A , B )


def test_noframeisrechable():
    """Test is reachable"""
    A = gen_noframe().is_reachable

    print( repr(A) )
    B = True

    assert numpy.array_equal( A , B )

###### RANDOMIZED #####

def test_randomizeddist():
    """Test distances"""
    A = gen_randomized().distances

    print( repr(A) )

    B = numpy.array( [[10, 11, 12, 13, 14, 15, 16, -1, 10],
       [ 9, -1, -1, -1, -1, -1, -1, -1,  9],
       [ 8,  7,  6,  7,  8,  9, 10, -1,  8],
       [-1, -1,  5, -1, -1, -1, -1, -1,  7],
       [22, -1,  4, -1,  2,  3,  4,  5,  6],
       [21, -1,  3, -1,  1, -1, -1, -1,  7],
       [20, -1,  2,  1,  0, -1, 14, -1,  8],
       [19, -1, -1, -1, -1, -1, 13, -1,  9],
       [18, 17, 16, 15, 14, 13, 12, 11, 10]] )

    assert numpy.array_equal( A , B )

def test_randomizeddir():
    """Test directions"""
    A = gen_randomized().directions

    print( repr(A) )

    B = numpy.array( [[b'v', b'<', b'<', b'<', b'<', b'<', b'<', b'#', b'v'],
       [b'v', b'#', b'#', b'#', b'#', b'#', b'#', b'#', b'v'],
       [b'>', b'>', b'v', b'<', b'<', b'<', b'<', b'#', b'v'],
       [b'#', b'#', b'v', b'#', b'#', b'#', b'#', b'#', b'v'],
       [b'v', b'#', b'v', b'#', b'v', b'<', b'<', b'<', b'<'],
       [b'v', b'#', b'v', b'#', b'v', b'#', b'#', b'#', b'^'],
       [b'v', b'#', b'>', b'>', b'X', b'#', b'v', b'#', b'^'],
       [b'v', b'#', b'#', b'#', b'#', b'#', b'v', b'#', b'^'],
       [b'>', b'>', b'>', b'>', b'>', b'>', b'>', b'>', b'^']] )

    assert numpy.array_equal( A , B )

def test_randomizedpath():
    """Test directions"""
    A = gen_randomized().path(0,2)

    print( repr(A) )

    B = numpy.array( [(0, 2), (0, 1), (0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (6, 3), (6, 4)] )

    assert numpy.array_equal( A , B )


def test_randomizedisrechable():
    """Test is reachable"""
    A = gen_randomized().is_reachable

    print( repr(A) )
    B = True

    assert numpy.array_equal( A , B )


###### NOT REACHABLE #####

def test_notreachabledist():
    """Test distances"""
    A = gen_notreachable().distances

    print( repr(A) )

    B = numpy.array( [[ 5,  4,  3,  2,  1,  0,  1],
       [ 6, -1,  4, -1, -1, -1,  2],
       [ 7, -1,  5, -1, -1, -1,  3],
       [ 8, -1,  6, -1, -1, -1,  4],
       [ 9, -1,  7, -1, -1, -1,  5],
       [10, -1, -1, -1, -1, -1,  6],
       [11, 12, 11, 10,  9,  8,  7]] )

    assert numpy.array_equal( A , B )

def test_notreachabledir():
    """Test directions"""
    A = gen_notreachable().directions

    print( repr(A) )

    B = numpy.array( [[b'>', b'>', b'>', b'>', b'>', b'X', b'<'],
       [b'^', b'#', b'^', b'#', b'#', b'#', b'^'],
       [b'^', b'#', b'^', b'#', b'#', b'#', b'^'],
       [b'^', b'#', b'^', b'#', b'#', b'#', b'^'],
       [b'^', b'#', b'^', b'#', b'#', b'#', b'^'],
       [b'^', b'#', b'#', b'#', b'#', b'#', b'^'],
       [b'^', b'<', b'>', b'>', b'>', b'>', b'^']] )

    assert numpy.array_equal( A , B )

def test_notreachablepath():
    """Test directions"""
    A = gen_notreachable().path(0,2)

    print( repr(A) )

    B = numpy.array( [(0, 2), (0, 3), (0, 4), (0, 5)] )

    assert numpy.array_equal( A , B )


def test_notreachableisrechable():
    """Test is reachable"""
    A = gen_notreachable().is_reachable

    print( repr(A) )
    B = False

    assert numpy.array_equal( A , B )



