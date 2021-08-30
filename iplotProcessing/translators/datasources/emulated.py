from iplotProcessing.core.signal import Signal

class DObj:
    data = None
    time = None
    time_unit = None
    data_units = None

class EmulatedTranslator:
    @staticmethod
    def translate(srcDobj: DObj, dstSig: Signal):
        dstSig.data_primary = srcDobj.data[0]
        dstSig.data_primary_unit = srcDobj.data_units[0]
        if len(srcDobj.data) == 2:
            dstSig.data_secondary = srcDobj.data[1]
            dstSig.data_secondary_unit = srcDobj.data_units[1]
        dstSig.time = srcDobj.time
        dstSig.time_unit = srcDobj.time_unit
