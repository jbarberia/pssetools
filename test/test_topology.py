# coding: latin-1
import os
import tempfile
from pssetools.utils.topology import parse_boundaries


def test_parse_boundaries():
    content = """# Archivo de prueba de limites
8000 2620
LII 5016 8011 1
SYS 6006 8004 2
T3 100 200 300 1
"""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as tf:
        tf.write(content)
        temp_path = tf.name

    try:
        bus1, bus2, fronteras = parse_boundaries(temp_path)
        assert bus1 == 8000
        assert bus2 == 2620
        assert len(fronteras) == 3
        assert fronteras[0] == ["LII", 5016, 8011, "1"]
        assert fronteras[1] == ["SYS", 6006, 8004, "2"]
        assert fronteras[2] == ["T3", 100, 200, 300, "1"]
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
