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

# returns signal point lumi string, e.g. 4mu (125 GeV, 20 GeV, 13 mm)
def SPLumiStr(*args):
    if len(args) == 1:
        # suppose args[0] is a list of 4 arguments
        try:
            return '{} ({} GeV, {} GeV, {} mm)'.format(*args[0])
        # suppose args[0] is a list of 2 arguments
        except:
            return '{} ({} GeV, {} GeV, {} mm)'.format(args[0][0], *args[0][1])
    # suppose args is a list of 2 arguments
    elif len(args) == 2:
        return '{} ({} GeV, {} GeV, {} mm)'.format(args[0], *args[1])
    # suppose args is a list of 4 arguments
    elif len(args) == 4:
        return '{} ({} GeV, {} GeV, {} mm)'.format(*args)
