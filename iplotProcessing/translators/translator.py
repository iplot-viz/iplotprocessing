from iplotProcessing.translators.datasources.codacuda import CodacUdaTranslator
from iplotProcessing.translators.datasources.imasuda import ImasUdaTranslator
from iplotProcessing.translators.datasources.emulated import EmulatedTranslator

class Translator:
    def new(kind="simulated"):
        if kind == "emulated":
            return EmulatedTranslator()
        elif kind == "codacuda":
            return CodacUdaTranslator()
        elif kind == "imasuda":
            return ImasUdaTranslator()
