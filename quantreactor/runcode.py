import ast
from itertools import takewhile

def have_var(expr, args):
    """
    True if expression is an assignment for a variable
    that already exists in `args`
    """
    if not isinstance(expr, ast.Assign):
        return False

    for target in expr.targets:
        if not isinstance(target, ast.Name):
            continue

        if target.id in args:
            return True

def _exec(cell, args={}, ns=None):
    if ns is None:
        ns = {}
    user_ns = get_ipython().user_ns  # flake8: noqa
    ns.update(user_ns)
    ns.update(args)
    code = "\n".join(takewhile(lambda x: x.strip() != '%stop', cell.split('\n')))
    module = ast.parse(code)
    # could just parse and see what was assigned
    module.body = list(filter(lambda expr: not have_var(expr, args), module.body))
    code = compile(module, '<dale>', 'exec')
    exec(code, ns)
    # not sure what to do with changed
    changed = {k:v for k, v in ns.items() if k not in user_ns or v is not user_ns[k]}
    return ns
