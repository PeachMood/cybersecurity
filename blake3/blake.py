IV = [0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19]

CHUNK_START = 2 ** 0
CHUNK_END = 2 ** 1
PARENT = 2 ** 2
ROOT = 2 ** 3

BLOCK_LENGTH = 64
CHUNK_LENGTH = 1024

def t0(counter: int) -> int:
    return (counter << 32) >> 32

def t1(counter: int) -> int:
    return counter >> 32

def int32(a: int) -> int:
    return a % (2 ** 32)

def add(a: int, b: int) -> int:
    return int32(a + b)

def rot(a: int, n: int) -> int:
    return  (a >> n) | int32(a << (32 - n))

def g(a: int, b: int, c: int, d: int, m1: int, m2: int):
    a = add(a, add(b, m1))
    d = rot(d ^ a, 16)
    c = add(c, d)
    b = rot(b ^ c, 12)
    a = add(a, add(b, m2))
    d = rot(d ^ a, 8)
    c = add(c, d)
    b = rot(b ^ c, 7)
    return a, b, c, d

def permutation(m: [int]):
    return [m[2], m[6], m[3], m[10], m[7], m[0], m[4], m[13], m[1], m[11], m[12], m[5], m[9], m[14], m[15], m[8]]

def e(m: [int], v: [int]):
    v[0], v[4], v[8], v[12] = g(v[0], v[4], v[8], v[12], m[0], m[1])
    v[1], v[5], v[9], v[13] = g(v[1], v[5], v[9], v[13], m[2], m[3])
    v[2], v[6], v[10], v[14] = g(v[2], v[6], v[10], v[14], m[4], m[5])
    v[3], v[7], v[11], v[15] = g(v[3], v[7], v[11], v[15], m[6], m[7])
    v[0], v[5], v[10], v[15] = g(v[0], v[5], v[10], v[15], m[8], m[9])
    v[1], v[6], v[11], v[12] = g(v[1], v[6], v[11], v[12], m[10], m[11])
    v[2], v[7], v[8], v[13] = g(v[2], v[7], v[8], v[13], m[12], m[13])
    v[3], v[4], v[9], v[14] = g(v[3], v[4], v[9], v[14], m[14], m[15])
    m = permutation(m)
    return m, v

def compress(h: [int], m: [int], t: int, b: int, d: int):
    v = [
        h[0], h[1], h[2], h[3],
        h[4], h[5], h[6], h[7],
        IV[0], IV[1], IV[2], IV[3],
        t0(t), t1(t), b, d,
    ]
    for i in range(7):
        m, v = e(m, v)
    return [
        v[0] ^ v[8], v[1] ^ v[9], v[2] ^ v[10], v[3] ^ v[11],
        v[4] ^ v[12], v[5] ^ v[13], v[6] ^ v[14], v[7] ^ v[15],
        v[8] ^ h[0], v[9] ^ h[1], v[10] ^ h[2], v[11] ^ h[3],
        v[12] ^ h[4], v[13] ^ h[5], v[14] ^ h[6], v[15] ^ h[7],
    ]

def words(bytes: bytearray) -> [int]:
    if len(bytes) < BLOCK_LENGTH:
        bytes.insert(BLOCK_LENGTH - len(bytes), 0)
    return [int.from_bytes(bytes[i: i + 4], "little") for i in range(0, len(bytes), 4)]

