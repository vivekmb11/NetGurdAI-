"""Root conftest.py ensures the project root is on sys.path for all test modules."""
import sys
import os

# Add project root to Python path so 'from app import ...' works in tests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
