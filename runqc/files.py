import os

# modified from: https://stackoverflow.com/a/10961991/1600630
def make_tree(path, recursive=False):
    """ get list of 'path's contents, recursively if desired
    
    To use in template:
    #TODO: get template usage into here!
    
    """
    print(f"DEBUG make_tree path: {path}")
    tree = dict(name=path, contents=[])
    lst = ()
    try:
        lst = os.listdir(path)
    except OSError:
        tree = "There was an OSError..."
        # pass #ignore errors
    except Exception as e:
        tree = "There was an Error... {}".format(str(e))

    for name in lst:
        fn = os.path.join(path, name)
        if os.path.isdir(fn) and recursive:
            tree['contents'].append(make_tree(fn, recursive=recursive))
        else:
            tree['contents'].append(dict(name=fn))

    return tree
