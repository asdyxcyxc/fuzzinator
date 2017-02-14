# Copyright (c) 2016-2017 Renata Hodovan, Akos Kiss.
#
# Licensed under the BSD 3-Clause License
# <LICENSE.rst or https://opensource.org/licenses/BSD-3-Clause>.
# This file may not be copied, modified, or distributed except
# according to those terms.

import json
import os
import shlex
import subprocess
import sys


def SubprocessCall(command, cwd=None, env=None, no_exit_code=None, test=None, **kwargs):
    """
    Subprocess invocation-based call of a SUT that takes test input on its
    command line. (See :class:`fuzzinator.call.FileWriterDecorator` for SUTs
    that take input from a file.)

    **Mandatory parameter of the SUT call:**

      - ``command``: string to pass to the child shell as a command to run (all
        occurrences of ``{test}`` in the string are replaced by the actual test
        input).

    **Optional parameters of the SUT call:**

      - ``cwd``: if not ``None``, change working directory before the command
        invocation.
      - ``env``: if not ``None``, a dictionary of variable names-values to
        update the environment with.
      - ``no_exit_code``: makes possible to force issue creation regardless of
        the exit code.

    **Result of the SUT call:**

      - If the child process exits with 0 exit code, no issue is returned.
      - Otherwise, an issue with ``'exit_code'``, ``'stdout'``, and ``'stderr'``
        properties is returned.

    **Example configuration snippet:**

        .. code-block:: ini

            [sut.foo]
            call=fuzzinator.call.SubprocessCall

            [sut.foo.call]
            # assuming that {test} is something that can be interpreted by foo as
            # command line argument
            command=./bin/foo {test}
            cwd=/home/alice/foo
            env={"BAR": "1"}
    """
    env = dict(os.environ, **json.loads(env)) if env else None
    no_exit_code = eval(no_exit_code) if no_exit_code else False
    with subprocess.Popen(shlex.split(command.format(test=test), posix=sys.platform != 'win32'),
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          cwd=cwd or os.getcwd(),
                          env=env) as proc:
        stdout, stderr = proc.communicate()
        if no_exit_code or proc.returncode != 0:
            return {
                'exit_code': proc.returncode,
                'stdout': stdout,
                'stderr': stderr,
            }
    return None
