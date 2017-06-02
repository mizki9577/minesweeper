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
    """
    The _Cell class has fields to indicate the location (x,y) and state (isdigged etc).
    It also has information on the number and location of 
    """

    def __init__(self, ismine=False):
        self.ismine = ismine
        self.isdigged = False
        self.isflagged = False
        self.x = 0 #location on grid
        self.y = 0
        self.n_mines_around = 0
        self.mines_around = [] # set of 8 adjacent mines (diagonals included). This set will be built by the Game object (terrible design)
        

    def dig(self): #uncovers cell, updates status of cell and indicates when mine is uncovered 
        if self.isdigged: # if already uncovered, do nothing
            return
        self.isdigged = True 
        if self.ismine:
            raise Exception('{}, {} is mine.'.format(self.x, self.y)) # end game when mine is uncovered
        elif self.n_mines_around == 0: # if no mines are adjacent...
            for cell in self.mines_around: # dig all around this square. Guaranteed to not uncover any mines
                cell.dig()
        return


def play_game(width, height, n_mines):
    """
    This is the entry point for running the code. Bash script (game) interfaces command line to this python code
    This creates a game with the given grid size and number of mines. Also accepts user input and displays
    updated game board to command line
    """
    game = Game(width, height, n_mines) 
    while True: #until the end of game or until error occurs
        visible_grid = game.get_grid() # get parseable and printable grid information
        print('   ' + ''.join(map('{:2} '.format, range(game.width)))) # print indices around border of game grid
        for y in range(game.height): # print columns
            sys.stdout.write('{:2}|'.format(y)) #print row index
            for x in range(game.width): #print row contents
                if visible_grid[x][y] == -1: #if covered, print '#'
                    sys.stdout.write('##|')
                elif visible_grid[x][y] == 0: # if uncovered, print blank space
                    sys.stdout.write('  |')
                else:
                    sys.stdout.write('{:2}|'.format(visible_grid[x][y])) #else print the number of adjacent mines
            sys.stdout.write('{:2}\n'.format(y)) # print on next line.
        print('   ' + ''.join(map('{:2} '.format, range(game.width)))) # print indices around bottom border

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
    """
    solver_A creates a new game and iterates over cells until game is solved or
    it cannot progress further
    """
    game = Game(width, height, n_mines)
    yield game.get_grid() # generate game grid

    first_x = random.randrange(width) #make initial random guess
    first_y = random.randrange(height)
    game.dig(first_x, first_y) #dig at this guess
    yield game.get_grid() #see results of guess

    solved_cells = set() # set of safe uncovered cells
    while True: #iterate until solved or game is non-determinate
        map_has_not_changed = True #flag to indicate that we can't solve board without guessing
        for x, column in enumerate(game.get_grid()): #iterate over columns, x is index of column
            for y, n_mines_around in enumerate(column): #iterate over entries of column, retrieve number of mines adjacent
                if (x, y) in solved_cells:
                    continue
                if n_mines_around in (0, -1): #if cell uncovered or has no adjacent mines
                    continue #do nothing
                grid = game.get_grid() #update grid model

                cells_around = set() # set of cells adjacent to current cell
                for cell_x, cell_y in [
                    (x-1, y-1), (x-1, y), (x-1, y+1),
                    (x+1, y-1), (x+1, y), (x+1, y+1),
                    (x, y-1), (x, y+1),
                ]:
                    if 0 <= cell_x < width and 0 <= cell_y < height:
                        #populate cells_around with index tuples of adjacent cells
                        cells_around.add((cell_x, cell_y)) 

                diggable_around = set() # set of adjacent cells that are still covered
                for cell_x, cell_y in cells_around:
                    if grid[cell_x][cell_y] == -1: # if adjacent cell is uncovered
                        diggable_around.add((cell_x, cell_y)) # add to set of uncovered adjacent cells
                n_diggable_around = len(diggable_around)

                flagged_around = set() #set of flagged adjacent cells
                for cell_x, cell_y in cells_around:
                    if grid[cell_x][cell_y] == -2: # if adjacent cell flagged
                        flagged_around.add((cell_x, cell_y)) #add to set
                n_flagged_around = len(flagged_around)

                undigged_around = diggable_around | flagged_around #union of two previously constructed sets
                n_undigged_around = len(undigged_around) # number of adjacent uncoverable cell candidates

                if n_diggable_around == 0: # if no adjacent cells can be uncovered
                    solved_cells.add((x, y)) # this cell is solved
                    continue

                if n_mines_around == n_undigged_around: #if all covered adjacent cells are mines
                    for cell_x, cell_y in undigged_around:
                        map_has_not_changed = False #we've found a mine(s)
                        game.flag(cell_x, cell_y) #flag that mine
                    yield game.get_grid() #update grid

                if n_mines_around == n_flagged_around: #if all adjacent mines are accounted for
                    for cell_x, cell_y in diggable_around:
                        map_has_not_changed = False # we've uncovered safe cells
                        game.dig(cell_x, cell_y) # dig everywhere adjacent except where mines are located
                    yield game.get_grid()

        if game.count_remain() == 0: # if all safe cells are uncovered
            return #we've won

        if map_has_not_changed: #if solving cannot progress further
            return # cannot solve without guessing


def test_solver(solver, width, height, n_mines):
    """
    This function interfaces command line calls to the solver module. This
    function prints the final grid that the solver produces
    """
    game = solver(width, height, n_mines)
    for visible_grid in game:
        output = '\n' # separate solution by a newline
        for y in range(height):
            output += '\n' # print next row
            for x in range(width):
                if visible_grid[x][y] == -1: #if cell covered
                    output += '#'
                elif visible_grid[x][y] == 0: #if cell uncovered
                    output += ' '
                elif visible_grid[x][y] == -2: #if cell is possible a mine, but not determineable
                    output += 'P'
                else:
                    output += str(visible_grid[x][y]) #else output number of adjacent mines
        sys.stdout.write(output)

    result = '\nSOLVED ;)'
    for l in visible_grid:
        if -1 in l: # if covered cell exists in solution 
            result = '\nFAILED :(' # solver was not able to complete puzzle
            break
    print(result)
