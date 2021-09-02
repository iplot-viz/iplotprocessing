import argparse
import os
import pandas as pd
import numpy as np
from iplotProcessing.core import Context, Processor
from iplotProcessing.example.emulatedDataAccess import DataAccess
from iplotLogging import setupLogger as sl

logger = sl.get_logger("iplotProcessing-Example", "DEBUG")
defaultExampleFile = os.path.join(os.path.dirname(__file__), "example_inp.csv")


def main():
    parser = argparse.ArgumentParser(
        description="Example usage of iplotProcessing.")
    parser.add_argument("--input", "-i", help="Input csv file.",
                        required=False, default=defaultExampleFile)
    args = parser.parse_args()

    # In order to use processing methods, initialize a context that
    # manages various processors within a global key-value based environment.
    ctx = Context()
    da = DataAccess()

    # Input is provided in csv format.
    # The columns named 'DS', 'Variable' must be present.
    inp_file = args.input
    contents = pd.read_csv(inp_file)

    # For each row, create a processor if stackId is non zero
    for i in range(contents.count()['DS']):
        p = Processor()
        params = {
            "pulsenb": contents["PulseNumber"][i],
            "dec_samples": contents["Samples"][i],
            "ts_start": contents["StartTime"][i],
            "ts_end": contents["EndTime"][i],
            "ts_format": "relative" if np.isnan(contents["StartTime"][i]) or np.isnan(contents["EndTime"][i]) else "absolute"
        }
        p.setParams(contents["DS"][i], contents["Variable"][i], **params)

        # In order to access and share global aliases, register it
        # with the previously created global context.
        ctx.register(p)

        # Update alias if declared
        alias = contents["Alias"][i]
        if isinstance(alias, str):
            ctx.updateAlias(p.dataSource, p.inputExpr,
                            contents["Alias"][i], **params)

        # Now, populate the environment, i.e, initialize key-value pairs.
        # The 'value' is an empty 'Signal' instance
        ctx.refresh()

        # Now, emulate data access and set the fetched contents as input data for processing
        for proc in ctx.processors.values():
            for varName in proc.varNames:
                dobj = da.getData(proc.dataSource, varName)
                ctx.setInputData(dobj, proc.dataSource, varName, **proc.params)

    # Now query all processors.
    for i in range(contents.count()['DS']):

        # Get processor by DS and Variable names
        dataSource = contents["DS"][i]
        inputExpr = contents["Variable"][i]

        params = {
            "pulsenb": contents["PulseNumber"][i],
            "dec_samples": contents["Samples"][i],
            "ts_start": contents["StartTime"][i],
            "ts_end": contents["EndTime"][i],
            "ts_format": "relative" if np.isnan(contents["StartTime"][i]) or np.isnan(contents["EndTime"][i]) else "absolute"
        }

        proc = ctx.getProcessor(dataSource, inputExpr, **params)
        assert(isinstance(proc, Processor))

        xdata = contents["x"][i]
        ydata = contents["y"][i]
        zdata = contents["z"][i]

        x = proc.compute(xdata)
        y = proc.compute(ydata)
        z = proc.compute(zdata)
