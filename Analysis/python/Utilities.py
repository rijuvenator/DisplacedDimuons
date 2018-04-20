# this works for a tuple OR 3 arguments
def SPStr(*args):
	if len(args) == 3:
		return '{}_{}_{}'.format(*args)
	elif len(args) == 1:
		return '{}_{}_{}'.format(*args[0])

# SignalPoint class
class SignalPoint(object):
	def __init__(self, *args, **kwargs):
		if len(args) == 3:
			self.SP = tuple(map(int,args))
		elif len(args) == 1:
			self.SP = tuple(map(int,args[0]))
		elif len(kwargs) == 3:
			self.SP = tuple(map(int,[kwargs['mH'],kwargs['mX'],kwargs['cTau']]))
		self.mH, self.mX, self.cTau = self.SP

	def SPStr(self):
		return '{}_{}_{}'.format(*self.SP)
