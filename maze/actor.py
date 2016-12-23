"""This file has been placed in the public domain"""
import asyncio
import contextlib
import time
import random

DIR = [ ( b'v', (1,0) ), ( b'>', (0,1) ) , ( b'^', (-1,0) ), ( b'<', (0,-1) ) ]
#RIGHT = { ( (1,0),(0,-1)), ( (0,1),(1,0)), ( (-1,0),(0,1)) , ( (0,-1),(-1,0))  }

class Actor:
    def __init__(self, grid, row, column, kind):
        """Coroutine-based actor on a grid

        :param grid:

            The grid this actor moves on. Must have the following attributes:

            * ``update_actor(actor)``: Called to mark the space currently
                occupied by the actor as "dirty" (needs redrawing)
            * ``cell_size``: size of a grid cell, in pixels (used to optimize
                animations)
            * ``directions``: a NumPy array of directions (ASCII bytes),
                containing ``b'v'``, ``b'<'``, ``b'>'``, ``b'^'`` depending
                on where the actor should move to from a particular cell.
                Only used in the default implementation of ``behavior``.

            This is stored in an attribute with the same name.

        :param row:
        :param column:

            The initial position of the actor.
            These are stored in attributes with the same names, and are updated
            regularly.
            When the actor is currently moving, the values are floats.

        :param kind:

            Any data for use by the grid drawing code.
            This is stored in an attribute with the same name.

        The attribute ``task`` will hold an ``asyncio.Task`` object
        corresponding to the actor's behavior. Cancel it when done.
        """
        self.row = row
        self.column = column
        self.kind = kind
        self.grid = grid
        #self.task = asyncio.ensure_future(self.behavior())


    async def behavior(self):
        """Coroutine containing the actor's behavior

        The base implementation follows directions the actor is standing on.
        If there is no directions (e.g. standing on a wall, unreachable space,
        or on the goal), the actor jumps repeatedly.

        To be reimplemented in subclasses..
        """

        if self.grid.directions[ int(self.row), int(self.column) ] == b' ':
            self.grid.no_path()
        await self.jump(1.0)

        while True:
            #shape = self.grid.directions.shape
            #row = int(self.row)
            #column = int(self.column)
            #if 0 <= row < shape[0] and 0 <= column < shape[1]:
            direction = self.grid.directions[ int(self.row), int(self.column) ]
            #else:
            #    direction = b'?'

            for d in DIR:
                if direction == d[0]:
                    move = d[1]
                    break
            else:
                if direction == b'X':
                    self.grid.end_game()
                    return

            await self.step( *move )

    def is_ok( self, row, column ):

        shape = self.grid.directions.shape
        return ( 0 <= row < shape[0] and 0 <= column < shape[1] and self.grid.array[ row, column ] >= 0 )


    def _progress(self, duration):
        """Iterator that yields progress from 0 to 1 based on time

        In each iteration, yields a number based on the current time:

        * 0.0 at the time the generator was started;
        * 1.0 at start time plus ``duration`` seconds (end time)
        * for the time in between, a linearly interpolated number between 0...1

        It is not guaranteed that 1.0 will be yielded on the last iteration.

        When using this with a for-loop, you probably need to put
        a sleep/delay into each iteration.
        """
        start = time.monotonic()
        while True:
            now = time.monotonic()
            p = (now - start) / duration
            if p > 1:
                return
            yield p

    @contextlib.contextmanager
    def _update_context(self):
        """Context manager for updating the actor's position

        Updates the grid widget before and after the contextis entered.
        Wrapping any coordinate updates in this context wil ensure the actor
        is drawn correctly.
        """
        self.grid.update_actor(self)
        yield
        self.grid.update_actor(self)

    async def step(self, dr, dc, duration=1):
        """Coroutine for a step in a given direction

        Smoothly moves ``dr`` tiles in the row-direction and ``dc`` tiles in
        the column-direction in ``duration`` seconds.
        """
        start_row = self.row
        start_col = self.column

        for p in self._progress(duration):
            with self._update_context():
                self.row = start_row + dr * p
                self.column = start_col + dc * p

            # Sleep amount is based on zoom level: we want to sleep for
            # about one pixel's worth of movement.
            await asyncio.sleep(duration/self.grid.cell_size)

        # Final update to the exact ending position (this should use integer
        # arithmetic, so it avoids rounding errors)
        with self._update_context():
            self.row = start_row + dr
            self.column = start_col + dc

    async def jump(self, duration=0.2):
        """Coroutine for a small jump

        Smoothly moves a bit up and down in ``duration`` seconds.
        """
        start_row = self.row

        for p in self._progress(duration):
            with self._update_context():
                # jump along a parabola
                self.row = start_row - p * (1-p)

            await asyncio.sleep(duration/self.grid.cell_size * 2)

        with self._update_context():
            self.row = start_row

    async def shiver(self, duration=0.1):
        """Coroutine for a small shiver

        Smoothly moves a bit left and right in ``duration`` seconds.
        """
        start_column = self.column

        for p in self._progress(duration):
            with self._update_context():
                # jump along a parabola
                self.column = start_column - p * (1-p)

            await asyncio.sleep(duration/self.grid.cell_size * 2)

        with self._update_context():
            self.column = start_column


