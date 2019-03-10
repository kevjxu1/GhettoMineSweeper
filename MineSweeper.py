#!/usr/local/bin/python3
import random
import os
from functools import reduce

# clear console
clearscreen = lambda: os.system('clear')

def swap(l, i, j):
    tmp = l[j]
    l[j] = l[i]
    l[i] = tmp

def print2D(mat, mines = None):
    rows = len(mat)
    cols = len(mat[0])
    for r in range(rows):
        if mines is None:
            print(mat[r])
        else:
            print([ 'X' if (r, c) in mines else 'O' for c in range(cols) ])

    return

class MineSweeper:

    # Index is measure of difficulty. Element is (rows, cols, nmines)
    DIFFICULTY_LEVELS = [ (8, 8, 10), (16, 16, 40), (24, 24, 99) ]

    def __init__(self, rows, cols, nmines):
        # _grid[r][c] = -1 means hidden.
        # _grid[r][c] = -2 means mine.
        # Otherwise, _grid[r][c] represents number of mines adjacent (including diagonals) to position (r, c)
        self._grid = [ [ -1 for c in range(cols) ] for r in range(rows) ]
        self._nmines = nmines
        self._mines = self._initMines(nmines)
        self._nsweeped = 0


    @staticmethod
    def setup():
        """
            Prompts user for game settings initializes game

            @return MineSweeper object
        """
        userInput = input('Choose settings by entering a difficulty between 0 and %d: ' % (len(MineSweeper.DIFFICULTY_LEVELS) - 1))

        while not userInput.isdigit():
            userInput = input('Invalid input. Please select a number between 0 and %d: ' % (len(MineSweeper.DIFFICULTY_LEVELS) - 1))

        i = int(userInput[0])
        rows, cols, nmines = MineSweeper.DIFFICULTY_LEVELS[i]
        print('Initializing game with %d rows, %d columns, and %d mines' % (rows, cols, nmines))
        return MineSweeper(rows, cols, nmines)


    @staticmethod
    def toDisplayChar(val):
        if val == -2:
            return 'X'
        elif val == -1:
            return '.'
        else:
            return str(val)


    def play(self):
        rows, cols = self._getDimensions()

        # pick first non-mine square, to start
        noNeighborMines = []
        for r in range(rows):
            for c in range(cols):
                if self._countNeighboringMines(r, c) == 0 and (r, c) not in self._mines:
                    noNeighborMines.append((r, c))

        while len(noNeighborMines) == 0:
            # make a new randomized set of mines, and try again
            self._mines = self._initMines(self._nmines)
            for r in range(rows):
                for c in range(cols):
                    if self._countNeighboringMines(r, c) == 0 and (r, c) not in self._mines:
                        noNeighborMines.append((r, c))

        picked = noNeighborMines[ random.randint(0, len(noNeighborMines) - 1) ]

        # first selection is expected to always be safe
        isSafe = self._selectCoordinate(picked[0], picked[1])
        self._redrawGrid()

        # game loop
        target = rows * cols - len(self._mines)
        while isSafe and self._nsweeped < target:
            userInput = input('select square to sweep (ROW COLUMN): ').split(' ')
            while len(userInput) != 2 \
                  or not reduce(lambda acc, e: acc and e.isdigit(), userInput, True) \
                  or not self._isValidCoordinates(int(userInput[0]), int(userInput[1])):
                userInput = input('Invalid coordinates. Try again. (r c): ').split(' ')

            r, c = [ int(i) for i in userInput ]
            isSafe = self._selectCoordinate(r, c)
            self._redrawGrid()

        if not isSafe:
            print('Failure: we stepped on a mine!')
        else:
            print('Success: we evaded all mines!')

        return


    def _isValidCoordinates(self, r, c):
        rows, cols = self._getDimensions()
        return 0 <= r < rows and 0 <= c < cols


    def _selectCoordinate(self, r, c):
        """@return whether the coordinate is safe (i.e. not a mine)"""
        if (r, c) in self._mines:
            self._grid[r][c] = -2
            return False

        self._sweep(r, c)
        return True


    def _countNeighboringMines(self, r, c):
        neighbors = self._getNeighbors(r, c)
        return sum( 1 for (rr, cc) in neighbors if (rr, cc) in self._mines )


    def _sweep(self, r, c):
        """DFS until we get neighboring mines"""

        if self._grid[r][c] != -1 or (r, c) in self._mines:
            return

        # visit
        self._nsweeped += 1
        neighbors = self._getNeighbors(r, c)
        print('neighbors of %d %d: %s' % (r, c, str(neighbors)))
        self._grid[r][c] = self._countNeighboringMines(r, c)
        if self._grid[r][c] > 0:
            # this square has a neighbor square with a mine
            return
        else:
            for rr, cc in neighbors:
                self._sweep(rr, cc)

        return


    def _getNeighbors(self, r, c):
        rows, cols = self._getDimensions()
        l = []
        if r - 1 >= 0 and c - 1 >= 0:
            l.append((r - 1, c - 1))
        if r - 1 >= 0:
            l.append((r - 1, c))
        if r - 1 >= 0 and c + 1 < cols:
            l.append((r - 1, c + 1))
        if c - 1 >= 0:
            l.append((r, c - 1))
        if c + 1 < cols:
            l.append((r, c + 1))
        if r + 1 < rows and c - 1 >= 0:
            l.append((r + 1, c - 1))
        if r + 1 < rows:
            l.append((r + 1, c))
        if r + 1 < rows and c + 1 < cols:
            l.append((r + 1, c + 1))

        return l


    def _redrawGrid(self):
        rows, cols = self._getDimensions()
        clearscreen()

        # debug
        #print2D(self._grid, self._mines)

        # print row indexes
        print(str.join('', [ '%5d' % c for c in range(cols) ]))
        for r in range(rows):
            rowData = str.join('', [ '%5s' % MineSweeper.toDisplayChar(self._grid[r][c]) for c in range(cols) ])
            print(str.join('', [ str(r), rowData ]))

        return

    def _initMines(self, nmines):
        rows, cols = self._getDimensions()

        # make coordinates set
        coords = []
        for r in range(rows):
            for c in range(cols):
                coords.append((c, r))

        mines = set()

        # randomly choose nmines mines
        for i in range(nmines):
            pick = random.randint(0, len(coords) - 1)
            mines.add(coords[pick])
            swap(coords, pick, len(coords) - 1)
            coords.pop()

        return mines

    def _getDimensions(self):
        rows = len(self._grid)
        cols = len(self._grid[0])
        return rows, cols



if __name__ == '__main__':
    game = MineSweeper.setup()
    game.play()
