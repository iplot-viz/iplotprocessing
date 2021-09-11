import unittest
from iplotProcessing.core import Context


class CtxAliasTesting(unittest.TestCase):

    def test_ctx_alias(self):
        ctx = Context()

        ctx.env.update_alias("ds1", "CS-XWIG002-I", "cs002i")
        ctx.env.update_alias("ds1", "CS-XWIG024-I", "cs024i")
        self.assertEqual(ctx.env.get("cs002i"), "015ecc4c72536cacf3351d9b0f67031d")
        self.assertEqual(ctx.env.get("cs024i"), "78f1ac48159ca4114abadaf61b547171")

        # alias to an alias
        ctx.env.update({"cs24i": "cs024i"})
        self.assertEqual(ctx.env.get("cs24i"), "cs024i")