class Fast_Actor ( Actor ):  #TODO refactor same code.

    async def behavior(self):

        if self.grid.directions[ int(self.row), int(self.column) ] == b' ':
            self.grid.no_path()
        await self.jump(1.0)

        while True:

            direction = self.grid.directions[ int(self.row), int(self.column) ]

            for d in DIR:
                if direction == d[0]:
                    move = d[1]
                    break
            else:
                if direction == b'X':
                    self.grid.end_game()
                    return

            await self.step( *move, 0.57 ) #cca 75% faster.


class Teleported_Actor ( Actor ):

    async def behavior(self):

        distances = self.grid.solved.distances

        if self.grid.directions[ int(self.row), int(self.column) ] == b' ':
            self.grid.no_path()
        await self.jump(1.0)

        while True:

            direction = self.grid.directions[ int(self.row), int(self.column) ]
            if direction == b'X':
                        self.grid.end_game()
                        return

            if random.randint(0,10) <= 1:


                shape = self.grid.directions.shape
                move = ( random.randint( 0,shape[0] - 1 ), random.randint( 0,shape[0] - 1 ) )

                if self.is_ok( *move ) and distances[move] > 5:
                    for i in range(4):
                        await self.shiver()
                    self.row, self.column = move
                    #print(self.row, self.column)
                    for i in range(4):
                        await self.shiver()




            else:

                for d in DIR:
                    if direction == d[0]:
                        move = d[1]
                        break
                else:
                    if direction == b'X':
                        self.grid.end_game()
                        return

                await self.step( *move)


class Accelerated_Actor ( Actor ):  #TODO refactor same code.

    async def behavior(self):

        if self.grid.directions[ int(self.row), int(self.column) ] == b' ':
            self.grid.no_path()
        await self.jump(1.0)
        last = (0,0)
        speed = 1.0

        while True:

            direction = self.grid.directions[ int(self.row), int(self.column) ]

            for d in DIR:
                if direction == d[0]:
                    move = d[1]
                    break
            else:
                if direction == b'X':
                    self.grid.end_game()
                    return


            if last == move:
                speed *= 9/10
            else:
                speed = 1.0

            last = move
            await self.step( *move, speed )



class Confused_Actor (Actor):

    async def behavior(self):

        if self.grid.directions[ int(self.row), int(self.column) ] == b' ':
            self.grid.no_path()
        await self.jump(1.0)

        array = self.grid.array
        move = ( 0, 0 )
        last_pos = ( -1, -1 )

        while True:
            pos = int(self.row), int(self.column)
            direction = self.grid.directions[ pos ]

            if direction == b'X':
                self.grid.end_game()
                return

            chosen = 0

            r1 = random.randint(0,2)
            if r1 == 0:
                r_dir = random.randint(0,3)
                move = DIR[r_dir][1]
                if self.is_ok( self.row + move[0], self.column + move[1] ):
                    chosen = 1

            if chosen == 0:
                for d in DIR:
                    if direction == d[0]:
                        move = d[1]
                        break


            if (pos[0] + move[0], pos[1] + move[1]) == last_pos:
                for d in DIR:
                    p = self.row + d[1][0], self.column + d[1][1]
                    if self.is_ok( *p ) and p!=last_pos:
                        chosen = 0

            if chosen == 0:
                continue

            last_pos = pos

            await self.step( *move )

class Right_hand_Actor ( Actor ):

    #def is_ok( self, row, column ):
    #    shape = self.grid.directions.shape
    #    return ( 0 <= row < shape[0] and 0 <= column < shape[1] and self.grid.array[ row, column ] >= 0  and self.visited[ row, column ] >= 0)


    async def behavior(self):

        if self.grid.directions[ int(self.row), int(self.column) ] == b' ':
            self.grid.no_path()
        await self.jump(1.0)

        begin = True;
        last_move = (0,0)
        last_speed = 1.0


        while True:

            direction = self.grid.directions[ int(self.row), int(self.column) ]

            if direction == b'X':
                        self.grid.end_game()
                        return

            if last_move[1] == 0: right = last_move[1], - last_move[0]
            else: right = last_move[1], last_move[0]

            if  self.is_ok( self.row+right[0], self.column+right[1] ) == False :
                move = last_move
                begin = False
            elif begin == False:
                move = right
            else:

                for d in DIR:
                    if direction == d[0]:
                        move = d[1]
                        break


            while self.is_ok( self.row+move[0], self.column+move[1] ) == False:
                if move[0] == 0: move = -move[1], move[0]
                else: move = move[1], move[0]

            speed = 1.0-random.randint(0,99)/100.0
            alpha = 0.7
            speed = (speed *  alpha + last_speed * (1.0 - alpha))

            last_move = move
            last_speed = speed
            await self.step( *move, speed ) #cca 75% faster.

