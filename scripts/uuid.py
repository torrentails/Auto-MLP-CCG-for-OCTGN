#-----------------------------------------------------------------------
# UUID objects (universally unique identifiers) according to RFC 4122
# Condensed version for use in Auto MLP CCG for OCTGN
# Original author: Ka-Ping Yee <ping@zesty.ca>
# The original source can be found here: http://python.org/pypi/uuid/
#-----------------------------------------------------------------------
class UUID(object):
    def __init__(self, bytes=None, version=None):
        if bytes is not None:
            if len(bytes) != 16:
                raise ValueError('bytes is not a 16-char string')
            int = long(('%02x'*16) % tuple(map(ord, bytes)), 16)
        if version is not None:
            if not 1 <= version <= 5:
                raise ValueError('illegal version number')
            # Set the variant to RFC 4122.
            int &= ~(0xc000 << 48L)
            int |= 0x8000 << 48L
            # Set the version number.
            int &= ~(0xf000 << 64L)
            int |= version << 76L
        self.__dict__['int'] = int

    def __cmp__(self, other):
        if isinstance(other, UUID):
            return cmp(self.int, other.int)
        return NotImplemented

    def __hash__(self):
        return hash(self.int)

    def __int__(self):
        return self.int

    def __repr__(self):
        return 'UUID(%r)' % str(self)

    def __setattr__(self, name, value):
        raise TypeError('UUID objects are immutable')

    def __str__(self):
        hex = '%032x' % self.int
        return '%s-%s-%s-%s-%s' % (
            hex[:8], hex[8:12], hex[12:16], hex[16:20], hex[20:])

    def get_bytes(self):
        bytes = ''
        for shift in range(0, 128, 8):
            bytes = chr((self.int >> shift) & 0xff) + bytes
        return bytes

    bytes = property(get_bytes)

    def get_bytes_le(self):
        bytes = self.bytes
        return (bytes[3] + bytes[2] + bytes[1] + bytes[0] +
                bytes[5] + bytes[4] + bytes[7] + bytes[6] + bytes[8:])

    bytes_le = property(get_bytes_le)

    def get_fields(self):
        return (self.time_low, self.time_mid, self.time_hi_version,
                self.clock_seq_hi_variant, self.clock_seq_low, self.node)

    fields = property(get_fields)

    def get_time_low(self):
        return self.int >> 96L

    time_low = property(get_time_low)

    def get_time_mid(self):
        return (self.int >> 80L) & 0xffff

    time_mid = property(get_time_mid)

    def get_time_hi_version(self):
        return (self.int >> 64L) & 0xffff

    time_hi_version = property(get_time_hi_version)

    def get_clock_seq_hi_variant(self):
        return (self.int >> 56L) & 0xff

    clock_seq_hi_variant = property(get_clock_seq_hi_variant)

    def get_clock_seq_low(self):
        return (self.int >> 48L) & 0xff

    clock_seq_low = property(get_clock_seq_low)

    def get_time(self):
        return (((self.time_hi_version & 0x0fffL) << 48L) |
                (self.time_mid << 32L) | self.time_low)

    time = property(get_time)

    def get_clock_seq(self):
        return (((self.clock_seq_hi_variant & 0x3fL) << 8L) |
                self.clock_seq_low)

    clock_seq = property(get_clock_seq)

    def get_node(self):
        return self.int & 0xffffffffffff

    node = property(get_node)

    def get_hex(self):
        return '%032x' % self.int

    hex = property(get_hex)

    def get_urn(self):
        return 'urn:uuid:' + str(self)

    urn = property(get_urn)

    def get_variant(self):
        if not self.int & (0x8000 << 48L):
            return RESERVED_NCS
        elif not self.int & (0x4000 << 48L):
            return RFC_4122
        elif not self.int & (0x2000 << 48L):
            return RESERVED_MICROSOFT
        else:
            return RESERVED_FUTURE

    variant = property(get_variant)

    def get_version(self):
        # The version bits are only meaningful for RFC 4122 UUIDs.
        if self.variant == RFC_4122:
            return int((self.int >> 76L) & 0xf)

    version = property(get_version)

def uuid4():
    """Generate a random UUID."""
    ##rewrite to use .NET's Random()
    random = Random()
    bytes = [chr(random.Next(256)) for i in range(16)]
    return UUID(bytes=bytes, version=4)