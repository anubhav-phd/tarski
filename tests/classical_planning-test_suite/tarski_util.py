################################################################################
#                                                                              #
# Info:     Utility methods for LAPKT-Tarski integration                       #
#                                                                              #
# Author:   Anubhav Singh                                                      #
#                                                                              #
# Date:     08-Sep-2019                                                        #
#                                                                              #
# Dependencies:                                                                #
# 1. pip install timers                                                        #
# 2. pip install tarski                                                        #
# 3. python 3.x                                                                #
#                                                                              #
################################################################################
'''
References-
[1.]  "Combining the Expressivity of UCPOP with the Efficiency of Graphplan"
        by B.Cenk Gazen and Craig A. Knoblock
[2.]  "Concise finite-domain representations for PDDL planning tasks"
        by Malte Helmert (Artificial Intelligence 173 (2009) 503–53)
'''

# standard library imports
#-----------------------------------------------------------------------------#
import time
import itertools
import sys
import copy
import contextlib
#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx#

# Tarski library imports
#-----------------------------------------------------------------------------#
from tarski.io import FstripsReader
from tarski.reachability.asp import *
from tarski.grounding import LPGroundingStrategy, NaiveGroundingStrategy
from tarski.syntax.transform.quantifier_elimination import QuantifierElimination
from tarski.syntax import (QuantifiedFormula, CompoundFormula, Tautology,
    Function, Quantifier, land, CompoundTerm, Contradiction, symref)
from tarski.syntax.builtins import BuiltinPredicateSymbol
from tarski.syntax.transform.substitutions import create_substitution
from tarski.syntax.transform.errors import TransformationError
from tarski.fstrips import (UniversalEffect, AddEffect, DelEffect,
    FunctionalEffect)
#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx#


# DEFINED CONSTANTS
DEFAULTCOST =   1

#-----------------------------------------------------------------------------#
@contextlib.contextmanager
def time_taken( task_name: str) :
    """
    Track the time taken for a task.
    Usage - "with time_taken("<process name>") :"
    Arguments
    =========
    time_taken: string - name of the task
    """
    start = ( time.time(), time.process_time())
    #print("***Started - {} ...***".format(task_name))
    sys.stdout.flush()
    yield
    #print(("***Finished {} after {:.3f} seconds CPU time, {:.3f} seconds "+
    #        "wall-clock time***\n").format( task_name, time.time()-start[0],
    #            time.process_time()-start[1] ))
    sys.stdout.flush()
#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx#



#-----------------------------------------------------------------------------#
def ground_generate_task( domain_file, problem_file, out_task=None) :
    """
    Uses Tarski Grounder to generate the output task using pddl

    Arguments
    =========
    domain_file  : domain pddl file location
    problem_file : problem pddl file location
    output_task  : C++ container to store/process domain and problem

    Returns
    =======
    None
    """

    parsing_timer   =   time.process_time()
    #Setup a reader to read the domain and problem pddl files
    with time_taken( "reading and parsing pddl file") :
        problem = FstripsReader( raise_on_error=True,
                theories=None).\
        read_problem( domain_file, problem_file)
    """
    # Eliminate Universal Effects and Quantifiers by transformation
    with time_taken("finding static predicates") :
        problem.fluent_preds = find_fluent_predicates( problem)
    """
    with time_taken( "preprocessing tarski problem") :
        process_problem( problem)
        init = problem.init_bk

    with time_taken( "grounding") :
        grounding               =   LPGroundingStrategy( problem)
        reachable_action_params =   copy.deepcopy( grounding.ground_actions())
        fluents                 =   copy.deepcopy( grounding.ground_state_variables())
        del grounding
        count_params = 0
        for x, y in reachable_action_params.items() :
            for z in y :
                count_params += 1
        #print("Total number of reachable action params = ", count_params)

    return True
#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx#

#-----------------------------------------------------------------------------#
def process_problem(problem, task_id=[0,]) :
    """
    1. Eliminates univeral effects from problem by transforming to multiple
        conditional effects
    2. Extract action cost from total-cost action effect or 1(default) and
        remove total cost atoms from problem.init

    Arguments
    =========
    problem: object of Problem class
    task_id: list of integers
        0 - All tasks (default)
        1 - Eliminate Unviseral Effects and Quantifiers
        2 - Extract cost from 'total-cost' atoms in prob. description
    Returns
    =======
    None
    """
    # Eliminate function extensions from prob.init
    if ( 0 in task_id) or( 2 in task_id) :
        problem.init_bk = {}
        for atom in problem.init.as_atoms() :
            if isinstance(atom, Atom) :
                problem.init_bk[atom] = True
        problem.fvals = []
        for k, x in problem.init.function_extensions.items() :
            for var, val in x.data.items() :
                problem.fvals.append((k[0]+"("+",".join(
                    [str(x.expr) for x in var])+")", val.symbol))
        problem.init.function_extensions    =   dict()

    for _, action in problem.actions.items() :
        effects = list()
        action.cost = 1 # set default cost as 1
        for effect in action.effects :
            effects += process_effects( effect, action, problem.language)
        action.effects = effects
        if ( 0 in task_id) or ( 1 in task_id) :
            action.precondition = process_formula( action.precondition,
                    problem.language)
    return 0
#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx#

