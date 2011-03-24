
class InterpretPlugin:
	"This is the base class for all interpret plugins."
	def __init__(self):
		""

	def getPluginName(self):
		return ''		

	def getCarving( self, fileName = ''):
		raise Exception('getCarving not implemented for "%s"' % getPluginName())
		return trianglemesh.TriangleMesh()

