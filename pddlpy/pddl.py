"""
Serialization of PDDL 2.2 EBNF specification from python objects.
"""


def constant_to_pddl(const):
    raise NotImplementedError()


def predicate_to_pddl(predicate):
    return "({name} {typed_list})".format(name=predicate.__class__.name,
                                          typed_list=predicate.args).lower()


def literal_to_pddl(literal):
    return "{name}({args})".format(name=literal.__class__.name,
                                   args=literal.args).lower()


def function_to_pddl(function):
    raise NotImplementedError()


def action_to_pddl(action):
    name = action.__class__.name

    precondition_def = (None if not hasattr(action, 'pre')
                        else ":precondition {goal}"
                        .format(goal=literal_to_pddl(action.pre)))

    effect_def = (None if not hasattr(action, 'post')
                  else ":effect {effect}"
                  .format(effect=literal_to_pddl(action.post)))

    return ("(:action {name} :parameters ({typed_list})"
            "{precondition_def} {effect_def}"
            .format(name=name,
                    precondition_def=precondition_def,
                    effect_def=effect_def)).lower()


def domain_to_pddl(domain):
    name = domain.name
    requirements = []

    constants_def = (None if not hasattr(domain, 'constants')
                     else "(:constants {})"
                     .format(' '.join([constant_to_pddl(c)
                                       for c in domain.constants])))

    predicates_def = ("(:predicates {})"
                      .format(' '.join([predicate_to_pddl(p)
                                        for p in domain.predicates])))

    functions_def = (None if not hasattr(domain, 'functions')
                     else "(:functions {})"
                     .format(' '.join([function_to_pddl(f)
                                       for f in domain.functions])))
    if functions_def:
        requirements.append(":fluents")

    structure_def = (' '.join([action_to_pddl(a)
                               for a in domain.actions]))

    require_def = (None if not requirements
                   else "(:requirements {})"
                   .format(' '.join(requirements)))

    return ("(define (domain {name})"
            " {require_def}"
            " {constants_def}"
            " {predicates_def}"
            " {functions_def}"
            " {structure_def}"
            ")").format(
        name=name,
        require_def=require_def,
        constants_def=constants_def,
        predicates_def=predicates_def,
        functions_def=functions_def,
        structure_def=structure_def).lower()


def problem_to_pddl(problem):
    name = problem.name
    domain_name = problem.domain.name
    requirements = []

    object_declaration = "(:objects {})".format(' '.join([o
                                                for o in problem.objects]))

    init = "(:init {})".format(' '.join([literal_to_pddl(l)
                                         for l in problem.init]))
    goal = "(:goal {})".format(literal_to_pddl(problem.goal))

    metric_spec = (None if not hasattr(problem, 'metric')
                   else "(:metric {optimization} {expression})"
                   .format(optimization=problem.metric.optimization,
                           expression=problem.metric.expression))

    require_def = (None if not requirements
                   else "(:requirements {})"
                   .format(' '.join(requirements)))

    return ("(define (problem {name})"
            " (:domain {domain_name})"
            " {require_def}"
            " {object_declaration}"
            " {init}"
            " {goal}"
            " {metric_spec}").format(
        name=name,
        domain_name=domain_name,
        require_def=require_def,
        object_declaration=object_declaration,
        init=init,
        goal=goal,
        metric_spec=metric_spec).lower()
