import os
import tempfile
import chain
import subprocess
from pddl import domain_to_pddl, problem_to_pddl

DEFAULT_OPTIONS = {
    'search': 'astar(blind)'
}


class FastDownwardError(Exception):
    pass


class FastDownward(object):
    """
    Wrapper class that handles calling FastDownward for planning problems.
    """
    def __init__(self):
        """
        Initializes a new FastDownward solver.
        """
        self.translate_executable = \
            "/home/pkv/Desktop/fd_deb/fd_src/src/translate/translate.py"
        self.preprocess_executable = \
            "/home/pkv/Desktop/fd_deb/fd_src/src/preprocess/preprocess"
        self.search_executable = \
            "/home/pkv/Desktop/fd_deb/fd_src/src/search/downward"
        self.options = DEFAULT_OPTIONS

    def solve(self, problem, options=None):
        """
        Dispatches the problem to a FastDownward solver and returns the
        resulting list of operations as (action, args) tuples.
        """
        # Load default options, override them, and convert to parameter list.
        opts = self.options
        opts.update(options)
        opts = list(chain.from_iterable(('--{}'.format(k), v)
                                        for (k, v) in opts))

        # Create a temporary directory where we will store our problem
        temp_dir = tempfile.mkdtemp()

        # Serialize a description of the domain in PDDL
        domain_fname = os.path.join(
            temp_dir, problem.domain.name + '.pddl')
        with open(domain_fname, 'w') as f:
            f.write(domain_to_pddl(problem.domain))

        # Serialize a description of the problem in PDDL
        problem_fname = os.path.join(temp_dir, problem._name + '.pddl')
        with open(problem_fname, 'w') as f:
            f.write(problem_to_pddl(problem))

        # Launch FastDownward as a sequence of planning operations that
        # are chained by 'or' operators to fail-through
        result = self.run_proc([self.translate_executable,
                                domain_fname, problem_fname], cwd=temp_dir) \
            or self.run_proc([self.preprocess_executable],
                             'output.sas', cwd=temp_dir) \
            or self.run_proc([self.search_executable] + opts,
                             'output', cwd=temp_dir)

        # Report any anomalous status codes returned by planner
        if result:
            raise FastDownwardError('FastDownward failed [{0}]'.format(result))

        # Parse the plan back into a list of tuples
        return problem._domain.parse(os.path.join(temp_dir, 'sas_plan'))

    def run_proc(args, stdin_name=None, cwd=None):
        """
        Helper function used to execute a shell command as a python
        subprocess with a list of arguments and a working directory.
        """
        if stdin_name:
            if cwd:
                stdin_name = os.path.join(cwd, stdin_name)
            stdin = open(stdin_name, 'rb')
        else:
            stdin = None

        with open(os.path.join(cwd, 'args[0].log'), 'w') as stdout:
            returncode = subprocess.call(
                args, stdin=stdin, stdout=stdout, cwd=cwd)

        if stdin:
            stdin.close()
        return returncode
