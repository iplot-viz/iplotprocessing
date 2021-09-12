from functools import partial
from io import StringIO

from iplotProcessing.core import Context, Signal
from iplotProcessing.example.emulatedDataAccess import SignalAdapterStub

import pandas as pd
import unittest
import base64

inp_file = """DS,Variable,Stack,Row span,Col span,Envelope,Alias,x,y,z,Samples,PulseNumber,StartTime,EndTime
emulated,CWS-SCSU-HR00:ML0002-LT-XI,1.1,,,1,cws2,${self}.time,${self}.data,${self}.data_secondary,100,13100/2,0,100
emulated,CWS-SCSU-HR00:ML0004-LT-XI,1.1,,,1,cws4,${self}.time,${self}.data,${self}.data_secondary,,,,
emulated,CWS-SCSU-HR00:ML0001-LT-XI,1.2,,,1,,${self}.time,${cws4}.data,${self}.data_secondary,10000,,9000,1000
emulated,CWS-SCSU-HR00:ML0003-LT-XI,1.2,,,1,,${self}.time,${cws2}.data + (${cws4}.data * 2),${self}.data_secondary,,14000/23,,
emulated,UTIL-HV-S22:TOTAL_POWER_LC13,1.3,,,1,,${self}.time,${self}.data,${self}.data_secondary,,32001,,
"""

valid_signal_data = {
    "0": {
        "x": "kixMDQAAAACTLEwNAAAAAJQsTA0AAAAAlSxMDQAAAACWLEwNAAAAAJcsTA0AAAAAmCxMDQAAAACZLEwNAAAAAJosTA0AAAAAmyxMDQAAAACcLEwNAAAAAJ0sTA0AAAAAnixMDQAAAACfLEwNAAAAAKAsTA0AAAAAoSxMDQAAAAA=",
        "y": "oixMDQAAAACjLEwNAAAAAKQsTA0AAAAApSxMDQAAAACmLEwNAAAAAKcsTA0AAAAAqCxMDQAAAACpLEwNAAAAAKosTA0AAAAAqyxMDQAAAACsLEwNAAAAAK0sTA0AAAAArixMDQAAAACvLEwNAAAAALAsTA0AAAAAsSxMDQAAAAA=",
        "z": "sixMDQAAAACzLEwNAAAAALQsTA0AAAAAtSxMDQAAAAC2LEwNAAAAALcsTA0AAAAAuCxMDQAAAAC5LEwNAAAAALosTA0AAAAAuyxMDQAAAAC8LEwNAAAAAL0sTA0AAAAAvixMDQAAAAC/LEwNAAAAAMAsTA0AAAAAwSxMDQAAAAA="
    },
    "1": {
        "x": "69Z9CQAAAADs1n0JAAAAAO3WfQkAAAAA7tZ9CQAAAADv1n0JAAAAAPDWfQkAAAAA8dZ9CQAAAADy1n0JAAAAAPPWfQkAAAAA9NZ9CQAAAAD11n0JAAAAAPbWfQkAAAAA99Z9CQAAAAD41n0JAAAAAPnWfQkAAAAA+tZ9CQAAAAA=",
        "y": "+9Z9CQAAAAD81n0JAAAAAP3WfQkAAAAA/tZ9CQAAAAD/1n0JAAAAAADXfQkAAAAAAdd9CQAAAAAC130JAAAAAAPXfQkAAAAABNd9CQAAAAAF130JAAAAAAbXfQkAAAAAB9d9CQAAAAAI130JAAAAAAnXfQkAAAAACtd9CQAAAAA=",
        "z": "C9d9CQAAAAAM130JAAAAAA3XfQkAAAAADtd9CQAAAAAP130JAAAAABDXfQkAAAAAEdd9CQAAAAAS130JAAAAABPXfQkAAAAAFNd9CQAAAAAV130JAAAAABbXfQkAAAAAF9d9CQAAAAAY130JAAAAABnXfQkAAAAAGtd9CQAAAAA="
    },
    "2": {
        "x": "PmvBCQAAAAA/a8EJAAAAAEBrwQkAAAAAQWvBCQAAAABCa8EJAAAAAENrwQkAAAAARGvBCQAAAABFa8EJAAAAAEZrwQkAAAAAR2vBCQAAAABIa8EJAAAAAElrwQkAAAAASmvBCQAAAABLa8EJAAAAAExrwQkAAAAATWvBCQAAAAA=",
        "y": "+9Z9CQAAAAD81n0JAAAAAP3WfQkAAAAA/tZ9CQAAAAD/1n0JAAAAAADXfQkAAAAAAdd9CQAAAAAC130JAAAAAAPXfQkAAAAABNd9CQAAAAAF130JAAAAAAbXfQkAAAAAB9d9CQAAAAAI130JAAAAAAnXfQkAAAAACtd9CQAAAAA=",
        "z": "XmvBCQAAAABfa8EJAAAAAGBrwQkAAAAAYWvBCQAAAABia8EJAAAAAGNrwQkAAAAAZGvBCQAAAABla8EJAAAAAGZrwQkAAAAAZ2vBCQAAAABoa8EJAAAAAGlrwQkAAAAAamvBCQAAAABra8EJAAAAAGxrwQkAAAAAbWvBCQAAAAA="
    },
    "3": {
        "x": "OtCgAQAAAAA70KABAAAAADzQoAEAAAAAPdCgAQAAAAA+0KABAAAAAD/QoAEAAAAAQNCgAQAAAABB0KABAAAAAELQoAEAAAAAQ9CgAQAAAABE0KABAAAAAEXQoAEAAAAARtCgAQAAAABH0KABAAAAAEjQoAEAAAAASdCgAQAAAAA=",
        "y": "mNpHIAAAAACb2kcgAAAAAJ7aRyAAAAAAodpHIAAAAACk2kcgAAAAAKfaRyAAAAAAqtpHIAAAAACt2kcgAAAAALDaRyAAAAAAs9pHIAAAAAC22kcgAAAAALnaRyAAAAAAvNpHIAAAAAC/2kcgAAAAAMLaRyAAAAAAxdpHIAAAAAA=",
        "z": "WtCgAQAAAABb0KABAAAAAFzQoAEAAAAAXdCgAQAAAABe0KABAAAAAF/QoAEAAAAAYNCgAQAAAABh0KABAAAAAGLQoAEAAAAAY9CgAQAAAABk0KABAAAAAGXQoAEAAAAAZtCgAQAAAABn0KABAAAAAGjQoAEAAAAAadCgAQAAAAA="
    },
    "4": {
        "x": "H6H5DQAAAAAgofkNAAAAACGh+Q0AAAAAIqH5DQAAAAAjofkNAAAAACSh+Q0AAAAAJaH5DQAAAAAmofkNAAAAACeh+Q0AAAAAKKH5DQAAAAApofkNAAAAACqh+Q0AAAAAK6H5DQAAAAAsofkNAAAAAC2h+Q0AAAAALqH5DQAAAAA=",
        "y": "L6H5DQAAAAAwofkNAAAAADGh+Q0AAAAAMqH5DQAAAAAzofkNAAAAADSh+Q0AAAAANaH5DQAAAAA2ofkNAAAAADeh+Q0AAAAAOKH5DQAAAAA5ofkNAAAAADqh+Q0AAAAAO6H5DQAAAAA8ofkNAAAAAD2h+Q0AAAAAPqH5DQAAAAA=",
        "z": "P6H5DQAAAABAofkNAAAAAEGh+Q0AAAAAQqH5DQAAAABDofkNAAAAAESh+Q0AAAAARaH5DQAAAABGofkNAAAAAEeh+Q0AAAAASKH5DQAAAABJofkNAAAAAEqh+Q0AAAAAS6H5DQAAAABMofkNAAAAAE2h+Q0AAAAATqH5DQAAAAA="
    }
}



