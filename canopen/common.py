import logging


logger = logging.getLogger(__name__)


class Variable(object):

    def __init__(self, od):
        self.od = od
        self.bits = Bits(self)

    def get_data(self):
        raise NotImplementedError()

    def set_data(self, data):
        raise NotImplementedError()

    @property
    def data(self):
        if self.od.access_type == "wo":
            logger.warning("Variable is write only")
        return self.get_data()

    @data.setter
    def data(self, data):
        if "w" not in self.od.access_type:
            logger.warning("Variable is read only")
        self.set_data(data)

    @property
    def raw(self):
        value = self.od.decode_raw(self.data)
        text = "Value of %s (0x%X:%d) is %s" % (
            self.od.name, self.od.index,
            self.od.subindex, value)
        if value in self.od.value_descriptions:
            text += " (%s)" % self.od.value_descriptions[value]
        logger.debug(text)
        return value

    @raw.setter
    def raw(self, value):
        logger.debug("Writing %s (0x%X:%d) = %s",
                     self.od.name, self.od.index,
                     self.od.subindex, value)
        self.data = self.od.encode_raw(value)

    @property
    def phys(self):
        value = self.od.decode_phys(self.data)
        logger.debug("Value of %s (0x%X:%d) is %s %s",
                     self.od.name, self.od.index,
                     self.od.subindex, value, self.od.unit)
        return value

    @phys.setter
    def phys(self, value):
        logger.debug("Writing %s (0x%X:%d) = %s",
                     self.od.name, self.od.index,
                     self.od.subindex, value)
        self.data = self.od.encode_phys(value)

    @property
    def desc(self):
        value = self.od.decode_desc(self.data)
        logger.debug("Description of %s (0x%X:%d) is %s",
                     self.od.name, self.od.index,
                     self.od.subindex, value)
        return value

    @desc.setter
    def desc(self, desc):
        logger.debug("Setting description of %s (0x%X:%d) to %s",
                     self.od.name, self.od.index,
                     self.od.subindex, desc)
        self.data = self.od.encode_desc(desc)


class Bits(object):

    def __init__(self, variable):
        self.variable = variable

    def _get_bits(self, key):
        if isinstance(key, slice):
            bits = range(key.start, key.stop, key.step)
        elif isinstance(key, int):
            bits = [key]
        else:
            bits = key
        return bits

    def __getitem__(self, key):
        return self.variable.od.decode_bits(self.variable.data,
            self._get_bits(key))

    def __setitem__(self, key, value):
        self.variable.data = self.variable.od.encode_bits(
            self.variable.data, self._get_bits(key), value)