class Output:
    input_chaining_value: [int]
    block: [int]
    block_length: int
    counter: int
    flags: int

    def __init__(self, input_chaining_value: [int], block: [int], block_length: int, counter, flags):
        self.input_chaining_value = input_chaining_value
        self.block = block
        self.block_length = block_length
        self.counter = counter
        self.flags = flags

    def chaining_value(self) -> [int]:
        return compress(
            self.input_chaining_value,
            self.block,
            self.counter,
            self.block_length,
            self.flags,
        )[:8]

    def root_output_bytes(self, output_length: int) -> bytes:
        output_bytes = bytearray()
        t = 0
        while t < output_length:
            output = compress(self.input_chaining_value, self.block, t // 64, self.block_length, self.flags | ROOT)
            for word in output:
                word_bytes = word.to_bytes(4, "little")
                take = min(len(word_bytes), output_length - t)
                output_bytes.extend(word_bytes[:take])
                t += take
        return output_bytes

class ChunkState:
    chaining_value: [int]
    chunk_counter: int
    buffer: bytearray
    buffer_length: int
    flags: int
    blocks_compressed: int

    def __init__(self, chaining_value: [int], chunk_counter: int, flags: int):
        self.chaining_value = chaining_value
        self.buffer = bytearray(BLOCK_LENGTH)
        self.buffer_length = 0
        self.chunk_counter = chunk_counter
        self.flags = flags
        self.blocks_compressed = 0

    def length(self) -> int:
        return BLOCK_LENGTH * self.blocks_compressed + self.buffer_length

    def fill_buffer(self, input_bytes: bytearray) -> bytearray:
        want = BLOCK_LENGTH - self.buffer_length
        take = min(want, len(input_bytes))
        self.buffer[self.buffer_length : self.buffer_length + take] = input_bytes[:take]
        self.buffer_length += take
        return input_bytes[take:]

    def start_flag(self) -> int:
        return CHUNK_START if (self.blocks_compressed == 0) else 0

    def update(self, input_bytes: bytearray) -> None:
        while input_bytes:
            if self.buffer_length == BLOCK_LENGTH:
                self.chaining_value = compress(
                    self.chaining_value,
                    words(self.buffer),
                    self.chunk_counter,
                    BLOCK_LENGTH,
                    self.flags | self.start_flag(),
                )[:8]
                self.blocks_compressed += 1
                self.buffer = bytearray(BLOCK_LENGTH)
                self.buffer_length = 0
            input_bytes = self.fill_buffer(input_bytes)

    def output(self) -> Output:
        return Output(
            self.chaining_value,
            words(self.buffer),
            self.buffer_length,
            self.chunk_counter,
            self.flags | self.start_flag() | CHUNK_END
        )

def parent_cv(left_child_cv: [int], right_child_cv: [int], key_words: [int], flags: int) -> [int]:
    return Output(
        key_words,
        left_child_cv + right_child_cv,
        BLOCK_LENGTH, 0,
        PARENT | flags
    ).chaining_value()

class Hasher:
    key_words: [int]
    chunk_state: ChunkState
    cv_stack = [[int]]
    flags: int

    def __init__(self) -> None:
        self.key_words = IV
        self.chunk_state = ChunkState(IV, 0, 0)
        self.cv_stack = []
        self.flags = 0

    def add_chunk_chaining_value(self, new_cv: [int], total_chunks: int) -> None:
        while total_chunks & 1 == 0:
            new_cv = parent_cv(self.cv_stack.pop(), new_cv, self.key_words, self.flags)
            total_chunks >>= 1
        self.cv_stack.append(new_cv)

    def update(self, input_bytes: bytes) -> None:
        while len(input_bytes) > 0:
            if self.chunk_state.length() == CHUNK_LENGTH:
                chunk_cv = self.chunk_state.output().chaining_value()
                total_chunks = self.chunk_state.chunk_counter + 1
                self.add_chunk_chaining_value(chunk_cv, total_chunks)
                self.chunk_state = ChunkState(self.key_words, total_chunks, self.flags)

            want = CHUNK_LENGTH - self.chunk_state.length()
            take = min(want, len(input_bytes))
            self.chunk_state.update(input_bytes[:take])
            input_bytes = input_bytes[take:]

    def finalize(self, output_length = 32) -> bytes:
        output = self.chunk_state.output()
        remaining = len(self.cv_stack)
        while remaining > 0:
            remaining -= 1
            output = Output(
                self.key_words,
                self.cv_stack[remaining] + output.chaining_value(),
                BLOCK_LENGTH,
                0,
                PARENT | self.flags)
        return output.root_output_bytes(output_length)

class Blake3:
    @staticmethod
    def hash(data: bytes) -> str:
        hasher = Hasher()
        hasher.update(bytearray(data))
        return hasher.finalize().hex()

    @staticmethod
    def hash_from_file(file_name: str) -> str:
        hasher = Hasher()
        with open(file_name, "rb") as file:
            while True:
                data = file.read(2048)
                hasher.update(bytearray(data))
                if not data:
                    break
        return hasher.finalize().hex()
