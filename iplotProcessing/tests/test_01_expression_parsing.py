# Copyright (c) 2020-2025 ITER Organization,
#               CS 90046
#               13067 St Paul Lez Durance Cedex
#               France
# Author IO
#
# This file is part of iplotprocessing module.
# iplotprocessing python module is free software: you can redistribute it and/or modify it under
# the terms of the MIT license.
#
# This file is part of ITER CODAC software.
# For the terms and conditions of redistribution or use of this software
# refer to the file LICENSE located in the top level directory
# of the distribution package
#


# Description: Tests the parser tool
# Author: Jaswant Sai Panchumarti

import unittest
import numpy as np
from iplotProcessing.common.errors import InvalidExpression
from iplotProcessing.tools import Parser


class TestExpressionParsing(unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.parser = Parser()

    def test_invalid_expressions(self) -> None:
        self.assertRaises(InvalidExpression, self.parser.set_expression, "${")
        self.assertRaises(InvalidExpression, self.parser.set_expression, "${${")
        self.assertRaises(InvalidExpression, self.parser.set_expression, "}")
        self.assertRaises(InvalidExpression, self.parser.set_expression, "}$")
        self.assertRaises(InvalidExpression, self.parser.set_expression, "}}")
        self.assertRaises(InvalidExpression, self.parser.set_expression, "${{")
        self.assertRaises(InvalidExpression, self.parser.set_expression, "$}")
        self.assertRaises(InvalidExpression, self.parser.set_expression, "${time")
        self.assertRaises(InvalidExpression, self.parser.set_expression, "time}")
        self.assertRaises(InvalidExpression, self.parser.set_expression, "{time}")
        self.assertRaises(InvalidExpression, self.parser.set_expression, "${{time}}")

    def test_vulnerabilities(self) -> None:
        self.assertRaises(InvalidExpression, self.parser.set_expression,
                          "for i in range(${t}):\n\tprint(i)")
        self.assertRaises(InvalidExpression, self.parser.set_expression,
                          "import sys, os\nif sys.platform == ${linux}:\n\t os.system('ls')")

    def test_eval_simple(self) -> None:
        expr = "sin(${x})"
        subst = {"x": 3.141592653589793 * 0.5}

        self.parser.set_expression(expr)
        self.parser.substitute_var(subst)
        self.parser.eval_expr()

        self.assertAlmostEqual(self.parser.result, 1.)

    def test_eval_complex(self) -> None:
        expr = "sin(${l}) + cos(${m}) + ${n}"
        subst = {"l": np.arange(0, 4, dtype=np.float64),
                 "m": np.arange(0, 40, 10, dtype=np.float64),
                 "n": 10.0}

        self.parser.set_expression(expr)
        self.parser.substitute_var(subst)
        self.parser.eval_expr()

        valid_result = np.frombuffer(
            b'\x00\x00\x00\x00\x00\x00&@\x1d\xca_\x80:\x01$@\x86@x\x90\x7f\xa2&@\xbf\x1c\x80\xed:\x97$@')
        for testVal, validVal in zip(self.parser.result, valid_result):
            self.assertAlmostEqual(testVal, validVal)

    def test_eval_wrong_complex(self) -> None:
        expr = "sin(${${l}}) + cos(${m}) + ${n}"
        self.assertRaises(InvalidExpression, self.parser.set_expression, expr)


if __name__ == "__main__":
    unittest.main()
