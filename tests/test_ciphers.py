import unittest

from app.core import caesar, xor, transposition
from app.core.steps import CipherError


class CaesarTests(unittest.TestCase):
    def test_latin_roundtrip(self):
        self.assertEqual(caesar.caesar("Hello, World!", 3), "Khoor, Zruog!")
        self.assertEqual(caesar.caesar("Khoor, Zruog!", 3, decrypt=True), "Hello, World!")

    def test_cyrillic_with_yo(self):
        self.assertEqual(caesar.caesar("Ёж", 1), "Жз")
        self.assertEqual(caesar.caesar("Я", 1), "А")

    def test_steps_count(self):
        self.assertEqual(len(caesar.caesar_steps("abc", 1)), 3)

    def test_empty(self):
        with self.assertRaises(CipherError):
            caesar.caesar_steps("", 1)


class XorTests(unittest.TestCase):
    def test_roundtrip_str_key(self):
        data = xor.encode_text("Привет")
        key = xor.parse_key("str", 0, "ключ")
        enc = xor.xor_bytes(data, key)
        self.assertEqual(xor.xor_bytes(enc, key), data)

    def test_steps(self):
        steps = xor.xor_steps(b"AB", bytes([0xFF]))
        self.assertEqual(len(steps), 16)
        self.assertEqual(steps[-1].data["output"], bytes([0x41 ^ 0xFF, 0x42 ^ 0xFF]))
        self.assertEqual(sum(1 for s in steps if s.major), 2)

    def test_hex_input(self):
        b, was_hex = xor.parse_input("4a 2F", allow_hex=True)
        self.assertEqual(b, bytes([0x4A, 0x2F]))
        self.assertTrue(was_hex)


class TranspositionTests(unittest.TestCase):
    def test_word_key(self):
        headers, ranks = transposition.parse_key("КЛЮЧ")
        self.assertEqual(ranks, [0, 1, 3, 2])  # К<Л<Ч<Ю

    def test_numeric_key(self):
        _, ranks = transposition.parse_key("3142")
        self.assertEqual(ranks, [2, 0, 3, 1])

    def test_roundtrip(self):
        enc = transposition.encrypt("ПРИВЕТМИР", "КЛЮЧ")
        self.assertEqual(len(enc), 12)
        self.assertEqual(transposition.decrypt(enc, "КЛЮЧ"), "ПРИВЕТМИР___")

    def test_known(self):
        # ключ 3142: столбцы читаются в порядке 2,4,1,3
        self.assertEqual(transposition.encrypt("ABCDEFGH", "3142"), "BFDHAECG")

    def test_bad_key(self):
        with self.assertRaises(CipherError):
            transposition.parse_key("3143")


if __name__ == "__main__":
    unittest.main()
