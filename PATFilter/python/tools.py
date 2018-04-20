def files_from_dbs(dataset, ana02=True):
    # could use DBSAPI but this is easier
    url = '--url https://cmsdbsprod.cern.ch:8443/cms_dbs_ph_analysis_02_writer/servlet/DBSServlet' if ana02 else ''
    cmd = 'dbs search %(url)s --query "find file where dataset=%(dataset)s"' % locals()
    cmdout = os.popen(cmd).readlines()
    ret = [y.strip('\n') for y in cmdout if '.root' in y]
    if not ret:
        raise RuntimeError('no files for %s (ana02: %s) found. dbs command output:\n' % (dataset, ana02) + ''.join(cmdout))
    return ret
