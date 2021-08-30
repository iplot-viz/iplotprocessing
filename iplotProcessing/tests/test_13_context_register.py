import unittest
from iplotProcessing.core import Context, Processor


class CtxRegisterTesting(unittest.TestCase):

    def test_ctx_proc_register(self):
        ctx = Context()
        ctx.env.update({"a": 1, "b": 2, "c": 3})
        p1 = Processor()
        p1.sourceId = "ds1"
        p2 = Processor()
        p2.sourceId = "ds2"
        ctx.register(p1)
        ctx.register(p2)
        self.assertDictEqual(ctx.env, p1.gEnv)
        self.assertDictEqual(ctx.env, p2.gEnv)

        ctx.env.update({"s": 1, "t": 2, "u": 3})
        self.assertDictEqual(ctx.env, p1.gEnv)
        self.assertDictEqual(ctx.env, p2.gEnv)

        ctx.deRegister(p1)
        self.assertEqual(len(ctx.processors.items()), 1)
        ctx.deRegister(p2)
        self.assertEqual(len(ctx.processors.items()), 0)
