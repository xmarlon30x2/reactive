from unittest import TestCase
from reactive.data_structures import Size

class TestSize(TestCase):
    def test_one_constructor(self):
        size = Size.one()
        self.assertEqual(size.rows, 1)
        self.assertEqual(size.columns, 1)

    def test_not_posible_compare(self):
        size = Size(rows=10, columns=30)
        
        with self.assertRaises(ValueError) as cm:
            _ = size > (2, )

        self.assertIn(
            'No se puede comparar',
            str(cm.exception)
        )
        
        with self.assertRaises(ValueError) as cm:
            _ = size < (2, )

        self.assertIn(
            'No se puede comparar',
            str(cm.exception)
        )
        
        with self.assertRaises(ValueError) as cm:
            _ = size >= (2, )

        self.assertIn(
            'No se puede comparar',
            str(cm.exception)
        )
        
        with self.assertRaises(ValueError) as cm:
            _ = size <= (2, )

        self.assertIn(
            'No se puede comparar',
            str(cm.exception)
        )

    def test_add(self):
        size1 = Size(rows=5, columns=10)
        size2 = Size(rows=2, columns=8)

        size3 = size1 + size2

        self.assertEqual(size3.columns, 18)
        self.assertEqual(size3.rows, 7)
        
        with self.assertRaises(ValueError) as cm:
            _ = size1 + (2, )

        self.assertIn(
            'No se puede sumar',
            str(cm.exception)
        )

    def test_sub(self):
        size1 = Size(rows=5, columns=10)
        size2 = Size(rows=2, columns=8)

        size3 = size1 - size2

        self.assertEqual(size3.columns, 2)
        self.assertEqual(size3.rows, 3)
        
        with self.assertRaises(ValueError) as cm:
            _ = size1 - (2, )

        self.assertIn(
            'No se puede restar',
            str(cm.exception)
        )
