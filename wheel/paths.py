"""
Installation paths.

Map the .data/ subdirectory names to install paths.
"""

import os.path
import sys
import distutils.dist as dist
import distutils.command.install as install

def get_install_paths(name):
    """
    Return the (distutils) install paths for the named dist.
    
    A dict with ('purelib', 'platlib', 'headers', 'scripts', 'data') keys.
    """    
    paths = {}

    # late binding due to potential monkeypatching
    d = dist.Distribution({'name':name})
    i = install.install(d)
    i.finalize_options()
    for key in install.SCHEME_KEYS:
        paths[key] = getattr(i, 'install_'+key)
        
    # pip uses this path as an alternative to the system's (read-only) 
    # include directory:
    if hasattr(sys, 'real_prefix'): # virtualenv
        paths['headers'] = os.path.join(sys.prefix, 
                                        'include', 
                                        'site', 
                                        'python' + sys.version[:3])

    return paths
