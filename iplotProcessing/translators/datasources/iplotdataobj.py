from iplotProcessing.core.signal import Signal

class IplotDataObjTranslator:
    @staticmethod
    def translate(srcDobj, dstSig: Signal):
        if srcDobj.ydata is not None:
            dstSig.data_primary = srcDobj.ydata
        dstSig.data_primary_unit = srcDobj.yunit
        if srcDobj.xdata is not None:
            dstSig.time = srcDobj.xdata
        dstSig.time_unit = srcDobj.xunit
