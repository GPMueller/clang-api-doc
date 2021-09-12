import unittest
import subprocess
from pathlib import Path, PurePosixPath

from clang_api_doc import clang_api_doc

TESTS_PATH = Path(__file__).parent.resolve()

SIMPLE_H_DOCS = """
### state

```C
struct state
```

Forward declaration of `state`



### get_config_index

```C
int get_config_index(state * state)
```

Calaculates the data configuration index in the current state



### get_data

```C
float * get_data(state * state)
```

Returns the pointer to the data in the current state
"""


class TestClangApiDoc(unittest.TestCase):
    def test_simple(self):
        infile = TESTS_PATH / "headers" / "simple.h"
        outfile = TESTS_PATH / "simple.md"

        clang_api_doc.transform_file(infile, outfile)

        docs = outfile.read_text()
        self.assertEqual(docs.strip(), SIMPLE_H_DOCS.strip())


if __name__ == "__main__":
    unittest.main()
