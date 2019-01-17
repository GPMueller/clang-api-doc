C API documentation
===================

* Copyright (c) 2001, Someone
 *
 * There is some license.
 * Find the file somewhere.
 *

-------------------------------


THIS IS A GLOBAL COMMENT AND THE FILE HEADING
------------------------------------------------------

-------------------------------


**`MYLIB_CONSTANT 3.24`:**

Some physical constant [A/m^2]

-------------------------------


**`static const double mylib_constant_b() { return 3.34; }`:**

Another physical constant [ps/rad], defined differently

-------------------------------


**`MYLIB_INDEX_A 0`:**

Enumeration index for object A

-------------------------------


**`MYLIB_INDEX_B 1`:**

Enumeration index for object B

-------------------------------


**`MYLIB_INDEX_C 2`:**

Enumeration index for object C

-------------------------------


**`struct state`:**

Some important, but opaque state struct

-------------------------------


**`struct point { float x; float y; float z; }`:**

Some transparent point struct

-------------------------------


**`typedef enum { some_value  = 0, other_value = 1, next_value  = 2, last_value  = 3, } mylib_values`:**

Typedef enum... this might be a bit tricky to format nicely.

Would be better to have `typedef enum mylib_values` and then the values
- some_value  = 0,
- other_value = 1,
- next_value  = 2,
- last_value  = 3,

-------------------------------


**`int mylib_version()`:**

Version information

-------------------------------


**`bool perform_operation(state * state, int some_index=-1)`:**

Move between images (change active_image)

-------------------------------


THIS IS AN EXAMPLE FOR GLOBAL COMMENT INSERTION
------------------------------------------------------

-------------------------------


**`bool mylib_example(state * state, int some_index=-1)`:**

This commment will appear in the docs

-------------------------------


**`bool mylib_something(state * state, int n=1, float init=0.1f)`:**

These comment lines will all appear in the docs

**Takes**
- n: the number of some things
- init: the initial value of something

**Returns**
- Whether something was successful

For example, if you want to do *something*, call
`bool success = mylib_something(mystate, 100, 2.0f);`

-------------------------------
