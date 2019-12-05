# Instructions for classical-planning test-suite

    1. Install Tarski

        git clone https://github.com/aig-upf/tarski
        cd tarski
        git checkout <branch-name> (branch which is the candidate for testing)
        sudo python3 -m pip install -e .

    2. Test 1 problem from all domains in "./classical" directory. This will generate `failure_report.csv` and `status_report.csv` files, and error logs in `stderr_logs` directory.
    
        ./test.sh
        ./test.sh -l (lenient PDDL requirements mode in Tarski)

    3. Test a particular domain and problem pddl

        python3 tarski_test.py --domain <path to domain pddl> --problem <path to problem pddl>

    4. For more info :

        python3 tarski_test.py --help

##### NOTE - 

	All the domain and problem pddl files used for the testing have been copied from https://bitbucket.org/planning-researchers/classical-domains
