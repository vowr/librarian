import xml.parsers.expat, os

configs = {}

def getConfValue(confName, variable):
	global configs
	try:
		info = os.stat(confName)
	except OSError as e:
		raise AssertionError('Missing Config file: %s' % (e,))
	modTime = info.st_mtime
	config = None
	if confName in configs:
		config = configs[confName]
		if config and config.modtime >= modTime:
			config = None
	if not config:
		config = Config(confName, modTime)
		configs[confName] = config
	if variable in config.varVals:
		return config.varVals[variable]
#End  getConfValue()

class Config:
	def __init__(self, confName, modTime):
		self.modtime = modTime
		self.values = []
		self.variable = ''
		self.varVals = {}
		self.inAP = self.inAN = self.inCD = self.inVR = self.inVL = False
		try:
			f = open(confName, 'r')
			buf = f.read()
		except IOError as e:
			raise AssertionError('Missing Config file(%s): %s', (confName, e))
		p = xml.parsers.expat.ParserCreate('ASCII')
		p.StartElementHandler = self.start_element
		p.EndElementHandler = self.end_element
		p.CharacterDataHandler = self.char_data
		p.Parse(buf, 1)
	# End __init()

	# 3 handler functions
	def start_element(self, name, attrs):
		if name == 'Entity_Profile':
			self.inAP = True
		elif name == 'Application' and self.inAP:
			self.inAN = True
		elif name == 'ConfigurationItem' and self.inAP:
			self.inCD = True
		elif name == 'variable' and self.inAP and self.inCD:
			self.inVR = True
		elif name == 'value' and self.inAP and self.inCD:
			self.inVL = True
		else:
			raise AssertionError('Unexpected XML start element: ' + name)

	def end_element(self, name):
		if name == 'Entity_Profile':
			self.inAP = False
		elif name == 'Application' and self.inAP:
			self.inAN = False
		elif name == 'ConfigurationItem' and self.inAP:
			if self.variable == '':
				raise AssertionError('Missing variable')
			elif self.values == []:
				raise AssertionError('Missing values')
			self.inCD = False
			self.varVals[self.variable] = self.values
			self.variable = ''
			self.values = []
		elif name == 'variable' and self.inAP and self.inCD:
			self.inVR = False
		elif name == 'value' and self.inAP and self.inCD:
			self.inVL = False
		else:
			raise AssertionError('Unexpected XML end element: ' + name)

	def char_data(self, data):
		if self.inAN:
			file = data
		elif self.inVR:
			self.variable = str(data)
		elif self.inVL:
			self.values.append(str(data))
# End class Config

# print(getConfValue('vowr.conf', 'database'))
