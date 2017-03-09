#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import random


class Game(object):

    def __init__(self, width, height, n_mines):
        self.width = width
        self.height = height
        self.n_mines = n_mines
        self.notdigged = True

        self.mines = []
        for _ in range(n_mines):
            self.mines.append(_Cell(ismine=True))

        self.normals = []
        for _ in range(width * height - n_mines):
            self.normals.append(_Cell(ismine=False))

    def _place_mines(self, first_x, first_y):
        self.notdigged = False

        cells = self.mines + self.normals
        while True:
            random.shuffle(cells)
            
            self.grid = []
            for c in range(self.width):
                self.grid.append(cells[self.height * c: self.height * (c + 1)])
            if not self.grid[first_x][first_y].ismine:
                break

            for column in self.grid:
                column.append(_Cell(ismine=False))
                self.grid.append([_Cell(ismine=False)] * (self.height + 1))

        for x in range(self.width):
            for y in range(self.height):
                cell = self.grid[x][y]

                cell.x, cell.y = x, y

                cell.mines_around.append(self.grid[x-1][y-1])
                cell.mines_around.append(self.grid[x-1][y])
                cell.mines_around.append(self.grid[x-1][y+1])
                cell.mines_around.append(self.grid[x][y-1])
                cell.mines_around.append(self.grid[x][y+1])
                cell.mines_around.append(self.grid[x+1][y-1])
                cell.mines_around.append(self.grid[x+1][y])
                cell.mines_around.append(self.grid[x+1][y+1])

                n_mines = 0
                for m in cell.mines_around:
                    if m.ismine:
                        n_mines += 1
                cell.n_mines_around = n_mines

        return

    def dig(self, x, y):
        if self.notdigged:
            self._place_mines(x, y)

        self.grid[x][y].dig()
        return

    def flag(self, x, y, state=True):
        if not self.grid[x][y].isdigged:
            self.grid[x][y].isflagged = state
        return

    def count_remain(self):
        nremain = 0
        for cell in self.normals:
            if not cell.isdigged:
                nremain += 1
        return nremain

    def get_grid(self):
        """
        Return the grid which is seen by the player.
         0 -  8 : number of mines around the cell.
        -1      : the cell has not been digged yet.
        -2      : the cell has been flagged (of cource it's not digged yet).
        """
        if self.notdigged:
            return [[-1] * self.height] * self.width

        mines = []
        for x in range(self.width):
            for y in range(self.height):
                cell = self.grid[x][y]
                if cell.isdigged:
                    mines.append(cell.n_mines_around)
                elif cell.isflagged:
                    mines.append(-2)
                else:
                    mines.append(-1)

        visible_grid = []
        for c in range(self.width):
            visible_grid.append(mines[self.height * c: self.height * (c + 1)])

        return visible_grid


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
