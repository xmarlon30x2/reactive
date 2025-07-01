import unittest
from unittest.mock import MagicMock, patch
from reactive.test_utils.expect.text import ExpectText
from reactive.data_structures import Box, Point, Size, Style, Char

class TestExpectText(unittest.TestCase):
    def setUp(self):
        # Configuración completa del mock
        self.mock_expect = MagicMock()
        self.mock_expect.size = Size(rows=24, columns=80)
        self.mock_expect.screen = "Line 1\nLine 2\nLine 3"
        self.mock_expect.terminal = MagicMock()
        
        # Configurar el box principal
        self.mock_expect.box = Box(
            point=Point(0, 0),
            size=self.mock_expect.size
        )
        
        # Configurar rectángulo simulado
        self.mock_rect = [
            [Char('H', Style.default()), Char('e', Style.default()), 
             Char('l', Style.default()), Char('l', Style.default()), 
             Char('o', Style.default())],
            [Char('W', Style.default()), Char('o', Style.default()), 
             Char('r', Style.default()), Char('l', Style.default()), 
             Char('d', Style.default())]
        ]
        self.mock_expect.terminal.get_rect.return_value = self.mock_rect
        
        # Crear instancia bajo prueba
        self.box = Box(point=Point(row=1, column=2), size=Size(rows=2, columns=5))
        self.text_area = ExpectText(_expect=self.mock_expect, _box=self.box)

    def test_text_property(self):
        with patch(
            'reactive.test_utils.expect.text.get_text_from_rect', 
            return_value="Hello\nWorld"
        ) as mock_get_text:
            text = self.text_area.text
            self.assertEqual(text, "Hello\nWorld")
            self.mock_expect.terminal.get_rect.assert_called_with(box=self.box)
            mock_get_text.assert_called_with(self.mock_rect)

    def test_equal(self):
        with patch.object(
            self.text_area, '_get_text', return_value="Test content"
        ):
            self.text_area.equal("Test content")
            
            with self.assertRaises(AssertionError) as cm:
                self.text_area.equal("Wrong content")
            self.assertIn(
                'Expected text to equal "Wrong content", but got "Test content"',
                str(cm.exception)
            )

    # Patrón similar para otros métodos de texto:
    # - not_equal
    # - contains
    # - not_contains
    # - startswith
    # - endswith
    # - count
    # - match
    # - not_match

    def test_subarea_from_box(self):
        sub_box = Box(point=Point(row=0, column=0), size=Size(rows=1, columns=3))
        sub_area = self.text_area.subarea(box=sub_box)
        
        self.assertEqual(sub_area.box.point, Point(row=1, column=2))
        self.assertEqual(sub_area.box.size, Size(rows=1, columns=3))

    def test_subarea_from_coords(self):
        sub_area = self.text_area.subarea(row=1, column=1, rows=1, columns=2)
        
        self.assertEqual(sub_area.box.point, Point(row=2, column=3))
        self.assertEqual(sub_area.box.size, Size(rows=1, columns=2))

    def test_at_position_validation(self):
        # Configurar posición actual
        self.text_area._box = Box( # type: ignore
            point=Point(row=10, column=20), 
            size=Size(rows=1, columns=1)
        )
        
        # Casos exitosos
        self.text_area.at(row=10, column=20)
        self.text_area.at(point=Point(row=10, column=20))
        self.text_area.at(row=10)
        self.text_area.at(column=20)
        
        # Caso fallido (fila incorrecta)
        with self.assertRaises(AssertionError) as cm:
            self.text_area.at(row=11)
        self.assertIn(
            'Posición esperada: (fila=11, columna=20)', 
            str(cm.exception)
        )
        
        # Caso fallido (columna incorrecta)
        with self.assertRaises(AssertionError) as cm:
            self.text_area.at(column=21)
        self.assertIn(
            'Posición esperada: (fila=10, columna=21)', 
            str(cm.exception)
        )

    def test_row(self):
        row_area = self.text_area.row(1)
        self.assertEqual(row_area.box.point, Point(row=2, column=2))
        self.assertEqual(row_area.box.size, Size(rows=1, columns=5))
        
        with self.assertRaises(AssertionError):
            self.text_area.row(2)  # Fuera de rango

    def test_below(self):
        below_area = self.text_area.below(rows=3)
        self.assertEqual(below_area.box.point, Point(row=3, column=2))
        self.assertEqual(below_area.box.size, Size(rows=3, columns=5))

    # Patrón similar para:
    # - test_above
    # - test_back
    # - test_forward

    def test_style_methods(self):
        # Configurar estilos de prueba
        style = Style.new(
            bold=True,
            color="#ff0000",
        )
        chars = [
            (Point(0, 0), Char('H', style)),
            (Point(0, 1), Char('e', style))
        ]
        
        # Crear un mock para _iter_chars
        mock_iter = MagicMock(return_value=chars)
        self.text_area._iter_chars = mock_iter # type: ignore
        
        # Estos deben pasar
        self.text_area.bold(True)
        self.text_area.color("#ff0000")
        self.text_area.italic(False)
        
        # Probar falla en estilo - debe lanzar AssertionError
        with self.assertRaises(AssertionError) as cm:
            self.text_area.underline(True)
        self.assertIn('tuviera el underline="True"', str(cm.exception))
        
        # Verificar que se llamó a _iter_chars
        self.assertEqual(mock_iter.call_count, 4)

    def test_styled_method(self):
        # Configurar estilos de prueba
        style = Style.new(
            bold=True,
            color="#ff0000",
        )
        chars = [
            (Point(0, 0), Char('H', style)),
            (Point(0, 1), Char('e', style))
        ]
        
        # Crear un mock para _iter_chars
        mock_iter = MagicMock(return_value=chars)
        self.text_area._iter_chars = mock_iter # type: ignore
        
        # Esto debe pasar
        self.text_area.styled(
            bold=True,
            color="#ff0000",
        )
        
        # Esto debe fallar - debe lanzar AssertionError
        with self.assertRaises(AssertionError):
            self.text_area.styled(
                bold=True,
                color="blue"  # Color incorrecto
            )
            
        # Verificar que se llamó a _iter_chars
        self.assertEqual(mock_iter.call_count, 10)

    def test_find(self):
        with patch(
            'reactive.test_utils.expect.text.find_box',
            return_value=Box(point=Point(0, 0), size=Size(1, 5))
        ) as mock_find_box:
            result = self.text_area.find("Hello")
            self.assertEqual(
                result.box, 
                Box(point=Point(0, 0), size=Size(1, 5))
            )
            
            mock_find_box.return_value = None
            with self.assertRaises(AssertionError) as cm:
                self.text_area.find("Python")
            self.assertIn(
                'Expected text to contain "Python"', 
                str(cm.exception)
            )

if __name__ == '__main__':
    unittest.main()
