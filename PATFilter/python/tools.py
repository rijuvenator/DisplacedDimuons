import sys


def files_from_dbs(dataset, ana02=True):
    # could use DBSAPI but this is easier
    url = '--url https://cmsdbsprod.cern.ch:8443/cms_dbs_ph_analysis_02_writer/servlet/DBSServlet' if ana02 else ''
    cmd = 'dbs search %(url)s --query "find file where dataset=%(dataset)s"' % locals()
    cmdout = os.popen(cmd).readlines()
    ret = [y.strip('\n') for y in cmdout if '.root' in y]
    if not ret:
        raise RuntimeError('no files for %s (ana02: %s) found. dbs command output:\n' % (dataset, ana02) + ''.join(cmdout))
    return ret

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.
    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).
    The "answer" return value is one of "yes" or "no".
    """

    valid = {"yes":True,   "y":True,  "ye":True,
             "no":False,     "n":False}
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "\
"(or 'y' or 'n').\n")

