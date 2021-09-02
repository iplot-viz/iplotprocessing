from io import StringIO
from iplotProcessing.core import Context, Processor
from iplotProcessing.example.emulatedDataAccess import DataAccess
import pandas as pd
import unittest
import base64

inp_file = """DS,Variable,Stack,Row span,Col span,Envelope,Alias,x,y,z
emulated,CWS-SCSU-HR00:ML0002-LT-XI,1.1,,,1,cws2,${self}.time,${self}.data,${self}.data_secondary
emulated,CWS-SCSU-HR00:ML0004-LT-XI,1.1,,,1,cws4,${self}.time,${self}.data,${self}.data_secondary
emulated,CWS-SCSU-HR00:ML0001-LT-XI,1.2,,,1,,${self}.time,${cws4}.data,${self}.data_secondary
emulated,CWS-SCSU-HR00:ML0003-LT-XI,1.2,,,1,,${self}.time,${cws2}.data + (${cws4}.data * 2),${self}.data_secondary
emulated,UTIL-HV-S22:TOTAL_POWER_LC13,1.3,,,1,,${self}.time,${self}.data,${self}.data_secondary
"""

valid_signal_data = {
    "0": {
        "data_primary": "oixMDQAAAACjLEwNAAAAAKQsTA0AAAAApSxMDQAAAACmLEwNAAAAAKcsTA0AAAAAqCxMDQAAAACpLEwNAAAAAKosTA0AAAAAqyxMDQAAAACsLEwNAAAAAK0sTA0AAAAArixMDQAAAACvLEwNAAAAALAsTA0AAAAAsSxMDQAAAAA=",
        "data_secondary": "sixMDQAAAACzLEwNAAAAALQsTA0AAAAAtSxMDQAAAAC2LEwNAAAAALcsTA0AAAAAuCxMDQAAAAC5LEwNAAAAALosTA0AAAAAuyxMDQAAAAC8LEwNAAAAAL0sTA0AAAAAvixMDQAAAAC/LEwNAAAAAMAsTA0AAAAAwSxMDQAAAAA=",
        "time": "kixMDQAAAACTLEwNAAAAAJQsTA0AAAAAlSxMDQAAAACWLEwNAAAAAJcsTA0AAAAAmCxMDQAAAACZLEwNAAAAAJosTA0AAAAAmyxMDQAAAACcLEwNAAAAAJ0sTA0AAAAAnixMDQAAAACfLEwNAAAAAKAsTA0AAAAAoSxMDQAAAAA=",
        "data_primary_unit": "C",
        "data_secondary_unit": "A",
        "time_unit": "ms",
        "x": "kixMDQAAAACTLEwNAAAAAJQsTA0AAAAAlSxMDQAAAACWLEwNAAAAAJcsTA0AAAAAmCxMDQAAAACZLEwNAAAAAJosTA0AAAAAmyxMDQAAAACcLEwNAAAAAJ0sTA0AAAAAnixMDQAAAACfLEwNAAAAAKAsTA0AAAAAoSxMDQAAAAA=",
        "y": "oixMDQAAAACjLEwNAAAAAKQsTA0AAAAApSxMDQAAAACmLEwNAAAAAKcsTA0AAAAAqCxMDQAAAACpLEwNAAAAAKosTA0AAAAAqyxMDQAAAACsLEwNAAAAAK0sTA0AAAAArixMDQAAAACvLEwNAAAAALAsTA0AAAAAsSxMDQAAAAA=",
        "z": "sixMDQAAAACzLEwNAAAAALQsTA0AAAAAtSxMDQAAAAC2LEwNAAAAALcsTA0AAAAAuCxMDQAAAAC5LEwNAAAAALosTA0AAAAAuyxMDQAAAAC8LEwNAAAAAL0sTA0AAAAAvixMDQAAAAC/LEwNAAAAAMAsTA0AAAAAwSxMDQAAAAA="
    },
    "1": {
        "data_primary": "+9Z9CQAAAAD81n0JAAAAAP3WfQkAAAAA/tZ9CQAAAAD/1n0JAAAAAADXfQkAAAAAAdd9CQAAAAAC130JAAAAAAPXfQkAAAAABNd9CQAAAAAF130JAAAAAAbXfQkAAAAAB9d9CQAAAAAI130JAAAAAAnXfQkAAAAACtd9CQAAAAA=",
        "data_secondary": "C9d9CQAAAAAM130JAAAAAA3XfQkAAAAADtd9CQAAAAAP130JAAAAABDXfQkAAAAAEdd9CQAAAAAS130JAAAAABPXfQkAAAAAFNd9CQAAAAAV130JAAAAABbXfQkAAAAAF9d9CQAAAAAY130JAAAAABnXfQkAAAAAGtd9CQAAAAA=",
        "time": "69Z9CQAAAADs1n0JAAAAAO3WfQkAAAAA7tZ9CQAAAADv1n0JAAAAAPDWfQkAAAAA8dZ9CQAAAADy1n0JAAAAAPPWfQkAAAAA9NZ9CQAAAAD11n0JAAAAAPbWfQkAAAAA99Z9CQAAAAD41n0JAAAAAPnWfQkAAAAA+tZ9CQAAAAA=",
        "data_primary_unit": "C",
        "data_secondary_unit": "A",
        "time_unit": "ms",
        "x": "69Z9CQAAAADs1n0JAAAAAO3WfQkAAAAA7tZ9CQAAAADv1n0JAAAAAPDWfQkAAAAA8dZ9CQAAAADy1n0JAAAAAPPWfQkAAAAA9NZ9CQAAAAD11n0JAAAAAPbWfQkAAAAA99Z9CQAAAAD41n0JAAAAAPnWfQkAAAAA+tZ9CQAAAAA=",
        "y": "+9Z9CQAAAAD81n0JAAAAAP3WfQkAAAAA/tZ9CQAAAAD/1n0JAAAAAADXfQkAAAAAAdd9CQAAAAAC130JAAAAAAPXfQkAAAAABNd9CQAAAAAF130JAAAAAAbXfQkAAAAAB9d9CQAAAAAI130JAAAAAAnXfQkAAAAACtd9CQAAAAA=",
        "z": "C9d9CQAAAAAM130JAAAAAA3XfQkAAAAADtd9CQAAAAAP130JAAAAABDXfQkAAAAAEdd9CQAAAAAS130JAAAAABPXfQkAAAAAFNd9CQAAAAAV130JAAAAABbXfQkAAAAAF9d9CQAAAAAY130JAAAAABnXfQkAAAAAGtd9CQAAAAA="
    },
    "2": {
        "data_primary": "TmvBCQAAAABPa8EJAAAAAFBrwQkAAAAAUWvBCQAAAABSa8EJAAAAAFNrwQkAAAAAVGvBCQAAAABVa8EJAAAAAFZrwQkAAAAAV2vBCQAAAABYa8EJAAAAAFlrwQkAAAAAWmvBCQAAAABba8EJAAAAAFxrwQkAAAAAXWvBCQAAAAA=",
        "data_secondary": "XmvBCQAAAABfa8EJAAAAAGBrwQkAAAAAYWvBCQAAAABia8EJAAAAAGNrwQkAAAAAZGvBCQAAAABla8EJAAAAAGZrwQkAAAAAZ2vBCQAAAABoa8EJAAAAAGlrwQkAAAAAamvBCQAAAABra8EJAAAAAGxrwQkAAAAAbWvBCQAAAAA=",
        "time": "PmvBCQAAAAA/a8EJAAAAAEBrwQkAAAAAQWvBCQAAAABCa8EJAAAAAENrwQkAAAAARGvBCQAAAABFa8EJAAAAAEZrwQkAAAAAR2vBCQAAAABIa8EJAAAAAElrwQkAAAAASmvBCQAAAABLa8EJAAAAAExrwQkAAAAATWvBCQAAAAA=",
        "data_primary_unit": "C",
        "data_secondary_unit": "A",
        "time_unit": "ms",
        "x": "PmvBCQAAAAA/a8EJAAAAAEBrwQkAAAAAQWvBCQAAAABCa8EJAAAAAENrwQkAAAAARGvBCQAAAABFa8EJAAAAAEZrwQkAAAAAR2vBCQAAAABIa8EJAAAAAElrwQkAAAAASmvBCQAAAABLa8EJAAAAAExrwQkAAAAATWvBCQAAAAA=",
        "y": "+9Z9CQAAAAD81n0JAAAAAP3WfQkAAAAA/tZ9CQAAAAD/1n0JAAAAAADXfQkAAAAAAdd9CQAAAAAC130JAAAAAAPXfQkAAAAABNd9CQAAAAAF130JAAAAAAbXfQkAAAAAB9d9CQAAAAAI130JAAAAAAnXfQkAAAAACtd9CQAAAAA=",
        "z": "XmvBCQAAAABfa8EJAAAAAGBrwQkAAAAAYWvBCQAAAABia8EJAAAAAGNrwQkAAAAAZGvBCQAAAABla8EJAAAAAGZrwQkAAAAAZ2vBCQAAAABoa8EJAAAAAGlrwQkAAAAAamvBCQAAAABra8EJAAAAAGxrwQkAAAAAbWvBCQAAAAA="
    },
    "3": {
        "data_primary": "StCgAQAAAABL0KABAAAAAEzQoAEAAAAATdCgAQAAAABO0KABAAAAAE/QoAEAAAAAUNCgAQAAAABR0KABAAAAAFLQoAEAAAAAU9CgAQAAAABU0KABAAAAAFXQoAEAAAAAVtCgAQAAAABX0KABAAAAAFjQoAEAAAAAWdCgAQAAAAA=",
        "data_secondary": "WtCgAQAAAABb0KABAAAAAFzQoAEAAAAAXdCgAQAAAABe0KABAAAAAF/QoAEAAAAAYNCgAQAAAABh0KABAAAAAGLQoAEAAAAAY9CgAQAAAABk0KABAAAAAGXQoAEAAAAAZtCgAQAAAABn0KABAAAAAGjQoAEAAAAAadCgAQAAAAA=",
        "time": "OtCgAQAAAAA70KABAAAAADzQoAEAAAAAPdCgAQAAAAA+0KABAAAAAD/QoAEAAAAAQNCgAQAAAABB0KABAAAAAELQoAEAAAAAQ9CgAQAAAABE0KABAAAAAEXQoAEAAAAARtCgAQAAAABH0KABAAAAAEjQoAEAAAAASdCgAQAAAAA=",
        "data_primary_unit": "C",
        "data_secondary_unit": "A",
        "time_unit": "ms",
        "x": "OtCgAQAAAAA70KABAAAAADzQoAEAAAAAPdCgAQAAAAA+0KABAAAAAD/QoAEAAAAAQNCgAQAAAABB0KABAAAAAELQoAEAAAAAQ9CgAQAAAABE0KABAAAAAEXQoAEAAAAARtCgAQAAAABH0KABAAAAAEjQoAEAAAAASdCgAQAAAAA=",
        "y": "mNpHIAAAAACb2kcgAAAAAJ7aRyAAAAAAodpHIAAAAACk2kcgAAAAAKfaRyAAAAAAqtpHIAAAAACt2kcgAAAAALDaRyAAAAAAs9pHIAAAAAC22kcgAAAAALnaRyAAAAAAvNpHIAAAAAC/2kcgAAAAAMLaRyAAAAAAxdpHIAAAAAA=",
        "z": "WtCgAQAAAABb0KABAAAAAFzQoAEAAAAAXdCgAQAAAABe0KABAAAAAF/QoAEAAAAAYNCgAQAAAABh0KABAAAAAGLQoAEAAAAAY9CgAQAAAABk0KABAAAAAGXQoAEAAAAAZtCgAQAAAABn0KABAAAAAGjQoAEAAAAAadCgAQAAAAA="
    },
    "4": {
        "data_primary": "L6H5DQAAAAAwofkNAAAAADGh+Q0AAAAAMqH5DQAAAAAzofkNAAAAADSh+Q0AAAAANaH5DQAAAAA2ofkNAAAAADeh+Q0AAAAAOKH5DQAAAAA5ofkNAAAAADqh+Q0AAAAAO6H5DQAAAAA8ofkNAAAAAD2h+Q0AAAAAPqH5DQAAAAA=",
        "data_secondary": "P6H5DQAAAABAofkNAAAAAEGh+Q0AAAAAQqH5DQAAAABDofkNAAAAAESh+Q0AAAAARaH5DQAAAABGofkNAAAAAEeh+Q0AAAAASKH5DQAAAABJofkNAAAAAEqh+Q0AAAAAS6H5DQAAAABMofkNAAAAAE2h+Q0AAAAATqH5DQAAAAA=",
        "time": "H6H5DQAAAAAgofkNAAAAACGh+Q0AAAAAIqH5DQAAAAAjofkNAAAAACSh+Q0AAAAAJaH5DQAAAAAmofkNAAAAACeh+Q0AAAAAKKH5DQAAAAApofkNAAAAACqh+Q0AAAAAK6H5DQAAAAAsofkNAAAAAC2h+Q0AAAAALqH5DQAAAAA=",
        "data_primary_unit": "C",
        "data_secondary_unit": "A",
        "time_unit": "ms",
        "x": "H6H5DQAAAAAgofkNAAAAACGh+Q0AAAAAIqH5DQAAAAAjofkNAAAAACSh+Q0AAAAAJaH5DQAAAAAmofkNAAAAACeh+Q0AAAAAKKH5DQAAAAApofkNAAAAACqh+Q0AAAAAK6H5DQAAAAAsofkNAAAAAC2h+Q0AAAAALqH5DQAAAAA=",
        "y": "L6H5DQAAAAAwofkNAAAAADGh+Q0AAAAAMqH5DQAAAAAzofkNAAAAADSh+Q0AAAAANaH5DQAAAAA2ofkNAAAAADeh+Q0AAAAAOKH5DQAAAAA5ofkNAAAAADqh+Q0AAAAAO6H5DQAAAAA8ofkNAAAAAD2h+Q0AAAAAPqH5DQAAAAA=",
        "z": "P6H5DQAAAABAofkNAAAAAEGh+Q0AAAAAQqH5DQAAAABDofkNAAAAAESh+Q0AAAAARaH5DQAAAABGofkNAAAAAEeh+Q0AAAAASKH5DQAAAABJofkNAAAAAEqh+Q0AAAAAS6H5DQAAAABMofkNAAAAAE2h+Q0AAAAATqH5DQAAAAA="
    }
}


