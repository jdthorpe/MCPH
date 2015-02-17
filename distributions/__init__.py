
class distributed(object):
	""" The base class for distributed values
	"""
    def __init__(self,parent): 
		self.parent = parent
		self.children = []
		self._seed = None

	def setValue(self,casecade=True):
		""" This value must be overridden by child classes
		"""
        raise RuntimeError('cannot instantiate an abstract class')

	def getValue(F)
		if self.value is None:
			self.setValue()
		return self.value

    # ----------------------------------------
    # STATUS properties 
    # ----------------------------------------
    # FIXME to be deprecated by eventOccuresBeforeAge
	def setSeed

	@property
    def seed(self): 
		return self._seed

	@seed.setter
	def seed(self,value):
		self._seed = value
		self.setValue()

    status = property(getStatus,) # no setter method!

