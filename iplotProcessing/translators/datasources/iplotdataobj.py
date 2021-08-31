from iplotProcessing.core.signal import Signal

class IplotDataObjTranslator:
    @staticmethod
    def translate(srcDobj, dstSig: Signal):
        dstSig.data_primary = srcDobj.ydata
        dstSig.data_primary_unit = srcDobj.yunit
        dstSig.time = srcDobj.xdata
        dstSig.time_unit = srcDobj.xunit
