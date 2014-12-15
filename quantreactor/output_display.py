from collections import OrderedDict
from IPython.display import Markdown

from .runcode import _exec

class CellRun(object):
    line = None
    header = None
    code = None
    output = None

def print_output(line, cell=None):
    """
    Trying to find an quick way to quickly write up summaries
    """
    ip = get_ipython()
    user_ns = ip.user_ns

    cells = OrderedDict()

    cr = CellRun()
    cr.line = line

    # split up into header and code if it exists
    bits = line.rsplit('||', 1)
    header = code = bits[0]

    if len(bits) == 2:
        header, code = bits

    cr.header = header
    cr.code = code

    cells[header] = cr

    def last_line_exec(cell):
        """ modify code to run and grab last evaluated """
        cell = '_output_display = ' + cell
        ip.run_cell(cell, silent=True)
        ret = user_ns['_output_display']
        del user_ns['_output_display']
        return ret

    results = OrderedDict() 
    for header, cr in cells.items():
        cr.output = last_line_exec(cr.code)
        results[header] = cr

    output = ''
    for header, cr in results.items():
        output += "###{header}\n`{code}`\n```{output}```\n".format(**cr.__dict__)
    return Markdown(output)

ip = get_ipython()
ip.register_magic_function(print_output, 'line', 'print')
