#pragma once
#ifndef EXAMPLE_HEADER_H
#define EXAMPLE_HEADER_H

#ifdef _WIN32

    #ifdef __cplusplus
        #define PREFIX extern "C" __declspec(dllexport)
        #define SUFFIX noexcept
    #else
        #define PREFIX __declspec(dllexport)
        #define SUFFIX
    #endif

#else

    #ifdef __cplusplus
        #define PREFIX extern "C"
        #define SUFFIX noexcept
    #else
        #define PREFIX
        #define SUFFIX
    #endif

#endif

struct State;

// Defines some index types
typedef enum
{
    index_a = 0,
    index_b = 1,
    index_c = 2
} Index_Type;

/*
            Set
----------------------------------
*/

// Set the types of the atoms in a basis cell
PREFIX void set_config_index(State *state, int index) SUFFIX;
// Set the overall lattice constant
PREFIX void set_index_type(State *state, Index_Type type) SUFFIX;

/*
            Get
----------------------------------
*/

// Get number of spins
PREFIX int get_config_index(State * state) SUFFIX;

// Get positions of spins
PREFIX float * get_data(State * state) SUFFIX;

// Get bravais lattice type
PREFIX Index_Type get_index_type(State *state) SUFFIX;

#undef DLLEXPORT
#endif
