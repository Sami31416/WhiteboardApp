// Include Pybind11 for Python-C++ bindings
#include <pybind11/pybind11.h>  

// Shorten pybind11 namespace to 'py' for easier use
namespace py = pybind11;  

// Define a Python module named 'core'
PYBIND11_MODULE(core, m) {  
    // Future Vulkan bindings will go here
    // Example: m.def("render", &renderFunction);
}  