import argparse
import os

from iplotProcessing.core import Context
from iplotProcessing.example.emulatedDataAccess import SignalAdapterStub
from iplotLogging import setupLogger as sl

logger = sl.get_logger("iplotProcessing-Example", "INFO")
defaultExampleFile = os.path.join(
    os.path.dirname(__file__), "example_inp_1.csv")


def main():
    parser = argparse.ArgumentParser(
        description="Example usage of iplotProcessing.")
    parser.add_argument("--input", "-i", help="Input csv file.",
                        required=False, default=defaultExampleFile)
    args = parser.parse_args()

    # In order to use processing methods, initialize a context that
    # manages various processors within a global key-value based environment.
    ctx = Context()

    # Input is provided in csv format.
    # The columns named 'DS', 'Variable' must be present.
    inp_file = args.input
    ctx.import_csv(inp_file, signal_class=SignalAdapterStub, delimiter=',', keep_default_na=False)
    
    # Now, populate the environment, i.e, initialize key-value pairs.
    ctx.build()

    a = ctx.evaluate("${ml0004}.time + 20000 * 365D")
    breakpoint()