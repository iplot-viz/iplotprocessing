import unittest
from iplotProcessing.core import Context


class CtxAliasTesting(unittest.TestCase):

    def test_ctx_alias(self):
        ctx = Context()

        ctx.update("cs002i", "CS-XWIG002-I")
        ctx.update("cs024i", "CS-XWIG024-I")
        self.assertEqual(ctx.env.get("cs002i"), "CS-XWIG002-I")
        self.assertEqual(ctx.env.get("cs024i"), "CS-XWIG024-I")

        # alias to an alias
        ctx.update("cs24i", "cs024i")
        self.assertEqual(ctx.env.get("cs24i"), "cs024i")
