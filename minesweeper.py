#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MineSweeper Game.
usage: minesweeper.py [width] [height] [number of mines]
酷い英語は気にするな。
"""
import sys
import random


class MineSweeper(object):

    """MineSweeper Game."""

    def __init__(self, width, height, n_mines):
        self.width = width
        self.height = height
        self.n_mines = n_mines
        self.notdigged = True

        # List of mines
        self.mines = []
        for _ in range(n_mines):
            self.mines.append(Cell(ismine=True))

        # List of normal cells
        self.normals = []
        for _ in range(width * height - n_mines):
            self.normals.append(Cell(ismine=False))

    def place_mines(self, first_x, first_y):
        self.notdigged = False

        # List of cells
        cells = self.mines + self.normals
        while True:
            random.shuffle(cells)
            # Create the grid from the list
            self.grid = []
            for c in range(self.width):
                self.grid.append(cells[self.height * c: self.height * (c + 1)])
            if not self.grid[first_x][first_y].ismine:
                break
            print('retry')

        # Append dummy cells to prevent to count the mine on the opposite side
        for row in self.grid:
            row.append(Cell(ismine=False))
        self.grid.append([Cell(ismine=False)] * (self.width + 1))

        for x in range(self.width):
            for y in range(self.height):
                cell = self.grid[x][y]

                # Coordinate of the cell
                cell.x, cell.y = x, y

                # Cells around the cell
                cell.mines_around.append(self.grid[x-1][y-1])
                cell.mines_around.append(self.grid[x-1][y])
                cell.mines_around.append(self.grid[x-1][y+1])
                cell.mines_around.append(self.grid[x][y-1])
                cell.mines_around.append(self.grid[x][y+1])
                cell.mines_around.append(self.grid[x+1][y-1])
                cell.mines_around.append(self.grid[x+1][y])
                cell.mines_around.append(self.grid[x+1][y+1])

                # Number of mines around the cell
                n_mines = 0
                for m in cell.mines_around:
                    if m.ismine:
                        n_mines += 1
                cell.n_mines_around = n_mines

        return

    def dig(self, x, y):
        """Dig surface."""
        if self.notdigged:
            self.place_mines(x, y)

        self.grid[x][y].dig()
        return self.count_remain() == 0

    def count_remain(self):
        """Count up cells remaining."""
        nremain = 0
        for cell in self.normals:
            if not cell.isdigged:
                nremain += 1
        return nremain

    def get_grid(self):
        """Return the grid which is seen by the player.
        -1 means the cell has not been digged.
        """
        # Return a dummy grid when no mines have never been digged
        if self.notdigged:
            return [[-1] * self.height] * self.width

        mines = []
        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[x][y]
                if cell.isdigged:
                    mines.append(cell.n_mines_around)
                else:
                    mines.append(-1)

        visible_grid = []
        for c in range(self.width):
            visible_grid.append(mines[self.width * c: self.width * (c + 1)])

        return visible_grid


class Cell(object):

    """A cell of MineSweeper game."""

    def __init__(self, ismine=False):
        self.ismine = ismine
        self.isdigged = False
        self.x = 0
        self.y = 0
        self.n_mines_around = 0
        self.mines_around = []

    def dig(self):
        """Dig the cell.
        If there is no mines around the cell,
        This will dig the cells around it."""
        if self.isdigged:
            return
        self.isdigged = True
        if self.ismine:
            raise NotImplementedError
        elif self.n_mines_around == 0:
            for cell in self.mines_around:
                cell.dig()
        return

if __name__ == '__main__':
    # やっつけ仕事
    game = MineSweeper(*map(int, sys.argv[1:]))

    while True:
        visible_grid = game.get_grid()
        print('   ' + ''.join(map(lambda x: '%2d ' % x, range(game.width))))
        for x in range(game.width):
            sys.stdout.write('%2d|' % x)
            for y in range(game.height):
                if visible_grid[x][y] == -1:
                    sys.stdout.write('##|')
                elif visible_grid[x][y] == 0:
                    sys.stdout.write('  |')
                else:
                    sys.stdout.write('%2d|' % visible_grid[x][y])
            sys.stdout.write('%2d\n' % x)
        print('   ' + ''.join(map(lambda x: '%2d ' % x, range(game.width))))

        if game.dig(*map(int, input().split())):
            print('CLEAR ;)')
            sys.exit()
