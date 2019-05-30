import shlex

def split(line):
    return shlex.split(line.strip('\n'))

ENDOFLIST = '<<<\n'
SUPEREND  = '%%%\n'
HTML = {}
filledHTML = False

ORDER = []
VARS = {}
EXTRACOMMANDS = []

CURRENTVARS = None
CURRENTMODE = None
CURRENTNAME = None
CURRENTOBJMODE = None

with open('data.dat') as f:
    for line in f:
        if line == '\n': continue
        if line[0] == '#': continue

        # first fill the HTML dictionary
        if not filledHTML:
            if 'PYTHON HTML DICT' in line: continue
            if line == ENDOFLIST:
                filledHTML = True
                continue
            key, val = split(line)
            HTML[key] = val

        # this means a new variable will be declared
        # keep track of the order and what the names are and what "mode"
        # i.e. am I filling a list? an object? running a command?
        if 'VAR' in line:
            data = split(line)[1:]
            ORDER.extend(data[::2])
            CURRENTVARS = data[::2]
            for var, mode in zip(data[::2], data[1::2]):
                VARS[var] = {'MODE':mode, 'DATA':None}
                CURRENTMODE = mode
                if mode == 'LIST':
                    VARS[var]['DATA'] = []
                elif mode == 'CMD':
                    VARS[var]['DATA'] = ''
                elif mode == 'OBJ':
                    VARS[var]['DATA'] = {}
            continue

        # tag for just adding a bunch of commands to the end
        if 'RUN' in line:
            CURRENTMODE = 'RUN'
            continue

        # list mode. this is a simple list. add onto each var and end with endoflist
        if CURRENTMODE == 'LIST':
            if line == ENDOFLIST:
                CURRENTVARS = None
                CURRENTMODE = None
                continue
            data = split(line)
            for var, val in zip(CURRENTVARS, data):
                VARS[var]['DATA'].append(val.format(**HTML))

        # cmd mode. var will be set to the cmd.
        if CURRENTMODE == 'CMD':
            if line == ENDOFLIST:
                CURRENTVARS = None
                CURRENTMODE = None
                continue
            for var in CURRENTVARS:
                if VARS[var]['DATA'] == '':
                    VARS[var]['DATA'] = line.strip('\n')
                    break

        # obj mode. var is an object. it has keys, whose values are lists and sublists.
        # currentvars is the names of the objects
        # currentname is which key we're processing
        # currentobjmode is the mode for the currentname
        # currentindex is used for substructure
        if CURRENTMODE == 'OBJ':
            if line == SUPEREND:
                CURRENTNAME = None
                CURRENTOBJMODE = None
                CURRENTINDEX = 0
                continue

            if 'NAME' in line:
                dummy, name, objmode = split(line)
                CURRENTNAME = name
                CURRENTOBJMODE = objmode
                CURRENTINDEX = 0
                for var in CURRENTVARS:
                    VARS[var]['DATA'][name] = []
                continue

            if CURRENTOBJMODE == '1:0':
                if line == ENDOFLIST: continue
                data = split(line)
                for var, val in zip(CURRENTVARS, data):
                    VARS[var]['DATA'][CURRENTNAME].append(val.format(**HTML))

            if CURRENTOBJMODE == '1:2' or CURRENTOBJMODE == '1:1' or CURRENTOBJMODE == '1:2:2':
                if line == ENDOFLIST:
                    CURRENTINDEX += 1
                    continue
                data = split(line)
                for var in CURRENTVARS:
                    if len(VARS[var]['DATA'][CURRENTNAME]) == CURRENTINDEX:
                        VARS[var]['DATA'][CURRENTNAME].append([])
                for var, val in zip(CURRENTVARS, data):
                    VARS[var]['DATA'][CURRENTNAME][CURRENTINDEX].append(val.format(**HTML))

        if CURRENTMODE == 'RUN':
            if line == ENDOFLIST:
                CURRENTVARS = None
                CURRENTMODE = None
                continue
            EXTRACOMMANDS.append(line.strip('\n'))

# takes a python list, makes a JS list string
def JSList(lst):
    return '[{}]'.format(', '.join(['"{}"'.format(i) for i in lst]))

# print it all out!
for var in ORDER:
    if VARS[var]['MODE'] == 'LIST':
        print 'var {} = {};'.format(var, JSList(VARS[var]['DATA']))
    if VARS[var]['MODE'] == 'CMD':
        print 'var {} = {};'.format(var, VARS[var]['DATA'])
    if VARS[var]['MODE'] == 'OBJ':
        print 'var {} = {{}};'.format(var)
        data = VARS[var]['DATA']
        for key in data:
            if type(data[key][0]) == str:
                print '{}["{}"] = {};'.format(var, key, JSList(data[key]))
            else:
                if len(data[key]) == 3:
                    listStrings = []
                    for lst in data[key][1:]:
                        listStrings.append(JSList(lst))
                    metaList = '[{}]'.format(', '.join(listStrings))
                    print '{}["{}"] = [{}, {}];'.format(var, key, JSList(data[key][0]), metaList)
                else:
                    listStrings = []
                    for lst in data[key]:
                        listStrings.append(JSList(lst))
                    print '{}["{}"] = [{}];'.format(var, key, ', '.join(listStrings))
for cmd in EXTRACOMMANDS:
    print cmd+';'
