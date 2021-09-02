import unittest
from iplotProcessing.core import Context


class CtxAliasTesting(unittest.TestCase):

    def test_ctx_alias(self):
        ctx = Context()

        ctx.updateAlias("ds1", "CS-XWIG002-I", "cs002i")
        ctx.updateAlias("ds1", "CS-XWIG024-I", "cs024i")
        ctx.updateAlias("ds2", "ASD-123", 'ds2asdrel', pulsenb="1300/2", ts_start=1000, ts_end=1005, ts_format="relative", dec_samples=100, nbp=1000)
        ctx.updateAlias("ds2", "ASD-123", 'ds2asdabs', pulsenb="1300/2", ts_start=1000, ts_end=1005, ts_format="absolute", dec_samples=100, nbp=1000)
        ctx.updateAlias("ds2", "ASD-123", 'ds2asdabs500', pulsenb="1300/2", ts_start=1000, ts_end=1005, ts_format="absolute", dec_samples=100, nbp=500)
        ctx.env.update({"ds2asdabs500_dup": "ds2asdabs500"})
        self.assertEqual(ctx.env.get("cs002i"), "1f7e627690fe9fac32d16332ab2ef7e3")
        self.assertEqual(ctx.env.get("cs024i"), "ffb9e8d694ef3c91910c84b7b6294f36")
        self.assertEqual(ctx.env.get("ds2asdrel"), "f341164eb070c499fab3a4eb2575fa7c")
        self.assertEqual(ctx.env.get("ds2asdabs"), "f594798a9b2cb9b61f29d252aefcf34e")
        self.assertEqual(ctx.env.get("ds2asdabs500"), "25f11b361066f2b9be3184ed7e7c6b3a")
        self.assertEqual(ctx.env.get("ds2asdabs500_dup"), "ds2asdabs500")
        

        # alias to an alias
        ctx.env.update({"cs24i": "cs024i"})
        self.assertEqual(ctx.env.get("cs24i"), "cs024i")
