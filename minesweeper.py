#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import random


""" The Game class is a model for the minesweeper board. It contains the parameters
that define the state of the current game.
"""
class Game(object):

    def __init__(self, width, height, n_mines):
        """
        The user chooses the dimensions of the board and the number of mines
        All inputs are assumed to be integers.
        """
        self.width = width # integer number of squares
        self.height = height
        self.n_mines = n_mines # integer number of total mines on board
        self.notdigged = True # flag to indicate if square has been uncovered

        self.mines = [] # set of mines of size n_mines
        for _ in range(n_mines):
            self.mines.append(_Cell(ismine=True)) # build list of mines

        self.normals = []
        for _ in range(width * height - n_mines): # remainder of squares
            self.normals.append(_Cell(ismine=False)) # build list of non-mine squares

    def _place_mines(self, first_x, first_y):
        """
        This function places the mines on the board after the first square is uncovered.
        This is necessary such that the user doesn't lose on their first move.
        No mines will be placed on (first_x,first_y). 'n_mines' specifies how
        many mines will be placed on the x*y grid.
        We also populate each non-mine square with a number indicating how many mines
        are adjacent to this square.
        """
        self.notdigged = False #user has made their first move

        cells = self.mines + self.normals # build list of all squares
        while True: # we rearrange our grid until the user's initial square is not a mine
            random.shuffle(cells) # randomly rearrange squares
            
            self.grid = [] # we will fit the rearranged set of cells onto this grid
            for c in range(self.width):
                # each entry in the array 'grid' is itself an array. These will be the columns
                # grid is of length self.width,  while each array inside grid is of length self.height 
                self.grid.append(cells[self.height * c: self.height * (c + 1)])
            if not self.grid[first_x][first_y].ismine: # user's initial guess is not a mine
                break # valid mine arrangement acheived. Stop rearranging

        for column in self.grid:
            column.append(_Cell(ismine=False)) # build buffer cells at bottom of grid
        self.grid.append([_Cell(ismine=False)] * (self.height + 1)) #buffer cells to right of the grid

        for x in range(self.width):
            for y in range(self.height):
                cell = self.grid[x][y] # we are going to update the parameters of each cell in 'grid'

                cell.x, cell.y = x, y # map this cell at (x,y) to grid location (x,y)
                #(quite a silly and circuitous implementation)

                # build list of squares adjacent to each square (diagonals included)
                cell.mines_around.append(self.grid[x-1][y-1])
                cell.mines_around.append(self.grid[x-1][y])
                cell.mines_around.append(self.grid[x-1][y+1])
                cell.mines_around.append(self.grid[x][y-1])
                cell.mines_around.append(self.grid[x][y+1])
                cell.mines_around.append(self.grid[x+1][y-1])
                cell.mines_around.append(self.grid[x+1][y])
                cell.mines_around.append(self.grid[x+1][y+1])

                n_mines = 0
                for m in cell.mines_around: # from list of adjacent squares...
                    if m.ismine:
                        n_mines += 1 # update current square's adjacent mine count
                cell.n_mines_around = n_mines # store this value in Cell object

        return

    def dig(self, x, y): # uncover cell at (x,y)
        if self.notdigged: # if this is the first cell to be uncovered
            self._place_mines(x, y) # place mines, avoid placing mines on initial guess (x,y)

        self.grid[x][y].dig() #call dig method on Cell object
        return

    def flag(self, x, y, state=True): # allow user to set flags on possible uncovered mines
        if not self.grid[x][y].isdigged: # if cell  at (x,y) not yet uncovered
            self.grid[x][y].isflagged = state #place flag on cell at (x,y) 
        return

    def count_remain(self): # remaining uncovered non-mine squares
        nremain = 0
        for cell in self.normals: # from set of non-mine squares
            if not cell.isdigged: # if uncovered
                nremain += 1 # update number of safe cells yet to be uncovered
        return nremain

    def get_grid(self):
        """
        get_grid returns an array that can be parsed to determine grid contents
        Results from this method can be printed (with additional parsing), or used
        by automatic solving function. Each entry in the 2D array contains one of
        the following integers:

        0 -  8  : indicates number of mines adjacent to this cell.
        -1      : cell has not yet been uncovered
        -2      : cell has been flagged (covered by default)
        """
        if self.notdigged: # if grid not yet started to be solved
            return [[-1] * self.height] * self.width # return full array of covered cells

        mines = [] # long 1D array of cells populated
        for x in range(self.width):
            for y in range(self.height):
                cell = self.grid[x][y] # for cell at (x,y)
                if cell.isdigged: # if cell has been uncovered
                    # update cell's value, giving it the number of adjacent cells that are mines
                    mines.append(cell.n_mines_around) 
                elif cell.isflagged:
                    mines.append(-2) # cell value of -2 indicates it is flagged
                else:
                    mines.append(-1) # otherwise, cell still covered

        visible_grid = [] # populate 2D array from 1D array (terrible)
        for c in range(self.width): # for each column in grid
            #populate each column of output grid with the rows stored in 'mines' array
            visible_grid.append(mines[self.height * c: self.height * (c + 1)])

        return visible_grid #return 2D grid of cells with cell content information


