// Forward declaration of `state`
struct state;

// Calaculates the data configuration index in the current state
int get_config_index(state * state);

// Returns the pointer to the data in the current state
float * get_data(state * state);