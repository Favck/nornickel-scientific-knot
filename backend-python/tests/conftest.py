import sys
from unittest.mock import MagicMock

# Мокаем тяжеловесную библиотеку sentence_transformers для тестов
sys.modules['sentence_transformers'] = MagicMock()
