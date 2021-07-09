#include "mymath.h"

#include <Eigen/Dense>
#include <pybind11/eigen.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <string>

// Create the Python module
PYBIND11_MODULE(bindings, module)
{
    namespace py = ::pybind11;
    module.doc() = "mymath bindings";

    // These methods accept numpy array but return float / list
    module.def("dot", &mymath::dot, py::arg("vector1"), py::arg("vector2"));
    module.def("normalize", &mymath::normalize, py::arg("data"));

    // In order to return directly a numpy object, we can pass through Eigen
    module.def(
        "normalize_numpy",
        [](const std::vector<double>& data) -> Eigen::VectorXd {
            const auto output = mymath::normalize(data);
            return Eigen::Map<Eigen::VectorXd>(
                const_cast<double*>(output.data()), output.size());
        },
        py::arg("data"));
}
