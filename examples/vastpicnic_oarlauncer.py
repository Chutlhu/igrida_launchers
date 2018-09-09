#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ALL DIRECTORY NAMES SHOULD END WITH '/'
RESULTS_DIR = "./Results/"    # On the grid
LOG_DIR = "./Logs/"            # On the grid
SEND_RESULTS_PATH = "~/Documents/Code/" # Laptop
SEND_RESULTS_DIR = "./Results_IGRIDA/"  # Except here: no trailing / here

MATLAB_FUN = "generate_rir_dataset"  # script that launch matlab binary
UNAME = "ddicarlo"          # To check your jobs with oarstat
LAPTOP = "embuscade"

# HYPERPARAMETERS DEFINITIONS
shortname = 'vast'
final_dataset_size = 10e3
n_jobs = 200
dataset_size_per_job = int(final_dataset_size/n_jobs_per_task);

parameters_and_ranges = {
    "dataset_size" :  dataset_size_per_job
}

def condition_to_prune_the_param_space(param_dict):
    return True
    # if param_dict["do_realistic_room"] > 0      \
    #     and param_dict["other_walls_abs"] > 0   \
    #     and param_dict["south_wall_abs"] > 0:
    #     return True
    # return False


# PARAMETER SPACE
# Set of input parameters for each job
PRMS_NAMES = ["id", "dataset_size"]

### YOU SHOULD NOT MODIFY BELOW HERE ###
BIN = "./bin/" + MATLAB_FUN + ".sh"  # Binary
PATH_SEND_RESULTS = UNAME + "@" + LAPTOP + ":" + SEND_RESULTS_PATH+SEND_RESULTS_DIR

################################################################################

import os
import subprocess
from itertools import product
import signal

## SOME AUXILIARY FUNCTIONS

# usefull class that allows take actions after a timeout
class timeout:
    def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message
    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)
    def __exit__(self, type, value, traceback):
        signal.alarm(0)

# Executes a shell command and returns the output without '\n' at the end.
def execute(c):
    return subprocess.check_output(c, shell=True).rstrip()

# Asks a y/n question, with No as default.
def ask_binary_question(q):
    answer = raw_input(q+" [y/N] ").lower()
    return (answer == 'yes' or answer == 'y')

# Generate the parameter space
def gen_params_space(**args):
    tupargs = list(args.items())
    keys = list(map(lambda x:x[0],tupargs))
    for item in product(*map(lambda x:x[1],tupargs)):
        tmp = dict(zip(keys,item))
        if not condition_to_prune_the_param_space(tmp):
            yield dict(zip(keys,item))

# Generate a short version of the filename with only the values
def short_name(oldstr):
    for char in PRMS_NAMES:
        oldstr.replace(char, "")
    return oldstr.replace("-", "")

def parse_short_name(short_name):
    params_str = short_name.split('_')
    params_dict = {}
    for idx, value in enumerate(params_str):
        params_dict[PRMS_NAMES[idx]] = value
    return params_dict

def parse_full_name(full_name):
    return

# Extract the parameter from the string
def scan_params_from_string(params_string):
    p = parse(PRMS_FRMT, params_string)
    return p

# For each point in the parameters space generate the suffix name
def from_params_dict_to_tuple(item):
    return tuple([item[k] for k in PRMS_NAMES])

# Returns the number of result lines in [fn], or 0 if the file does not exist.
def get_lines(fn):
    if os.path.isfile(fn):
        cmd = "wc -l %s | cut -f 1 -d ' '" % fn
        nb_lines = int(execute(cmd))
        if nb_lines>0:
            nb_lines = nb_lines-1   # Do not count the header line
    else:
        nb_lines = 0
    return nb_lines

def ask_send_results(q="Should I send the results to your laptop"):
    send = ask_binary_question(q+" (path is '"+str(PATH_SEND_RESULTS)+"') ?")
    if send:
        # print "Well, this is actually not implemented yet. The programmer must have been lazy."
        rsync_cmd = "rsync -avz -e 'ssh' "+RESULTS_DIR+" "+PATH_SEND_RESULTS
        execute(rsync_cmd)

# Generates the job "wrapper" command, i.e. including 'oarsub'
def gen_wrapper_command(cmd, shortname, suffix, nb_cores, max_duration_hours):
    # Generate outputs
    outn = LOG_DIR + shortname + "_%jobid%.out"
    errn = LOG_DIR + shortname + "_%jobid%.err"
    # Generate wrappper command
    cmd = "oarsub -l "                       \
            + "/nodes=1"                      \
            + "/core="    + str(nb_cores) + "," \
            + "walltime=" + str(max_duration_hours) + ":00:00 "  \
            + "-S \"./"   + cmd  + " " + suffix + "\" " \
            + "-n " + shortname  + " "       \
            + "-O " + outn + " "             \
            + "-E " + errn
    return cmd

def get_jobs():
    running = execute("oarstat -u "+UNAME+" -f | grep command | cut -d' ' -f7-")
    # running is the list of commands, 1 command per line
    return running

# Returns if [pcmd] is already running or waiting to be launched.
def check_job(pcmd, running):
    return pcmd in running

def compute_resources(params_string):
    p = scan_params_from_string(params_string)
    mem_gb = (p['d']*p['n']*8*1.5)      # 1.5*dataset size
    # This is a rough approximation, the memory/core depends on the cluster!
    if mem_gb > 2:
        nb_cores = 2
    elif mem_gb > 4:
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

def ask_binary_question():
    check = str(raw_input("Wanna do it ? (Y/N): ")).lower().strip()
    try:
        if check[0] == 'y':
            return True
        elif check[0] == 'n':
            return False
        else:
            print('Invalid Input')
            return ask_binary_question()
    except Exception as error:
        print("Please enter valid inputs")
        print(error)
        return ask_binary_question()

### HERE COMES THE MAGIC
def main():

    print("==================================================")
    print("=                    w|-|eLLc0me                 =")
    print("=               please help yourself             =")
    print("==================================================")


    print("The magic trick of today is: running for " + MATLAB_FUN)

    # Create directories if necessary
    execute("mkdir -p "+ RESULTS_DIR)
    execute("mkdir -p "+ LOG_DIR)

    if False:
        #TODO: check current and completed jobs
    else:
        print("So, you want to lounch some experiments, arent you?")

        # generate list of all comb of parameters form the given dict
        param_dicts_list = list(gen_params_space(**parameters_and_ranges))

        n_jobs = len(param_dicts_list)
        # print how many jobs it is going to be launched
        print("You are going to submit %g jobs to IGRIDA"%(n_jobs))

        if not ask_binary_question():
            return print('Ahhh, it was nice. See ya later!')

        for idx, params_dict in enumerate(param_dicts_list):
            if idx > n_jobs -1:
                print("Resubmitting failed jobs.")

            print("Submitting job %d/%d"%(i+1,n_jobs))
            #from param dict to string for the matlab binary
            suffix = params2string(params_dict)
            #compute resources (n_core, time) for the job
            (n_cores, max_duration_hours) = (2,6)
            #n_cores, max_duration_hours = compute_resources(params_dict)
            wcmd = gen_wrapper_command(BIN, 
                        shortname,
                        suffix, n_cores, max_duration_hours)
            try:
                # let s wait 4 seconds before getting crazy...
                with timeout(seconds=4):
                    print(wcmd)
                    execute(wcmd)
            except:
                print('No worries, we will try it later')
                param_dicts_list.append(i)

            print ""

if __name__ == '__main__':
    main()
