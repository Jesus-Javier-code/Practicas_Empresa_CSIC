import unittest
from pathlib import Path

# === CONFIGURACIÓN ===
# Establece el directorio base del proyecto
project_root = Path(__file__).resolve().parent
tests_dir = project_root / "A04_tests"

# === EJECUTAR TODOS LOS TESTS ===
def run_all_tests():
    print("=== RUNNING UNIT TESTS ===\n")
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=str(tests_dir), pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if result.wasSuccessful():
        print("\n=== ALL TESTS PASSED ===")
    else:
        print("\n=== SOME TESTS FAILED ===")


if __name__ == "__main__":
    run_all_tests()