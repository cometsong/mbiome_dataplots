import os
import types
import json
from inspect import currentframe, getframeinfo
from pathlib import Path

this_file = getframeinfo(currentframe()).filename
parent_dir = str(Path(this_file).resolve().parent.parent)

auth_file = os.path.join(parent_dir,'db_auth.json')
db_fp = open(auth_file, 'r')
# types.SimpleNamespace to use "obj.atrr"
_db = json.load(db_fp, object_hook=lambda d: types.SimpleNamespace(**d))

db_config = {
    'url':
        f'{_db.dbtype}://{_db.user}:{_db.password}'
        f'@{_db.host}:{_db.port}/{_db.database}',
    'charset': _db.charset,
}