class _Cell(object):

    def __init__(self, ismine=False):
        self.ismine = ismine
        self.isdigged = False
        self.isflagged = False
        self.x = 0
        self.y = 0
        self.n_mines_around = 0
        self.mines_around = []

    def dig(self):
        if self.isdigged:
            return
        self.isdigged = True
        if self.ismine:
            raise Exception('{}, {} is mine.'.format(self.x, self.y))
        elif self.n_mines_around == 0:
            for cell in self.mines_around:
                cell.dig()
        return


def play_game(width, height, n_mines):
    game = Game(width, height, n_mines)
    while True:
        visible_grid = game.get_grid()
        print('   ' + ''.join(map('{:2} '.format, range(game.width))))
        for y in range(game.height):
            sys.stdout.write('{:2}|'.format(y))
            for x in range(game.width):
                if visible_grid[x][y] == -1:
                    sys.stdout.write('##|')
                elif visible_grid[x][y] == 0:
                    sys.stdout.write('  |')
                else:
                    sys.stdout.write('{:2}|'.format(visible_grid[x][y]))
            sys.stdout.write('{:2}\n'.format(y))
        print('   ' + ''.join(map('{:2} '.format, range(game.width))))

        try:
            x, y = map(int, input('(x, y) : ').split())  # may raise ValueError
            if game.dig(x, y):  # may raise IndexError
                print('CLEAR ;)')
                sys.exit()
        except ValueError:
            continue
        except IndexError:
            continue
        except EOFError:
            sys.exit(1)
        except KeyboardInterrupt:
            sys.exit(1)


def solver_A(width, height, n_mines):

    game = Game(width, height, n_mines)
    yield game.get_grid()

    first_x = random.randrange(width)
    first_y = random.randrange(height)
    game.dig(first_x, first_y)
    yield game.get_grid()

    solved_cells = set()
    while True:
        map_has_not_changed = True
        for x, column in enumerate(game.get_grid()):
            for y, n_mines_around in enumerate(column):
                if (x, y) in solved_cells:
                    continue
                if n_mines_around in (0, -1):
                    continue
                grid = game.get_grid()

                cells_around = set()
                for cell_x, cell_y in [
                    (x-1, y-1), (x-1, y), (x-1, y+1),
                    (x+1, y-1), (x+1, y), (x+1, y+1),
                    (x, y-1), (x, y+1),
                ]:
                    if 0 <= cell_x < width and 0 <= cell_y < height:
                        cells_around.add((cell_x, cell_y))

                diggable_around = set()
                for cell_x, cell_y in cells_around:
                    if grid[cell_x][cell_y] == -1:
                        diggable_around.add((cell_x, cell_y))
                n_diggable_around = len(diggable_around)

                flagged_around = set()
                for cell_x, cell_y in cells_around:
                    if grid[cell_x][cell_y] == -2:
                        flagged_around.add((cell_x, cell_y))
                n_flagged_around = len(flagged_around)

                undigged_around = diggable_around | flagged_around
                n_undigged_around = len(undigged_around)

                if n_diggable_around == 0:
                    solved_cells.add((x, y))
                    continue

                if n_mines_around == n_undigged_around:
                    for cell_x, cell_y in undigged_around:
                        map_has_not_changed = False
                        game.flag(cell_x, cell_y)
                    yield game.get_grid()

                if n_mines_around == n_flagged_around:
                    for cell_x, cell_y in diggable_around:
                        map_has_not_changed = False
                        game.dig(cell_x, cell_y)
                    yield game.get_grid()

        if game.count_remain() == 0:
            return

        if map_has_not_changed:
            return


def test_solver(solver, width, height, n_mines):
    """Test a solver."""
    game = solver(width, height, n_mines)
    for visible_grid in game:
        output = '\n'
        for y in range(height):
            output += '\n'
            for x in range(width):
                if visible_grid[x][y] == -1:
                    output += '#'
                elif visible_grid[x][y] == 0:
                    output += ' '
                elif visible_grid[x][y] == -2:
                    output += 'P'
                else:
                    output += str(visible_grid[x][y])
        sys.stdout.write(output)

    result = '\nSOLVED ;)'
    for l in visible_grid:
        if -1 in l:
            result = '\nFAILED :('
            break
    print(result)
