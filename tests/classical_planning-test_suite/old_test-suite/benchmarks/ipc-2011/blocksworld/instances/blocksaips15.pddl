Domain: /home/xoxo/Documents/Research_Project/anubhav-research/BFWS-Bloomfilter/benchmarks/ipc-2006/openstacks/domain.pddl Problem: /home/xoxo/Documents/Research_Project/anubhav-research/BFWS-Bloomfilter/benchmarks/ipc-2006/openstacks/problems/p01.pddl
Parsing...
Parsing: [0.000s CPU, 0.002s wall-clock]
Generating Datalog program... [0.000s CPU, 0.000s wall-clock]
Normalizing Datalog program...
Normalizing Datalog program: [0.010s CPU, 0.001s wall-clock]
Preparing model... [0.000s CPU, 0.001s wall-clock]
Generated 34 rules.
Computing model... [0.000s CPU, 0.002s wall-clock]
241 relevant atoms
95 auxiliary atoms
336 final queue length
516 total queue pushes
Completing instantiation... [0.000s CPU, 0.003s wall-clock]
goal relaxed reachable: True
42 atoms
Computing fact groups...
Finding invariants...
13 initial candidates
Time limit reached, aborting invariant generation
Finding invariants: [0.000s CPU, 0.000s wall-clock]
Checking invariant weight... [0.000s CPU, 0.000s wall-clock]
Instantiating groups... [0.000s CPU, 0.000s wall-clock]
Collecting mutex groups... [0.000s CPU, 0.000s wall-clock]
Choosing groups...
42 uncovered facts
Choosing groups: [0.000s CPU, 0.000s wall-clock]
Building translation key... [0.000s CPU, 0.000s wall-clock]
Computing fact groups: [0.000s CPU, 0.001s wall-clock]
Axioms 20
Deterministic 115 actions
Invariants 42
stacks-avail_n0
waiting_o4
waiting_o3
waiting_o2
machine-available
waiting_o5
waiting_o1
(not made_p1)
(not made_p2)
(not made_p3)
(not made_p4)
(not made_p5)
(not new-axiom@0_p1)
(not new-axiom@0_p2)
(not new-axiom@0_p3)
(not new-axiom@0_p4)
(not new-axiom@0_p5)
(not new-axiom@1_o1)
(not new-axiom@1_o2)
(not new-axiom@1_o3)
(not new-axiom@1_o4)
(not new-axiom@1_o5)

 Match tree built with 115 nodes.

PDDL problem description loaded: 
	Domain: openstacks-sequencedstrips
	Problem: os-sequencedstrips-small-4
	#Actions: 115
	#Fluents: 57
Starting search with BRFS (time budget is 60 secs)...
[2][3][4][5][6][7][8][9][10][11][12]Plan found with cost: 11
1. (open-new-stack n0 n1)
2. (start-order o5 n1 n0)
3. (ship-order o5 n0 n1)
4. (start-order o4 n1 n0)
5. (ship-order o4 n0 n1)
6. (start-order o3 n1 n0)
7. (ship-order o3 n0 n1)
8. (start-order o2 n1 n0)
9. (ship-order o2 n0 n1)
10. (start-order o1 n1 n0)
11. (ship-order o1 n0 n1)
Time: 0.152237
Generated: 33760
Expanded: 21394
Total time: 0.15225
Nodes generated during search: 33761
Nodes expanded during search: 21394
BRFS search completed in 0.15225 secs, check 'bfs_f.log' for details