class CtxRefreshTesting(unittest.TestCase):

    def test_ctx_refresh(self):
        ctx = Context()
        DataAccess.secret = 1000
        da = DataAccess()
        # Input is provided in csv format.
        # The columns named 'DS', 'Variable' must be present.
        contents = pd.read_csv(StringIO(inp_file))

        # For each row, create a processor if stackId is non zero
        for i in range(contents.count()['DS']):
            p = Processor()
            p.dataSource = contents["DS"][i]
            p.inputExpr = contents["Variable"][i]

            # In order to access and share global aliases, register it
            # with the previously created global context.
            ctx.register(p)

            # Update alias if declared
            alias = contents["Alias"][i]
            if isinstance(alias, str):
                ctx.updateAlias(p.dataSource, p.inputExpr, contents["Alias"][i])

        # Now, populate the environment, i.e, initialize key-value pairs.
        # The 'value' is an empty 'Signal' instance
        ctx.refresh()

        # Now, emulate data access and set the fetched contents as input data for processing
        for proc in ctx.processors.values():
            for varname in proc.varNames:
                dobj = da.getData(proc.dataSource, varname)
                ctx.setInputData(proc.dataSource, varname, dobj)

        # Now query all processors.
        test_data_dump = {}

        for i in range(contents.count()['DS']):

            # Get processor by DS and Variable names
            dataSource = contents["DS"][i]
            inputExpr = contents["Variable"][i]

            proc = ctx.getProcessor(dataSource, inputExpr)
            assert(isinstance(proc, Processor))

            xdata = contents["x"][i]
            ydata = contents["y"][i]
            zdata = contents["z"][i]

            x = proc.compute(xdata)
            y = proc.compute(ydata)
            z = proc.compute(zdata)

            test_data_dump.update({i:
                                   {"data_primary": base64.b64encode(proc.output.data_primary.tobytes()).decode('ascii'),
                                    "data_secondary": base64.b64encode(proc.output.data_secondary.tobytes()).decode('ascii'),
                                    "time": base64.b64encode(proc.output.time.tobytes()).decode('ascii'),
                                    "data_primary_unit": proc.output.data_primary_unit,
                                    "data_secondary_unit": proc.output.data_secondary_unit,
                                    "time_unit": proc.output.time_unit,
                                    "x": base64.b64encode(x.tobytes()).decode('ascii'),
                                    "y": base64.b64encode(y.tobytes()).decode('ascii'),
                                    "z": base64.b64encode(z.tobytes()).decode('ascii')}})

        for kv1, kv2 in zip(test_data_dump.items(), valid_signal_data.items()):
            self.assertEqual(kv1[1], kv2[1])

        # Note: Copy the json's contents to valid_signal_data defined above.
        # import json
        # with open("output.json", 'w') as f:
        #     json.dump(test_data_dump, f)

if __name__ == "__main__":
    unittest.main()
