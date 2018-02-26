#
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""`pstar` module.

Import like this:
```python
from pstar import defaultpdict, frozenpset, pdict, plist, pset, ptuple, pstar
```

Of course, `from pstar import *` works as well.

If you have a bunch of data that you want to convert to pstar and manipulate, you can
also just import like this to get the recursive conversion function:
```python
from pstar import pstar
```

At that point, you can access the core `pstar` classes as needed with:
```python
pd = pstar.pdict(foo=1, bar=2, baz=3)
pl = pstar.plist([1, 2, 3])
```
"""

from .pstar import defaultpdict, frozenpset, pdict, plist, pset, ptuple, pstar

__all__ = ['defaultpdict', 'frozenpset', 'pdict', 'plist', 'pset', 'ptuple', 'pstar']
