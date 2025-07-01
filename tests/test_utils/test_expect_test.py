import unittest
from unittest.mock import MagicMock, patch
from reactive.test_utils.expect.text import ExpectText
from reactive.data_structures import Box, Point, Size, Style, Char

class TestExpectText(unittest.TestCase):
    def setUp(self):
        # Mock de las dependencias
        self.mock_expect = MagicMock()
        self.mock_expect.size = Size(rows=24, columns=80)
        self.mock_expect.screen = "Line 1\nLine 2\nLine 3"
        self.mock_expect.terminal = MagicMock()
        
        # Configurar el mock para get_rect
        self.mock_rect = [
            [Char('H', Style.default()), Char('e', Style.default()), Char('l', Style.default()), Char('l', Style.default()), Char('o', Style.default())],
            [Char('W', Style.default()), Char('o', Style.default()), Char('r', Style.default()), Char('l', Style.default()), Char('d', Style.default())]
        ]
        self.mock_expect.terminal.get_rect.return_value = self.mock_rect
        
        # Crear una instancia base de ExpectText
        self.box = Box(point=Point(row=1, column=2), size=Size(rows=2, columns=5))
        self.text_area = ExpectText(_expect=self.mock_expect, _box=self.box)

    def test_initialization(self):
        self.assertEqual(self.text_area.box, self.box)
        self.assertEqual(self.text_area.size, Size(rows=2, columns=5))
        self.assertEqual(self.text_area.point, Point(row=1, column=2))

    def test_text_property(self):
        # Mockear get_text_from_rect
        with patch('src.tui.testing.text.get_text_from_rect') as mock_get_text:
            mock_get_text.return_value = "Hello\nWorld"
            text = self.text_area.text
            self.assertEqual(text, "Hello\nWorld")
            
            # Verificar llamadas
            self.mock_expect.terminal.get_rect.assert_called_with(box=self.box)
            mock_get_text.assert_called_with(self.mock_rect)

    def test_equal(self):
        with patch.object(self.text_area, 'text', new="Test content"):
            # Caso exitoso
            self.text_area.equal("Test content")
            
            # Caso fallido
            with self.assertRaises(AssertionError) as cm:
                self.text_area.equal("Wrong content")
            self.assertIn('Expected text to equal "Wrong content", but got "Test content"', str(cm.exception))

    def test_not_equal(self):
        with patch.object(self.text_area, 'text', new="Test content"):
            # Caso exitoso
            self.text_area.not_equal("Different content")
            
            # Caso fallido
            with self.assertRaises(AssertionError) as cm:
                self.text_area.not_equal("Test content")
            self.assertIn('Expected text to not be equal to "Test content"', str(cm.exception))

    def test_contains(self):
        with patch.object(self.text_area, 'text', new="Hello World"):
            # Caso exitoso
            self.text_area.contains("Hello", "World")
            
            # Caso fallido
            with self.assertRaises(AssertionError) as cm:
                self.text_area.contains("Python", "World")
            self.assertIn('Expected text to contain "Python"', str(cm.exception))

    def test_not_contains(self):
        with patch.object(self.text_area, 'text', new="Hello World"):
            # Caso exitoso
            self.text_area.not_contains("Python", "Java")
            
            # Caso fallido
            with self.assertRaises(AssertionError) as cm:
                self.text_area.not_contains("Hello", "Java")
            self.assertIn('Expected text to not contain "Hello"', str(cm.exception))

    def test_startswith(self):
        with patch.object(self.text_area, 'text', new="Hello World"):
            # Caso exitoso
            self.text_area.startswith("Hello")
            
            # Caso fallido
            with self.assertRaises(AssertionError) as cm:
                self.text_area.startswith("World")
            self.assertIn('Expected text to start with "World"', str(cm.exception))

    def test_endswith(self):
        with patch.object(self.text_area, 'text', new="Hello World"):
            # Caso exitoso
            self.text_area.endswith("World")
            
            # Caso fallido
            with self.assertRaises(AssertionError) as cm:
                self.text_area.endswith("Hello")
            self.assertIn('Expected text to end with "Hello"', str(cm.exception))

    def test_count(self):
        with patch.object(self.text_area, 'text', new="a a a"):
            # Caso exitoso
            self.text_area.count("a", 3)
            
            # Caso fallido
            with self.assertRaises(AssertionError) as cm:
                self.text_area.count("a", 2)
            self.assertIn('Expected 2 occurrences of "a"', str(cm.exception))

    def test_match(self):
        with patch.object(self.text_area, 'text', new="abc123"):
            # Caso exitoso
            self.text_area.match(r'\w+\d+')
            
            # Caso fallido
            with self.assertRaises(AssertionError) as cm:
                self.text_area.match(r'^\d+$')
            self.assertIn('Expected area to match regex', str(cm.exception))

    def test_not_match(self):
        with patch.object(self.text_area, 'text', new="abc123"):
            # Caso exitoso
            self.text_area.not_match(r'^\d+$')
            
            # Caso fallido
            with self.assertRaises(AssertionError) as cm:
                self.text_area.not_match(r'\w+\d+')
            self.assertIn('Expected area to not match regex', str(cm.exception))

    def test_subarea_from_box(self):
        sub_box = Box(point=Point(row=0, column=0), size=Size(rows=1, columns=3))
        sub_area = self.text_area.subarea(box=sub_box)
        
        # Verificar nueva posición absoluta
        self.assertEqual(sub_area.box.point, Point(row=1, column=2))
        self.assertEqual(sub_area.box.size, Size(rows=1, columns=3))

    def test_subarea_from_coords(self):
        sub_area = self.text_area.subarea(row=1, column=1, rows=1, columns=2)
        
        # Verificar nueva posición absoluta
        self.assertEqual(sub_area.box.point, Point(row=2, column=3))
        self.assertEqual(sub_area.box.size, Size(rows=1, columns=2))

    def test_at_position_validation(self):
        # Configurar posición actual
        self.text_area._box = Box(point=Point(row=10, column=20), size=Size(rows=1, columns=1)) # type: ignore
        
        # Casos exitosos
        self.text_area.at(row=10, column=20)
        self.text_area.at(point=Point(row=10, column=20))
        self.text_area.at(row=10)
        self.text_area.at(column=20)
        
        # Caso fallido (fila incorrecta)
        with self.assertRaises(AssertionError) as cm:
            self.text_area.at(row=11)
        self.assertIn('Posición esperada: (fila=11, columna=20)', str(cm.exception))
        
        # Caso fallido (columna incorrecta)
        with self.assertRaises(AssertionError) as cm:
            self.text_area.at(column=21)
        self.assertIn('Posición esperada: (fila=10, columna=21)', str(cm.exception))

    def test_row(self):
        row_area = self.text_area.row(1)
        self.assertEqual(row_area.box.point, Point(row=2, column=2))
        self.assertEqual(row_area.box.size, Size(rows=1, columns=5))
        
        # Verificar validación de fila
        with self.assertRaises(AssertionError):
            self.text_area.row(2)  # Fuera de rango

    def test_below(self):
        below_area = self.text_area.below(rows=3)
        self.assertEqual(below_area.box.point, Point(row=3, column=2))
        self.assertEqual(below_area.box.size, Size(rows=3, columns=5))

    def test_above(self):
        above_area = self.text_area.above(rows=1)
        self.assertEqual(above_area.box.point, Point(row=0, column=2))
        self.assertEqual(above_area.box.size, Size(rows=1, columns=5))

    def test_back(self):
        back_area = self.text_area.back(columns=2)
        self.assertEqual(back_area.box.point, Point(row=1, column=0))
        self.assertEqual(back_area.box.size, Size(rows=2, columns=2))

    def test_forward(self):
        forward_area = self.text_area.forward(columns=3)
        self.assertEqual(forward_area.box.point, Point(row=1, column=7))
        self.assertEqual(forward_area.box.size, Size(rows=2, columns=3))

    def test_style_methods(self):
        # Mockear _iter_chars
        style = Style(
            bold=True,
            color="#ff0000",
            blink=None,
            bgcolor=None,
            hidden=None,
            italic=None,
            reverse=None,
            underline=None,
            strike=None
        )
        chars = [
            (Point(0, 0), Char('H', style)),
            (Point(0, 1), Char('e', style))
        ]
        self.text_area._iter_chars = lambda: iter(chars) # type: ignore
        
        # Probar métodos de estilo
        self.text_area.bold(True)
        self.text_area.color("#ff0000")
        
        # Probar falla en estilo
        with self.assertRaises(AssertionError) as cm:
            self.text_area.italic(True)
        self.assertIn('tuviera el italic="True"', str(cm.exception))

    def test_styled_method(self):
        # Mockear _iter_chars
        style = Style(
            bold=True,
            color="#ff0000",
            blink=None,
            bgcolor=None,
            hidden=None,
            italic=None,
            reverse=None,
            underline=None,
            strike=None
        )
        chars = [
            (Point(0, 0), Char('H', style)),
            (Point(0, 1), Char('e', style))
        ]
        self.text_area._iter_chars = lambda: iter(chars) # type: ignore
        
        # Probar con estilo completo
        self.text_area.styled(
            bold=True,
            color="#ff0000",
            italic=False
        )
        
        # Probar falla en estilo
        with self.assertRaises(AssertionError):
            self.text_area.styled(
                bold=True,
                color="blue"  # Color incorrecto
            )

    def test_find(self):
        with patch('src.tui.testing.text.find_box') as mock_find_box:
            # Configurar caso exitoso
            found_box = Box(point=Point(row=0, column=0), size=Size(rows=1, columns=5))
            mock_find_box.return_value = found_box
            
            result = self.text_area.find("Hello")
            self.assertEqual(result.box, found_box)
            
            # Configurar caso fallido
            mock_find_box.return_value = None
            with self.assertRaises(AssertionError) as cm:
                self.text_area.find("Python")
            self.assertIn('Expected text to contain "Python"', str(cm.exception))

if __name__ == '__main__':
    unittest.main()
