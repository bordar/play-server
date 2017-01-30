import sys
import os.path

# parse the command line
scriptName = os.path.basename(sys.argv[0])
if len(sys.argv) < 3:
	print 'Usage:\n\t%s <input file> <output file>' % scriptName
	sys.exit(1)
inputFile, outputFile = sys.argv[1:]

# initialize
inputData = file(inputFile, 'rb').read()

preprocessorMacro = '__%s_H__' % os.path.splitext(os.path.basename(inputFile))[0].upper()

result = '// generated by %s from %s\n' % (scriptName, os.path.basename(inputFile))
result += '#ifndef %s\n' % preprocessorMacro
result += '#define %s\n\n' % preprocessorMacro

structName = None
for curLine in inputData.split('\n'):
	# strip comments
	commentPos = curLine.find('//')
	if commentPos >= 0:
		curLine = curLine[:commentPos]
	
	# ignore empty lines
	if len(curLine.strip()) == 0:
		continue
		
	if curLine[0] != '\t':
		# handle struct name
		if structName != None:
			result += '\n#define sizeof_%s (%d)\n\n' % (structName, (curPos + 7) / 8)
			
		structName = curLine.strip()
		result += '// %s\n' % structName	
		result += 'typedef unsigned char %s_t;\n\n' % structName
		curPos = 0
		continue
		
	# handle struct field
	(fieldName, bitCount) = map(lambda x: x.strip(), curLine.split(':'))
	bitCount = int(bitCount)
	endPos = curPos + bitCount
	getter = ''
	setter = ''
	while curPos < endPos:
		# calculate field info
		byteIndex = curPos / 8
		nextByteBoundary = (byteIndex + 1) * 8
		nextPos = min(nextByteBoundary, endPos)
		byteStartPos = curPos - byteIndex * 8
		byteEndPos = nextPos - byteIndex * 8
		getBitsMask = (1 << (byteEndPos - byteStartPos)) - 1
		shiftedGetBitsMask = getBitsMask << (8 - byteEndPos)
		bitsLeft = endPos - nextPos
		shift = 8 - byteEndPos - bitsLeft
		
		# build getter
		curGetter = '((x)[%d])' % byteIndex
		if shiftedGetBitsMask != 0xff:
			curGetter = '(%s & 0x%02x)' % (curGetter, shiftedGetBitsMask)
		if shift > 0:
			curGetter = '(%s >> %d)' % (curGetter, shift)
		elif shift < 0:
			curGetter = '(%s << %d)' % (curGetter, -shift)
		if len(getter) > 0:
			getter += ' | '
		getter += curGetter
		
		# build setter
		curSetter = '(x)[%d] = ' % byteIndex
		if shiftedGetBitsMask != 0xff:
			curSetter += '(((x)[%d]) & 0x%02x) | ' % (byteIndex, (~shiftedGetBitsMask) & 0xff)
		newValue = '(v)'
		if shift > 0:
			newValue = '(%s << %d)' % (newValue, shift)
		elif shift < 0:
			newValue = '(%s >> %d)' % (newValue, -shift)
		newValue = '(%s & 0x%02x)' % (newValue, shiftedGetBitsMask)		
		curSetter += newValue
		setter += curSetter + '; '
		
		curPos = nextPos
	
	# output the getter and setter
	result += '#define %s_get_%s(x) (%s)\n' % (structName, fieldName, getter)
	result += '#define %s_set_%s(x, v) { %s}\n' % (structName, fieldName, setter)
	curPos = endPos

if structName != None:
	result += '\n#define sizeof_%s (%d)\n\n' % (structName, (curPos + 7) / 8)
	
result += '#endif // %s\n' % preprocessorMacro

file(outputFile, 'wb').write(result)
