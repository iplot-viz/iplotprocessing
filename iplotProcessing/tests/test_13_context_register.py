import unittest
from iplotProcessing.core import Context, Processor


class ProcCtxTesting(unittest.TestCase):

    def test_ctx_proc_register(self):
        ctx = Context()
        ctx.env = {"a": 1, "b": 2, "c": 3}
        p1 = Processor()
        p2 = Processor()
        ctx.register(p1)
        ctx.register(p2)
        self.assertDictEqual(ctx.env, p1.gEnv)
        self.assertDictEqual(ctx.env, p2.gEnv)

        ctx.env = {"s": 1, "t": 2, "u": 3}
        self.assertDictEqual(ctx.env, p1.gEnv)
        self.assertDictEqual(ctx.env, p2.gEnv)

        ctx.deRegister(p1)
        self.assertEqual(len(ctx.processors.items()), 1)
        ctx.deRegister(p2)
        self.assertEqual(len(ctx.processors.items()), 0)
