import unittest
import subprocess
from pathlib import Path, PurePosixPath

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
        try:
            infile = TESTS_PATH / "headers" / "simple.h"
            outfile = TESTS_PATH / "simple.md"
            subprocess.check_output(["clang-api-doc", '-f', str(infile), '-o', str(outfile)], shell=True, stderr=subprocess.STDOUT)
            docs = outfile.read_text()
            self.assertEqual(docs.strip(), SIMPLE_H_DOCS.strip())
        except subprocess.CalledProcessError as e:
            self.fail(f"Could not generate docs. Message:\n{e.output.decode('utf-8').strip()}")

if __name__ == '__main__':
    unittest.main()