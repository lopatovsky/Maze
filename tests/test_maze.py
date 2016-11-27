import maze
import random

######TODO requirments spustenie aby fungovalo normalne

def test_normaldist1():
    """Test"""
    random.seed(11)
    array = maze.generate_maze(10,10)
    sol = maze.analyze(array)

    print(sol.is_reachable)
    #maze.maze_generator.print_maze( sol.distances )
    print(sol.distances)
    print(sol.directions)
    sol.path(6,1)

    assert 2 == 2

def test_normaldist2():
    pass

def test_normaldir1():
    pass

def test_normaldir2():
    pass

def test_normalisreachable1():
    pass

def test_normalisreachable2():
    pass

#bez okraju

#obfuskovane
# is not reachable