#-----------------------------------------------------------------------------#
def process_effects( eff, action, lang, task_id=[0,]) :
    """
    Elimates univeral effects by transforming to multiple conditional effects

    Arguments
    =========
    lang: object of type FirstOrderLanguage
    eff:  any effect type object
    task_id - Usage same as 'process_problem' method
    Returns
    =======
    list: list of effects
    """
    effect_l            = [] # new list of effects
    if isinstance( eff, UniversalEffect) and ( 0 in task_id or 1 in task_id) :
        for effect in eff.effects :
            effect.condition = process_formula( effect.condition,
                    lang)

            # if Uni. Effect then transform to a list of Add/Del Effects
            if isinstance( effect, UniversalEffect) :
                effect_l += process_effects( effect, action, lang)
                continue

            # else if Add/Del effect, just instantiate condition and atom
            assert isinstance( effect, AddEffect) or isinstance(
                    effect, DelEffect)

            card, syms, substs = _enumerate_instantiations( eff.variables)
            if card == 0 :
                raise TransformationError( "universal effect elimination",
                       eff, "No constants were defined!")
            cond_effects    = []
            for values in itertools.product( *substs) :
                subst       = create_substitution( syms, values)
                cond_sub    = process_formula( term_substitution(
                    lang, effect.condition, subst), lang)
                atom_sub    = term_substitution( lang, effect.atom, subst)
                if isinstance( effect, AddEffect) :
                    ce = AddEffect( atom_sub, cond_sub)
                elif isinstance( effect, DelEffect) :
                    ce = DelEffect( atom_sub, cond_sub)
                else :
                    raise TransformationError( "universal effect elimination",
                        eff, "Effect type can't be handled!")
                cond_effects.append( ce)
            effect_l += cond_effects
    elif isinstance( eff, FunctionalEffect) and (eff.lhs.symbol.symbol==
        'total-cost') and (0 in task_id or 2 in task_id) :
        action.cost = eff.rhs
    elif (isinstance(eff, AddEffect) or isinstance(eff, DelEffect)) and \
            (0 in task_id or 1 in task_id) :
        eff.condition = process_formula( eff.condition, lang)
        effect_l.append( eff)
    else :
        effect_l.append( eff)

    return effect_l
#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx#

#-----------------------------------------------------------------------------#
def process_formula( formula, lang) :
    """
    Recursively eliminate quantified formulas in formulas

    Arguments
    =========
    formula: CompoundFormula or QuantifiedFormula

    Returns
    =======
    Transformed formula
    """
    # Anu :  Added dnf check to flag formulas which may require DNF
    formula.dnf_check = False
    if isinstance( formula, CompoundFormula) :
        sub_f   =   []
        if formula.connective==Connective.Or :
            formula.dnf_check   =   True
        for f in formula.subformulas :
            sub_f.append( process_formula( f, lang))
            if f.dnf_check==True :
                formula.dnf_check = True
        formula.subformulas =   sub_f
        return formula
    elif isinstance( formula, QuantifiedFormula) :
        return process_formula( ( QuantifierElimination.rewrite( lang, formula,
            QuantifierEliminationMode.All)).result, lang)
    else :
        return formula
#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx#

#-----------------------------------------------------------------------------#
def _enumerate_instantiations( variables) :
    """
    Enumerate Instantiations

    Argument
    ========
    variables: iterator of type class Variable

    Returns
    =======
    cardinality: int
    symbols: list
    instantiations: list
    """
    syms = []
    instantiations = []
    cardinality = 1
    for st in variables :
        if st.sort.builtin :
            raise TransformationError( "instantiate compound formula", phi,
                    "Variable found of built-in sort '{}', domain is too large!"
                    .format( st.sort.name))
        syms.append( st)
        instantiations.append( list(st.sort.domain()))
        cardinality *= len( instantiations[-1])
    return cardinality, syms, instantiations
#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx#

#-----------------------------------------------------------------------------#
def visit(phi, subst):
    if isinstance(phi, CompoundFormula):
        subformulas = [visit(f, subst) for f in phi.subformulas]
        return CompoundFormula( phi.connective, subformulas)

    elif isinstance(phi, QuantifiedFormula):
        if any(symref(x) in subst for x in phi.variables):
            raise SubstitutionError(phi, subst, 'Attempted to substitute variable bound by quantifier')
        formula =   visit(phi.formula, subst)
        return QuantifiedFormula(phi.quantifier, phi.variables, formula)

    elif isinstance(phi, Atom):
        new_subterms = list(phi.subterms)
        phi = Atom(phi.symbol, phi.subterms)
        for k, t in enumerate(new_subterms):
            rep = subst.get(symref(t), None)
            if rep is None:
                new_subterms[k] = visit(t, subst)
            else:
                new_subterms[k] = rep
        phi.subterms = tuple(new_subterms)
        return phi
    elif isinstance(phi, CompoundTerm):
        new_subterms = list(phi.subterms)
        phi = CompoundTerm(phi.symbol, phi.subterms)
        for k, t in enumerate(new_subterms):
            rep = subst.get(symref(t), None)
            if rep is None:
                new_subterms[k] = visit(t, subst)
            else:
                new_subterms[k] = rep
        phi.subterms = tuple(new_subterms)
        return phi
    return phi
#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx#

#-----------------------------------------------------------------------------#
def term_substitution(language, phi, substitution, inplace=False):
    """ Return the result of applying the given substitution to the given formula or term of the language.
    If `inplace` is true, the given formula is the one modified.
    """
    assert isinstance(phi, (Formula, Term))
    #phi = phi if inplace else copy.deepcopy(phi)
    phi = visit(phi, substitution)
    return phi
#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx#
