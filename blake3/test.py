import unittest
import random
from string import ascii_lowercase
from blake3 import blake3
from blake import Blake3

class TestBlake3(unittest.TestCase):
    def test_empty_string(self):
        bytes = b""
        expected = blake3(bytes).digest().hex()
        actual = Blake3.hash(bytes)
        print("Empty string:")
        print(f"My: {actual}")
        print(f"Library: {expected}\n")
        self.assertEqual(expected, actual)

    def test_small_string(self):
        bytes = b"string for testing blake3 algorithm"
        expected = blake3(bytes).digest().hex()
        actual = Blake3.hash(bytes)
        print("Small string:")
        print(f"My: {actual}")
        print(f"Library: {expected}\n")
        self.assertEqual(expected, actual)

    def test_medium_string(self):
        from_string = bytes("".join(random.choice(ascii_lowercase) for _ in range(10240)).encode())
        expected = blake3(from_string).digest().hex()
        actual = Blake3.hash(from_string)
        self.assertEqual(expected, actual)

    def test_large_string(self):
        from_string = bytes("".join(random.choice(ascii_lowercase) for _ in range(100000)).encode())
        expected = blake3(from_string).digest().hex()
        actual = Blake3.hash(from_string)
        self.assertEqual(expected, actual)

    def test_large_file(self):
        file_name = "large.bin"
        actual = Blake3.hash_from_file(file_name)
        hasher = blake3()
        with open(file_name, "rb") as file:
            while True:
                data = file.read(2048)
                hasher.update(bytearray(data))
                if not data:
                    break
        expected = hasher.digest().hex()
        print("From big file:")
        print(f"My: {actual}")
        print(f"Library: {expected}\n")
        self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()
