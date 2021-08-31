from iplotProcessing.translators.datasources.iplotdataobj import IplotDataObjTranslator
from iplotProcessing.translators.datasources.emulated import EmulatedTranslator

class Translator:
    def new(kind="emulated"):
        if kind == "emulated":
            return EmulatedTranslator()
        elif kind in ["codacuda", "imasuda"]:
            return IplotDataObjTranslator()
