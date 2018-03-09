# this works for a tuple OR 3 arguments
def SPStr(*args):
	if len(args) == 3:
		return '{}_{}_{}'.format(*args)
	elif len(args) == 1:
		return '{}_{}_{}'.format(*args[0])


