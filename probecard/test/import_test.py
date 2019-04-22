import unittest
import sys
class TestImports(unittest.TestCase):

    def test_main(self):
        sys.path.append("../../")
        import probecard
        print(probecard.GUI.five())

if __name__ == '__main__':
    unittest.main()
