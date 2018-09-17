#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ALL DIRECTORY NAMES SHOULD END WITH '/'
RESULTS_DIR = "results/"                                    # On the grid
LOG_DIR = "log/"                                            # On the grid
SEND_RESULTS_PATH = "~/Thèse/these-achatali/src/Privacy/"   # Laptop
SEND_RESULTS_FOLDER = "results_igrida"  # Except here: no trailing / here 
MATLAB_FUN = "test_privacy"
UNAME = "achatali"                                          # To check your jobs with oarstat
LAPTOP = "tatlurutit"
nb_iterations = 80      # If the same number of iterations is required for all tuples of parameters

###############################################################
############## You should not modify below here ###############
###############################################################

BIN = "bin/wrapper_"+MATLAB_FUN+".sh"  # Binary, gen. with gen_simple_wrapper.sh
PATH_SEND_RESULTS = UNAME+"@"+LAPTOP+":"+SEND_RESULTS_PATH+SEND_RESULTS_FOLDER
# Parameter space

# Set of parameters, used to generate short name & check running scripts
PRMS_PREFIX = ['ds', 'pds', 'd', 'k', 'kdf', 'n', 'dnt', 'dsnr', 'ddec', 'snt', 'ssnr', 'ssp', 'thds']
# Full set of parameters, including the number of iterations necessary to call the function
PRMS_FULL = PRMS_PREFIX+['fn', 'its']
EXT = "csv"         # Extension

###############################################################

import os
import subprocess

#-----------------------------------------------------------------------
#-                      Some auxiliary functions                       -
#-----------------------------------------------------------------------

# Executes a shell command and returns the output without '\n' at the end.
def ex(c):
    return subprocess.check_output(c, shell=True).rstrip()

# Create directories if necessary
ex("mkdir -p "+RESULTS_DIR)
ex("mkdir -p "+LOG_DIR)

# Asks a y/n question, with No as default.
def ask_binary_question(q):
    answer = raw_input(q+" [y/N] ").lower()
    return (answer == 'yes' or answer == 'y')

# Generator of ranges with float step (to avoid using numpy which is not available on igrida-oar-launcher)
def drange(start, stop, step):
    r = start
    while r <= stop:
        yield r
        r += step

# Generates a "short" unique name without spaces for each tuple of parameters.
def gen_short_name(p):
    snl = map(lambda l: l+"-"+str(p[l]), PRMS_PREFIX)
    return '_'.join(snl)

# Generates the sequence that will be used for matching with oarstat result
# We do not include the number of iterations here
def gen_command_prefix(p):
    arg_l = map(lambda l: str(p[l]), PRMS_PREFIX)
    return BIN+" "+(' '.join(arg_l))

# The full command here, with the number of iterations
def gen_command(p):
    arg_l = map(lambda l: str(p[l]), PRMS_FULL)
    return BIN+" "+(' '.join(arg_l))

#-----------------------------------------------------------------------
#-                  This is a parameters generator!                    -
#-----------------------------------------------------------------------

