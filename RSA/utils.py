import math
from random import randrange, getrandbits

def module_power(a, n, m):
    r = 1
    while n > 0:
        if n & 1 == 1:
            r = (r * a) % m
        a = (a * a) % m
        n >>= 1
    return r

def multiplicative_inverse(e, phi):
    d = 0
    x1 = 0
    x2 = 1
    y1 = 1
    temp_phi = phi

    while e > 0:
        temp1 = temp_phi//e
        temp2 = temp_phi - temp1 * e
        temp_phi = e
        e = temp2

        x = x2 - temp1 * x1
        y = d - temp1 * y1

        x2 = x1
        x1 = x
        d = y1
        y1 = y

    if temp_phi == 1:
        return d + phi

def is_prime_test(n: int, k: int = 128) -> bool:
    if n == 2 or n == 3:
        return True
    if n <= 1 or n % 2 == 0:
        return False

    s = 0
    r = n - 1
    while r & 1 == 0:
        s += 1
        r //= 2

    for _ in range(k):
        a = randrange(2, n - 1)
        x = pow(a, r, n)
        if x != 1 and x != n - 1:
            j = 1
            while j < s and x != n - 1:
                x = pow(x, 2, n)
                if x == 1:
                    return False
                j += 1
            if x != n - 1:
                return False
    return True

def generate_odd_number(length: int) -> int:
    p = getrandbits(length)
    p |= (1 << length - 1) | 1
    return p

def generate_prime_number(length: int) -> int:
    p = 4
    while not is_prime_test(p):
        p = generate_odd_number(length)
    return p

def bytes_to_blocks(raw_bytes: bytes, block_length: int) -> list[int]:
    return [int.from_bytes(raw_bytes[i: i + block_length], 'little') for i in range(0, len(raw_bytes), block_length)]

def blocks_to_bytes(blocks: list[int]) -> bytes:
    array = bytearray()
    for block in blocks:
        array.extend(block.to_bytes(math.ceil(block.bit_length() / 8), 'little'))
    return bytes(array)
