from functools import partial
from collections import OrderedDict

from .runcode import _exec
from . import datacache
from . import output_display
import imp
from earthdragon.tools.timer import Timer

imp.reload(datacache)
imp.reload(output_display)

def cell_magic(func):
    return func

def parse_args(line):
    lines = line.split()
    kwargs = {}
    for line in lines:
        if '=' in line:
            k, v = line.split('=')
            try:
                v = int(v)
            except:
                pass
            kwargs[k] = v
            continue

        if line.startswith('--'):
            kwargs[line] = True
            continue

    return kwargs

# these module level global should be in a class
scoped_cells = {}
scoped_namespaces = {}

@cell_magic
def scoped(line, cell):
    """
    Will scope a block so that it will have access to the ipython ns
    but will not modify it.

    Note, this only applies to shallow modifications. If you modify an
    attribute of global, then that attribute would change.
    """
    name = None
    try:
        bits = line.split(" ")
        if '=' not in bits[0]:
            name = bits[0]
    except:
        pass
    args = parse_args(line)

    scoped_ns = None
    if name:
        scoped_ns = scoped_namespaces.setdefault(name, {})

    if name and '--cell-func' in args:
        scoped_cells[name] = cell

    if '--no-run' in args:
        return

    if '--inherit' in args:
        parent_name = args['--inherit']
        parent_ns = scoped_namespaces.setdefault(parent_name, {})
        scoped_ns.update(parent_ns)

    with Timer(name):
        ns = _exec(cell, args, ns=scoped_ns)

    if name:
        scoped_namespaces[name] = ns

@cell_magic
def run_cell(line):
    """ run a named scoped magic """
    bits = line.split()
    name = bits.pop(0)
    args = parse_args(' '.join(bits))
    cell = scoped_cells[name]
    _exec(cell, args)

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

        if line.strip().startswith("%"):
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
