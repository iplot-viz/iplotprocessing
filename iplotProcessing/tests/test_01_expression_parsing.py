import unittest
import numpy as np
from iplotProcessing.basicProcessing import exprProcessing, ProcParsingException


class TestExpressionParsing(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.parser = exprProcessing()

    def test_invalid_expressions(self) -> None:
        self.assertRaises(ProcParsingException, self.parser.setExpr, "${")
        self.assertRaises(ProcParsingException, self.parser.setExpr, "${${")
        self.assertRaises(ProcParsingException, self.parser.setExpr, "}")
        self.assertRaises(ProcParsingException, self.parser.setExpr, "}$")
        self.assertRaises(ProcParsingException, self.parser.setExpr, "}}")
        self.assertRaises(ProcParsingException, self.parser.setExpr, "${{")
        self.assertRaises(ProcParsingException, self.parser.setExpr, "$}")
        self.assertRaises(ProcParsingException, self.parser.setExpr, "${time")
        self.assertRaises(ProcParsingException, self.parser.setExpr, "time}")
        self.assertRaises(ProcParsingException, self.parser.setExpr, "{time}")
        self.assertRaises(ProcParsingException, self.parser.setExpr, "${{time}}")

    def test_vulnerabilities(self) -> None:
        self.assertRaises(ProcParsingException, self.parser.setExpr,
                          "for i in range(${t}):\n\tprint(i)")
        self.assertRaises(ProcParsingException, self.parser.setExpr,
                          "import sys, os\nif sys.platform == ${linux}:\n\t os.system('ls')")

    def test_eval_simple(self) -> None:
        expr = "sin(${x})"
        subst = {"x": 3.141592653589793 * 0.5}
        
        self.parser.setExpr(expr)
        self.parser.substituteExpr(subst)
        self.parser.evalExpr()
        
        self.assertAlmostEqual(self.parser.result, 1.)

    def test_eval_complex(self) -> None:
        expr = "sin(${l}) + cos(${m}) + ${n}"
        subst = {"l": np.arange(0, 4, dtype=np.float64),
                 "m": np.arange(0, 40, 10, dtype=np.float64),
                 "n": 10.0}
        
        self.parser.setExpr(expr)
        self.parser.substituteExpr(subst)
        self.parser.evalExpr()

        validResult = np.frombuffer(
            b'\x00\x00\x00\x00\x00\x00&@\x1d\xca_\x80:\x01$@\x86@x\x90\x7f\xa2&@\xbf\x1c\x80\xed:\x97$@')
        for testVal, validVal in zip(self.parser.result, validResult):
            self.assertAlmostEqual(testVal, validVal)

    def test_eval_WrongComplex(self) -> None:
        expr = "sin(${${l}}) + cos(${m}) + ${n}"
        subst = {"${l}": np.arange(0, 4, dtype=np.float64),
                 "m": np.arange(0, 40, 10, dtype=np.float64),
                 "n": 10.0}
        try:
            self.parser.setExpr(expr)
            self.parser.substituteExpr(subst)
            self.parser.evalExpr()
            validResult = np.frombuffer(
                b'\x00\x00\x00\x00\x00\x00&@\x1d\xca_\x80:\x01$@\x86@x\x90\x7f\xa2&@\xbf\x1c\x80\xed:\x97$@')
            for testVal, validVal in zip(self.parser.result, validResult):
                self.assertAlmostEqual(testVal, validVal)
        ##shall trigger an exception
        except ProcParsingException:
            pass




if __name__ == "__main__":
    unittest.main()
