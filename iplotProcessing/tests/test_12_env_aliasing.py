# Description: Tests aliasing within an environment
# Author: Jaswant Sai Panchumarti

import unittest
from iplotProcessing.core import Context


class CtxAliasTesting(unittest.TestCase):

    def test_ctx_alias(self):
        ctx = Context()
        
        uid1 = ctx.env.construct_uid(data_source='ds1', name='CS-XWIG002-I')
        ctx.env.add_alias("cs002i", uid1)
        uid2 = ctx.env.construct_uid(data_source='ds1', name='CS-XWIG024-I')
        ctx.env.add_alias("cs024i", uid2)
        self.assertEqual(ctx.env.get("cs002i"), uid1)
        self.assertEqual(ctx.env.get("cs024i"), uid2)

        # alias to an alias
        ctx.env.update({"cs24i": "cs024i"})
        self.assertEqual(ctx.env.get("cs24i"), "cs024i")
