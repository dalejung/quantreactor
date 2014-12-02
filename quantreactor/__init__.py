from itertools import takewhile
import ast
from functools import partial
from collections import OrderedDict

def cell_magic(func):
    return func

def parse_args(line):
    lines = line.split()
    kwargs = {}
    for line in lines:
        if '=' not in line:
            continue
        k, v = line.split('=')
        try:
            v = int(v)
        except:
            pass
        kwargs[k] = v
    return kwargs

scoped_cells = {}

def have_var(expr, args):
    """
    True if expression is an assignment for a variable
    that already exists in `args`
    """
    if not isinstance(expr, ast.Assign):
        return False

    for target in expr.targets:
        if target.id in args:
            return True

def _exec(cell, args):


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
    changed = {k:v for k, v in ns.items() if k not in user_ns or v is not user_ns[k]}

@cell_magic
def scoped(line, cell):
    """
    Will scope a block so that it will have access to the ipython ns
    but will not modify it.

    Note, this only applies to shallow modifications. If you modify an
    attribute of global, then that attribute would change.
    """
    args = parse_args(line)
    name = args.get('func_name', None)
    if name:
        scoped_cells[name] = cell
    return _exec(cell, args)

@cell_magic
def run_cell(line):
    """ run a named scoped magic """
    bits = line.split()
    name = bits.pop(0)
    args = parse_args(' '.join(bits))
    cell = scoped_cells[name]
    return _exec(cell, args)

@cell_magic
def petri(line, cell):
    """
    Allows a multi-cell. Basically, it will break up the cell by %% blocks
    and then execute each one in turn.
    """
    ip = get_ipython()
    cells = OrderedDict()
    cells[''] = []
    c = cells['']
    for line in cell.split('\n'):
        if not line.strip() and not c:
            continue

        if line.strip().startswith("%%"):
            cells[line] = []
            c = cells[line]
        else:
            c.append(line)

    for k in cells:
        cells[k] = '\n'.join(cells[k])

    output = {}
    for line, cell in cells.items():
        output[line] = ip.run_cell(line + "\n" + cell)


ip = get_ipython()
ip.register_magic_function(scoped, 'cell')
ip.register_magic_function(run_cell, 'line')
ip.register_magic_function(petri, 'cell')
