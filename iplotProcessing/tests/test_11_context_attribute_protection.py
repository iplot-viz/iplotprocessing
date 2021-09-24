# Description: Tests safe protection of context attributes
# Author: Jaswant Sai Panchumarti

import unittest
from iplotProcessing.core import Context


class CtxAttribTesting(unittest.TestCase):

    def test_ctx_attributes(self):
        ctx = Context()
        self.assertRaises(AttributeError, ctx.__setattr__, "env", [])
        self.assertRaises(AttributeError, ctx.__setattr__, "env", 1)
