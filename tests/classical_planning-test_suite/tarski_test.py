#!/usr/bin/python3
import sys
import os
import argparse
import re
import time
import resource
import logging

from tarski_util import ground_generate_task
from os.path import basename, abspath, dirname

def main( domain_file, problem_file) :
    start = ( time.time(), time.process_time())   
    try :
        status = ground_generate_task( domain_file, problem_file, None)
    except :
        status = False
        logging.exception("message")

    time_taken = time.time() - start[0]

    if status  :
        print(basename(dirname(domain_file)), "," ,basename(problem_file), ",", "success", ",",
            time_taken, ",", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1000, ",",
            "./stderr_dir/"+basename(dirname(domain_file))+"_stderr.log")
    else : 
        print(basename(dirname(domain_file)), "," ,basename(problem_file), ",", "failure", ",",
            time_taken, ",", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1000, ",",
            "./stderr_dir/"+basename(dirname(domain_file))+"_stderr.log")

if __name__ == "__main__":
    parser  =   argparse.ArgumentParser( description= "Process planner input")
    parser.add_argument( '-d', '--domain', action='store', nargs='?',
            required=True, help='path to the domain pddl file')
    parser.add_argument( '-p', '--problem', action='store', nargs='?',
            required=True, help='path to the problem pddl file')

    args    =   parser.parse_args()
    main( args.domain, args.problem )
