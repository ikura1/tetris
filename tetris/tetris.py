from enum import IntEnum
import random

import numpy as np
import pyxel


SCENE_TITLE = 0
SCENE_PLAY = 1
SCENE_GAMEOVER = 2

BOARD_WIDTH = 10
BOARD_HEIGHT = 20

CELL_SIZE = 8
BLOCK_SPEED = CELL_SIZE
DOWN_FRAME = 1  # 60


BLOCKS = (
    (
        2,
        ((0, -1), (0, 1), (0, 2)),
        6,
    ),  # tetris
    (4, ((0, -1), (0, 1), (1, 1)), 5),  # L1
    (4, ((0, -1), (0, 1), (-1, 1)), 9),  # L2
    (2, ((0, -1), (1, 0), (1, 1)), 8),  # key1
    (2, ((0, -1), (-1, 0), (-1, 1)), 11),  # key2
    (1, ((0, 1), (1, 0), (1, 1)), 10),  # square
    (4, ((0, -1), (1, 0), (-1, 0)), 2),  # T
)


class BLOCK_TYPE(IntEnum):
    TETRIS = 0
    L_1 = 1
    L_2 = 2
    KEY_1 = 3
    KEY_2 = 4
    SQUARE = 5
    T = 6


class Block:
    def __init__(self, x, y, type):
        self.x, self.y = x, y
        self.type = type
        self.rotate_limit, self.cells, self.color = BLOCKS[type]
        # TODO: 原点と表示を分ける
        self.rotate = 0


class Canvas:
    def __init__(self):
        self.board = None
        self.active = True
        self.block = Block(5, 1, random.randint(0, 6))
        self.init_board()

    def init_board(self):
        self.board = np.zeros((BOARD_HEIGHT + 5, BOARD_WIDTH + 2))
        self.board[:, 0] = 1
        self.board[:, -1] = 1
        self.board[-1, :] = 1
        self.active = True

    def update(self):
        if not self.active:
            return
        self.update_block()
        self.delete_block(self.block)
        if pyxel.frame_count % DOWN_FRAME == 0:
            self.block.y += 1
        if not self.put_block(self.block):
            self.block.y -= 1
            self.put_block(self.block)
            self.delete_line()
            self.block = Block(5, 1, random.randint(0, 6))
            if not self.put_block(self.block):
                self.active = False

    def update_block(self):
        # update block関数?
        nblock = Block(self.block.x, self.block.y, self.block.type)
        nblock.rotate = self.block.rotate
        if pyxel.btnp(pyxel.KEY_R):
            nblock.rotate += 1
        elif pyxel.btnp(pyxel.KEY_LEFT):
            nblock.x -= 1
        elif pyxel.btnp(pyxel.KEY_RIGHT):
            nblock.x += 1
        elif pyxel.btnp(pyxel.KEY_DOWN):
            nblock.y += 1
        elif pyxel.btnp(pyxel.KEY_T):
            # 下まで
            nblock.y += 10
        if (
            self.block.x != nblock.x
            or self.block.y != nblock.y
            or self.block.rotate != nblock.rotate
        ):
            # self.block != nblock:
            self.delete_block(self.block)
            if self.put_block(nblock):
                self.block = nblock
            else:
                self.put_block(self.block)

    def draw(self):
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                cell = self.board[y + 4][x + 1]
                pyxel.rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE, cell)

    def delete_line(self):
        for y in range(BOARD_HEIGHT):
            flag = True
            for x in range(BOARD_WIDTH):
                cell = self.board[y + 4][x + 1]
                if cell == 0:
                    flag = False

            if flag:
                self.board[1 : y + 5, 1:-1] = self.board[0 : y + 4, 1:-1]

    def put_block(self, block, action=None):
        if action is None:
            action = False
        if self.board[block.y][block.x] != 0:
            return False

        if action:
            self.board[block.y][block.x] = block.color

        for x, y in block.cells:
            # rotate
            r = block.rotate % block.rotate_limit
            cells = [cell[:] for cell in block.cells]
            for i in range(r):
                y, x = -x, y

            if self.board[block.y + y][block.x + x] != 0:
                return False

            if action:
                self.board[block.y + y][block.x + x] = block.color

        if not action:
            self.put_block(block, True)
        return True

    def delete_block(self, block):
        self.board[block.y][block.x] = 0
        for x, y in block.cells:
            r = block.rotate % block.rotate_limit
            cells = [cell[:] for cell in block.cells]
            for i in range(r):
                y, x = -x, y
            self.board[block.y + y][block.x + x] = 0
        return True


class App:
    def __init__(self):
        pyxel.init(80, 160, caption="Pyxel Tetris")
        self.scene = SCENE_TITLE
        self.canvas = Canvas()
        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        if self.scene == SCENE_TITLE:
            self.update_title_scene()
        elif self.scene == SCENE_PLAY:
            self.update_play_scene()
        elif self.scene == SCENE_GAMEOVER:
            self.update_gameover_scene()

    def update_title_scene(self):
        # TODO: DT砲とかにしたい
        if pyxel.btnp(pyxel.KEY_ENTER):
            self.scene = SCENE_PLAY

    def update_play_scene(self):
        self.canvas.update()
        if not self.canvas.active:
            self.scene = SCENE_GAMEOVER

    def update_gameover_scene(self):
        if pyxel.btnp(pyxel.KEY_ENTER):
            self.canvas.init_board()
            self.scene = SCENE_PLAY

    def draw(self):
        pyxel.cls(0)

        if self.scene == SCENE_TITLE:
            self.draw_title_scene()
        elif self.scene == SCENE_PLAY:
            self.draw_play_scene()
        elif self.scene == SCENE_GAMEOVER:
            self.draw_gameover_scene()

    def draw_title_scene(self):
        pyxel.text(14, 66, "Pyxel, Tetris!", pyxel.frame_count % 16)
        pyxel.text(11, 126, "- PRESS ENTER -", 13)

        x = 5
        y = 140
        s = "frame: {}".format(pyxel.frame_count)

        pyxel.text(x + 1, y, s, 1)

    def draw_play_scene(self):
        self.canvas.draw()

    def draw_gameover_scene(self):
        self.canvas.draw()

        pyxel.text(22, 66, "GAME OVER", 8)
        pyxel.text(11, 126, "- PRESS ENTER -", 7)


if __name__ == "__main__":
    App()