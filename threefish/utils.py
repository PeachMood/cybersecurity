EXTENDED_KEY_SCHEDULE_CONST = 0x1BD11BDAA9FC1A22

ROUNDS_NUMBER = {
    4: 72,
    8: 72,
    16: 80,
}

PERMUTATION_TABLE = {
    4: [0, 3, 2, 1],
    8: [2, 1, 4, 7, 6, 5, 0, 3],
    16: [0, 9, 2, 13, 6, 11, 4, 15, 10, 7, 12, 3, 14, 5, 8, 1],
}

REVERSED_PERMUTATION_TABLE = {
    4: [0, 3, 2, 1],
    8: [6, 1, 0, 7, 2, 5, 4, 3],
    16: [0, 15, 2, 11, 6, 13, 4, 9, 14, 1, 8, 5, 10, 3, 12, 7],
}

ROTATION_CONSTANTS = {
    4: [
        [14, 16],
        [52, 57],
        [23, 40],
        [5, 37],
        [25, 33],
        [46, 12],
        [58, 22],
        [32, 32],
    ],
    8: [
        [46, 36, 19, 37],
        [33, 27, 14, 42],
        [17, 49, 36, 39],
        [44, 9, 54, 56],
        [39, 30, 34, 24],
        [13, 50, 10, 17],
        [25, 29, 39, 43],
        [8, 35, 56, 22],
    ],
    16: [
        [24, 13, 8, 47, 8, 17, 22, 37],
        [38, 19, 10, 55, 49, 18, 23, 52],
        [33, 4, 51, 13, 34, 41, 59, 17],
        [5, 20, 48, 41, 47, 28, 16, 25],
        [41, 9, 37, 31, 12, 47, 44, 30],
        [16, 34, 56, 51, 4, 53, 42, 41],
        [31, 44, 47, 46, 19, 42, 44, 25],
        [9, 48, 35, 52, 23, 31, 37, 20],
    ]
}

def bytes_to_words(data: bytes):
    return [int.from_bytes(data[i: i + 8], "little") for i in range(0, len(data), 8)]

def words_to_bytes(data: [int]):
    array = bytearray()
    for word in data:
        array.extend(word.to_bytes(8, "little"))
    return bytes(array)

def int64(a: int):
    return a & 0xFFFFFFFFFFFFFFFF

def add(a: int, b: int):
    return int64(a + b)

def sub(a: int, b: int):
    return int64(a - b)

def rotate_left(a: int, n: int):
    return int64((a << n) | int64(a >> (64 - n)))

def rotate_right(a: int, n: int):
    return int64(int64(a << (64 - n)) | (a >> n))
