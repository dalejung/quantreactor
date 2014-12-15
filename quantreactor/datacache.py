from dalestrat.data_decorator import DataStore
from . import runcode
import imp
from edamame.tools.profiler import Profiler

imp.reload(runcode)

from .runcode import _exec

def _datacache(line, cell):
    ip = get_ipython()
    user_ns = ip.user_ns

    vars = line.split()
    namespace = vars.pop(0)
    _datastore = user_ns.setdefault('_datastore', {})
    if namespace not in _datastore:
        _datastore[namespace] = DataStore(namespace)
    ds = _datastore.get(namespace)

    for key in vars:
        if key in ds:
            user_ns[key] = ds[key]

    # really just check for non existent
    # not too complicated
    if not ds.keys():
        ip.run_cell(cell)

    for key in vars:
        obj = user_ns.get(key, None)
        if obj is None:
            continue

        if obj is ds[key]:
            continue

        if not getattr(obj, '_dirty', None):
            continue

        ds[key] = user_ns[key]

def datacache(line, cell):
    #with Profiler(_datacache):
    #    return _datacache(line, cell)
    return _datacache(line, cell)


ip = get_ipython()
ip.register_magic_function(datacache, 'cell')