class CtxRefreshTesting(unittest.TestCase):

    def test_ctx_refresh(self):
        ctx = Context()
        SignalAdapterStub.secret = 1000
        # Input is provided in csv format.
        # The columns named 'DS', 'Variable' must be present.
        table = pd.read_csv(StringIO(inp_file), delimiter=',', keep_default_na=False)
        ctx.import_dataframe(table, signal_class=SignalAdapterStub)

        # Now, populate the environment, i.e, initialize key-value pairs.
        ctx.build()

        # Now query all processors.
        test_data_dump = {}

        for i in range(table.count()['DS']):
            # Get processor by DS and Variable names
            dataSource = table["DS"][i]
            inputExpr = table["Variable"][i]

            params = {
                "pulsenb": table["PulseNumber"][i],
                "dec_samples": table["Samples"][i],
                "ts_start": table["StartTime"][i],
                "ts_end": table["EndTime"][i],
            }


            xdata = table["x"][i]
            ydata = table["y"][i]
            zdata = table["z"][i]

            if len(dataSource) and len(inputExpr):
                sig_hash = ctx.env.get_hash(dataSource, inputExpr)
            else:
                sig_hash = ''

            x = ctx.evaluate(xdata, sig_hash, **params)
            y = ctx.evaluate(ydata, sig_hash, **params)
            z = ctx.evaluate(zdata, sig_hash, **params)

            test_data_dump.update({i:
                                   {"x": base64.b64encode(x.tobytes()).decode('ascii'),
                                    "y": base64.b64encode(y.tobytes()).decode('ascii'),
                                    "z": base64.b64encode(z.tobytes()).decode('ascii')}})

        for kv1, kv2 in zip(test_data_dump.items(), valid_signal_data.items()):
            self.assertEqual(kv1[1], kv2[1])

        # Note: Copy the json's table to valid_signal_data defined above.
        # import json
        # with open("output.json", 'w') as f:
        #     json.dump(test_data_dump, f)


if __name__ == "__main__":
    unittest.main()
