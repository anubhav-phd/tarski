#!/usr/bin/env python3
################################################################################
#                                                                              #
# Info:     Classical planning - Pddl parsing and grounding test module        #
#                                                                              #
# Author:   Anubhav Singh (anubhav.singh.eng@gmail.com)                        #
#                                                                              #
# Date:     05-Dec-2019                                                        #
#                                                                              #
# Dependencies:                                                                #
# 1. pip install tarski                                                        #
# 2. python version - 3.x (as required by tarski)                              #
#                                                                              #
################################################################################

import sys
import os
import argparse
import re
import time
import resource
import logging

from tarski_util import ground_generate_task
from os.path import basename, abspath, dirname

def main( domain_file, problem_file, verbose, lenient) :
    start = ( time.time(), time.process_time())   
    try :
        status = ground_generate_task( domain_file, problem_file, None, verbose, lenient)
    except :
        status = False
        logging.exception("message")


    time_taken = time.time() - start[0]
    
    if verbose :
        print("|---- Overall status, runtime and max memory consumption ----|")
    # DEFAULT OUTPUT
    if status  :
        if verbose :
            print(basename(dirname(domain_file)), "," ,basename(problem_file), ",", "success", ",",
                "{:.3f} seconds , ".format(time_taken),  
                resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1000, "MB", end="")
        else :
            print(basename(dirname(domain_file))+ "," +basename(problem_file)+ ","+ "success"+
                ",{:.3f},".format(time_taken)+  
                str(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1000), end="")
    else : 
        if verbose :
            print(basename(dirname(domain_file)), "," ,basename(problem_file), ",", "failure", ",",
                "{:.3f} seconds , ".format(time_taken),  
                resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1000, "MB", end="")
        else :
            print(basename(dirname(domain_file))+ "," +basename(problem_file)+ ","+ "failure"+
                ",{:.3f},".format(time_taken)+  
                str(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1000), end="")
    if verbose :
        print("\n|---- xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx ----|")

if __name__ == "__main__":
    parser  =   argparse.ArgumentParser( description= "Process planner input")
    parser.add_argument( '-d', '--domain', action='store', nargs='?',
            required=True, help='path to the domain pddl file')
    parser.add_argument( '-p', '--problem', action='store', nargs='?',
            required=True, help='path to the problem pddl file')
    parser.add_argument( '-v', '--verbose', action='store_true'
            , help='print elaborate - step-wise output on runtime')
    parser.add_argument( '-l', '--lenient', action='store_true'
            , help='sets strict_with_requirements = False for Tarski grounding, the parser will'+ 
                    ' be less strict with the PDDL requirement flags, and will load by default'+
                    ' and necessary theories to process action costs.')

    args    =   parser.parse_args()
    main( args.domain, args.problem, args.verbose, args.lenient )