# Parameter generator. Return tuples (parameters, short-name, file-name, command, prefix-command, nb_iterations).
def gen_params():
    # An array for each desired value in our parameter space
    ar_dk = [[10,10]]                  # Array of [d,k] couples
    ar_n = [128*2**e for e in range(0,13)] # 13 -> ~1 million
    # print ar_n
    # ar_n = [128*2**e for e in range(3,4)]
    # ar_kdf = [2,6,10]                              # m = kdf*k*d
    ar_kdf = [10]                              # m = kdf*k*d
    ar_dataset = ['GMM']

    use_sketches_d_sparsity = 0
    # Just change manually depending on what you want to try
    if 0:
        ar_data_noise_type = ['Gaussian', 'Laplacian']
        ar_data_SNR = [i for i in drange(1, 10, 1)]+[i for i in drange(12, 30, 2)]
        # ar_data_noise_deconvolution = [0];
        ar_data_noise_deconvolution = [1, 0]
        ar_sketches_sparsity = [0]
        ar_sketches_noise_type = ['None']
        ar_sketches_SNR = [0]
        ar_param_dataset = [2.5]
    elif 0:
        ar_data_noise_type = ['None']
        ar_data_SNR = ['Inf']
        ar_data_noise_deconvolution = [0]
        ar_sketches_sparsity = [0]
        ar_sketches_noise_type = ['Gaussian', 'Laplacian']
        ar_sketches_SNR = [i for i in drange(-21, 19, 2)]
        ar_param_dataset = [1.5]
        ar_n = [16*2**e for e in range(0,15)]
    elif 1:
        ar_data_noise_type = ['None']
        ar_data_SNR = ['Inf']
        ar_data_noise_deconvolution = [0]
        # ar_sketches_sparsity = [0.1, 0.2]
        # ar_sketches_sparsity = [0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.98, 0.99]
        sc = [1., 2., 3., 6.]
        # tmp = [x/100. for x in sc]+[x/10. for x in sc]+sc+[x*10. for x in sc]+100
        tmp = [x/100. for x in sc]+[x/10. for x in sc]+sc+[x*10. for x in sc]+[100]
        ar_sketches_sparsity = [1.-x/100. for x in tmp]
        # ar_sketches_sparsity = [0.01]

        # ar_sketches_d_sparsity = [float(x)/10 for x in range(20,1,-1)]+[float(x)/100 for x in range(9,1,-1)]
        use_sketches_d_sparsity = 1
        ar_sketches_noise_type = ['None']
        ar_sketches_SNR = [0]
        ar_param_dataset = [2.5]
    else:
        ar_data_noise_type = ['None']
        ar_data_SNR = ['Inf']
        ar_data_noise_deconvolution = [0]
        # ar_sketches_sparsity = [0.1, 0.2]
        ar_sketches_sparsity = [0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.98, 0.99]
        ar_sketches_noise_type = ['None']
        ar_sketches_SNR = [0]
        ar_param_dataset = [2.5]

    nb_threads = 0
    
    for [d,k] in ar_dk:
        for kdf in ar_kdf:
            m = k*d*kdf
            for n in ar_n:
                for data_noise_type in ar_data_noise_type:
                    for data_SNR in ar_data_SNR:
                        for data_noise_deconvolution in ar_data_noise_deconvolution:
                            # if use_sketches_d_sparsity>0:
                                # ar_sketches_sparsity = ar_sketches_d_sparsity 
                                # ar_sketches_sparsity = [float(m-c*d)/m for c in ar_sketches_d_sparsity]

                            for sketches_sparsity in ar_sketches_sparsity:
                                for sketches_noise_type in ar_sketches_noise_type:
                                    for sketches_SNR in ar_sketches_SNR:
                                        for param_dataset in ar_param_dataset:
                                            p = {"ds": 'GMM', "pds": param_dataset, "d": d, "k": k, "kdf": kdf, "n": n, "dnt": data_noise_type, "dsnr": data_SNR, "ddec": data_noise_deconvolution, "snt": sketches_noise_type, "ssnr": sketches_SNR, "ssp": sketches_sparsity, "thds": nb_threads, "its": nb_iterations}
                                            sn = gen_short_name(p)
                                            fn = RESULTS_DIR+sn+"."+EXT
                                            p['sn'] = sn
                                            p['fn'] = fn
                                            cmd = gen_command(p)
                                            pcmd = gen_command_prefix(p)
                                            yield (p, sn, fn, cmd, pcmd, nb_iterations)

# Returns the number of result lines in [fn], or 0 if the file does not exist.
def get_lines(fn):
    if os.path.isfile(fn):
        cmd = "wc -l %s | cut -f 1 -d ' '" % fn
        nb_lines = int(ex(cmd))
        if nb_lines>0:
            nb_lines = nb_lines-1   # Do not count the header line
    else:
        nb_lines = 0
    return nb_lines

# Makes a first loop on the parameter space to compute the number of jobs,
# and check if some results have already been computed.
def collect_data(submitted_commands):
    nb_total = 0
    nb_missing = 0
    nb_incomplete = 0
    nb_planned = 0           # A planned job can be "missing" or "incomplete" as well!
    nbl_total = 0
    nbl_computed = 0
    for (p, sn, fn, cmd, pcmd, its) in gen_params():
        # print sn
        nb_total = nb_total + 1
        nbl_total = nbl_total + its
        nb_lines = get_lines(fn)
        nbl_computed = nbl_computed + nb_lines
        if nb_lines == 0:
            nb_missing = nb_missing + 1
        if nb_lines > 0 and nb_lines < its:
            # print "nb_lines = "+str(nb_lines)+"/"+str(its)
            nb_incomplete = nb_incomplete + 1
        planned = check_job(pcmd, submitted_commands)
        if planned:
            nb_planned = nb_planned + 1
    p_missing = int(nb_missing / float(nb_total) * 100)
    p_incomplete = int(nb_incomplete / float(nb_total) * 100)
    pl_missing = int((nbl_total - nbl_computed) / float(nbl_total) * 100)
    p_planned = int(nb_planned / float(nb_missing + nb_incomplete) * 100)
    nb_relaunch = nb_incomplete + nb_missing - nb_planned       # Relaunch if missing
    return (nb_total, nb_missing, nb_incomplete, nb_relaunch, p_missing, p_incomplete, pl_missing, p_planned)

