def hexdump(src, length=16):
	result = []
	digits = 4 if isinstance(src, str) else 2
	for i in range(0, len(src), length):
		s = src[i:i+length]
		hexa = " ".join(map("{0:0>2X}".format, src))
		text = "".join([chr(x) if 0x20 <= x < 0x7F else "." for x in s])
		result.append("%04X   %-*s   %s" % (i, length*(digits + 1), hexa, text))
	return "\n".join(result)
