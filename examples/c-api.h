#ifndef EXAMPLE_H
#define EXAMPLE_H

// Some physical constant [A/m^2]
#define MYLIB_CONSTANT 3.24

// Another physical constant [ps/rad], defined differently
static const double mylib_constant_b()
{
    return 3.34;
}

// Enumeration index for object A
#define MYLIB_INDEX_A 0

// Enumeration index for object B
#define MYLIB_INDEX_B 1

// Enumeration index for object C
#define MYLIB_INDEX_C 2

// Some important, but opaque state struct
struct state;

// Some transparent point struct
struct point
{
    float x;
    float y;
    float z;
};

// Version information
int mylib_version();

// Move between images (change active_image)
bool perform_operation(state * state, int some_index=-1);

// These comments will not
// appear in the docs
// This commment will appear in the docs
bool mylib_example(state * state, int some_index=-1);

/*
These comment lines will all appear in the docs

**Takes**
- n: the number of some things
- init: the initial value of something

**Returns**
- Whether something was successful

For example, if you want to do *something*, call
`bool success = mylib_something(mystate, 100, 2.0f);`
*/
bool mylib_something(state * state, int n=1, float init=0.1f);

#endif