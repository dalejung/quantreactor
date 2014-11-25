from itertools import takewhile
import ast
from functools import partial
from collections import OrderedDict

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

def scoped(line, cell):
    args = parse_args(line)
    name = args.get('func_name', None)
    if name:
        scoped_cells[name] = cell
    return _exec(cell, args)

def run_cell(line):
    bits = line.split()
    name = bits.pop(0)
    args = parse_args(' '.join(bits))
    cell = scoped_cells[name]
    return _exec(cell, args)

def petri(line, cell):
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
