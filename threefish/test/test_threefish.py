from unittest import TestCase
from threefish import Threefish
from skein import threefish

class TestThreefish(TestCase):
    def test_small_data(self):
        key = b"key of 32,64 or 128 bytes length"
        tweak = b"tweak: 16 bytes "
        plaintext = b"block of data,same length as key"
        print("Plaintext")
        print(f"{plaintext}\n")

        library_threefish = threefish(key, tweak)
        implemented_threefish = Threefish(key, tweak)

        expected_result = library_threefish.encrypt_block(plaintext)
        actual_result = implemented_threefish.encrypt_block(plaintext)
        print("Encrypted plaintext")
        print(f"Expected: {expected_result}")
        print(f"Actual: {actual_result}\n")

        expected_result = library_threefish.decrypt_block(expected_result)
        actual_result = implemented_threefish.decrypt_block(actual_result)
        print("Decrypted ciphertext")
        print(f"Expected: {expected_result}")
        print(f"Actual: {actual_result}\n")

    def test_large_data(self):
        key = bytes("k" * 128, "utf-8")
        tweak = bytes("t" * 16, "utf-8")

        library_threefish = threefish(key, tweak)
        implemented_threefish = Threefish(key, tweak)

        with open("1MB.bin", "rb") as file:
            while True:
                plaintext = file.read(128)
                if not plaintext:
                    break
                expected_result = library_threefish.encrypt_block(plaintext)
                actual_result = implemented_threefish.encrypt_block(plaintext)
                self.assertEqual(expected_result, actual_result)

                expected_result = library_threefish.decrypt_block(expected_result)
                actual_result = implemented_threefish.decrypt_block(actual_result)
                self.assertEqual(expected_result, actual_result)