def ask_send_results(q="Should I send the results to your laptop"):
    send = ask_binary_question(q+" (path is '"+str(PATH_SEND_RESULTS)+"') ?")
    if send:
        # print "Well, this is actually not implemented yet. The programmer must have been lazy."
        rsync_cmd = "rsync -avz -e 'ssh' "+RESULTS_DIR+" "+PATH_SEND_RESULTS
        ex(rsync_cmd)

# Generates the job "wrapper" command, i.e. including 'oarsub'
def gen_wrapper_command(cmd, sn, nb_cores, max_duration_hours):
    out = "log/"
    # Generate outputs
    outn = LOG_DIR+sn+"_%jobid%.out"
    errn = LOG_DIR+sn+"_%jobid%.err"
    # Generate wrappper command
    # The name cannot be longer than 100 on IGRIDA
    return "oarsub -l /nodes=1/core="+str(nb_cores)+",walltime="+str(max_duration_hours)+":00:00 -n "+sn[0:100]+" -O "+outn+" -E "+errn+" '"+cmd+"'"

def get_jobs():
    running = ex("oarstat -u "+UNAME+" -f | grep command | cut -d' ' -f7-")
    # running is the list of commands, 1 command per line
    return running

# Returns if [pcmd] is already running or waiting to be launched.
def check_job(pcmd, running):
    return pcmd in running

def compute_ressources(p):
    mem_gb = (p['d']*p['n']*8*1.5)      # 1.5*dataset size
    # This is a rough approximation, the memory/core depends on the cluster!
    if mem_gb>2:
        nb_cores = 2
    elif mem_gb>4:
        nb_cores = 8
    else:
        nb_cores = 12
    max_duration_hours = 4
    return (nb_cores, max_duration_hours)

def res_oarsub(res):
    return ("Generate a job key" in res)

def print_infos(nb_total, p_missing, p_incomplete, p_planned, pl_missing):
    print "Total number of jobs: "+str(nb_total)+"."
    print "Missing files: "+str(p_missing)+"%."
    print "Incomplete files: "+str(p_incomplete)+"%."
    print "From these missing or incomplete, "+str(p_planned)+"% are already running or planned."
    print "Missing lines: "+str(pl_missing)+"%."
    
#-----------------------------------------------------------------------
#-                  This is where the magic happens!                   -
#-----------------------------------------------------------------------
def launch():
    submitted_commands = get_jobs()
    (nb_total, nb_missing, nb_incomplete, nb_relaunch, p_missing, p_incomplete, pl_missing, p_planned) = collect_data(submitted_commands)
    print "=================================================="
    print "=                    Welcome!                    ="
    print "=================================================="
    if nb_relaunch>0:
        currently_running = 0
        if nb_relaunch == nb_total:
            print "Well well well, looks like there are no results yet."
            b = ask_binary_question("You're about to launch "+str(nb_total)+" scripts. Proceed?")
            if not b:
                exit(0)
        else:
            print_infos(nb_total, p_missing, p_incomplete, p_planned, pl_missing)
            print "------------------------------"
            b = ask_binary_question("You're about to relaunch "+str(nb_relaunch)+" scripts. Proceed?")
            if not b:
                exit(0)
        # This is where we actually submit the jobs
        for (p, sn, fn, cmd, pcmd, its) in gen_params():
            nbl = get_lines(fn)
            nbl_to_compute = its - nbl
            planned = check_job(pcmd, submitted_commands)
            if nbl_to_compute>0 and not planned: # then we actually need to do something…
                (nb_cores, max_duration_hours) = compute_ressources(p)
                wcmd = gen_wrapper_command(cmd, sn, nb_cores, max_duration_hours)
                # print "'"+wcmd+"' must run."
                res = ex(wcmd)
                if not res_oarsub(res):
                    print res
                else:
                    print "[OK] "+sn
        if nb_relaunch<nb_total:
            ask_send_results("Should I send intermediate results to your laptop")
    else:
        print "Nothing to do!"
        if nb_missing+nb_incomplete == 0:
            print "Your experimental results are all available, what are you waiting for?"
            ask_send_results()
        else:
            print "------------------------------"
            print_infos(nb_total, p_missing, p_incomplete, p_planned, pl_missing)
            print "------------------------------"
            print "Some jobs are still running or planned though."
            ask_send_results("Should I send intermediate results to your laptop")

launch()

#cmd="oarsub -l /nodes=1/core=$nb_cores,walltime=$time_hours:00:00 -p \"cluster = '$cluster' AND host<>'igrida11-16.irisa.fr'\" -O $outn -E $errn '$call'"
#cmd="oarsub -l /nodes=1/core=$nb_cores,walltime=$time_hours:00:00 -p 'mem_node > $mem_gb*1024' -p \"cluster = '$cluster'\" -O $outn -E $errn '$call'"
