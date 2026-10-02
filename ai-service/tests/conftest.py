import sys
from unittest.mock import MagicMock

# Globally mock heavy ML libraries before any test modules are collected.
# This prevents PyTorch from crashing the test suite or taking up 1GB of RAM.
sys.modules['torch'] = MagicMock()
sys.modules['sentence_transformers'] = MagicMock()
sys.modules['fastembed'] = MagicMock()
