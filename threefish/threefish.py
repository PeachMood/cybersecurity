from utils import EXTENDED_KEY_SCHEDULE_CONST, ROUNDS_NUMBER, PERMUTATION_TABLE, REVERSED_PERMUTATION_TABLE, ROTATION_CONSTANTS, add, sub, rotate_left, rotate_right, bytes_to_words, words_to_bytes
from functools import reduce

class Threefish:
    k: [int]
    t: [int]
    nw: int
    nr: int
    pi: [int]
    rpi: [int]
    r: [[int]]
    kd: [[int]]

    def __init__(self, key: bytes, tweak: bytes):
        if len(key) not in [32, 64, 128]:
            raise ValueError(f"The length of the key must be 258, 512 or 1024 bit")

        if len(tweak) != 16:
            raise ValueError(f"The length of the tweak must be 128 bit")

        self.k = bytes_to_words(key)
        self.t = bytes_to_words(tweak)
        self.nw = len(key) // 8
        self.nr = ROUNDS_NUMBER[self.nw]
        self.pi = PERMUTATION_TABLE[self.nw]
        self.rpi = REVERSED_PERMUTATION_TABLE[self.nw]
        self.r = ROTATION_CONSTANTS[self.nw]
        self.prepare_key()
        self.prepare_tweak()
        self.prepare_subkeys()

    def prepare_key(self):
        self.k.append(reduce(lambda result, element: element ^ result, self.k[:]) ^ EXTENDED_KEY_SCHEDULE_CONST)

    def prepare_tweak(self):
        self.t.append(self.t[0] ^ self.t[1])

    def prepare_subkeys(self):
        self.kd = [[0 for _ in range(self.nw)] for _ in range(self.nr // 4 + 1)]
        for s in range(self.nr // 4 + 1):
            for i in range(self.nw):
                self.kd[s][i] = self.k[(s + i) % (self.nw + 1)]
                if i == self.nw - 3:
                    self.kd[s][i] = add(self.kd[s][i], self.t[s % 3])
                elif i == self.nw - 2:
                    self.kd[s][i] = add(self.kd[s][i], self.t[(s + 1) % 3])
                elif i == self.nw - 1:
                    self.kd[s][i] = add(self.kd[s][i], s)

    def mix(self, x0: int, x1: int, d: int, j: int):
        y0 = add(x0, x1)
        y1 = rotate_left(x1, self.r[d % 8][j]) ^ y0
        return y0, y1

    def encrypt_block(self, plaintext: bytes):
        plaintext = bytes_to_words(plaintext)
        if len(self.k) - 1 != len(plaintext):
            raise ValueError(f"The key and the plaintext must be the same length")

        vd = plaintext.copy()
        for d in range(self.nr):
            ed = [0] * self.nw
            if d % 4 == 0:
                for i in range(self.nw):
                    ed[i] = add(vd[i], self.kd[d // 4][i])
            else:
                ed = vd.copy()

            fd = [0] * self.nw
            for j in range(self.nw // 2):
                fd[2 * j], fd[2 * j + 1] = self.mix(ed[2 * j], ed[2 * j + 1], d, j)

            for i in range(self.nw):
                vd[i] = fd[self.pi[i]]

        c = []
        for i in range(self.nw):
            c.append(add(vd[i], self.kd[self.nr // 4][i]))

        return words_to_bytes(c)

    def demix(self, y0, y1, d, j):
        y1 ^= y0
        x1 = rotate_right(y1, self.r[d % 8][j])
        x0 = sub(y0, x1)
        return x0, x1

    def decrypt_block(self, ciphertext):
        ciphertext = bytes_to_words(ciphertext)
        if len(self.k) - 1 != len(ciphertext):
            raise ValueError(f"The key and the ciphertext must be the same length")

        vd = ciphertext.copy()
        for d in range(self.nr, 0, -1):
            fd = [0] * self.nw
            if d % 4 == 0:
                for i in range(self.nw):
                    fd[i] = sub(vd[i], self.kd[d // 4][i])
            else:
                fd = vd.copy()

            ed = [0] * self.nw
            for i in range(self.nw):
                ed[i] = fd[self.rpi[i]]

            for j in range(self.nw // 2):
                vd[2 * j], vd[2 * j + 1] = self.demix(ed[2 * j], ed[2 * j + 1], d - 1, j)

        c = []
        for i in range(self.nw):
            c.append(sub(vd[i], self.kd[0][i]))

        return words_to_bytes(c)

