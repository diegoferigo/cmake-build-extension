// Documentation: https://numpy.org/doc/stable/reference/swig.interface-file.html

%module(package="mathlib") mymath

%{
#define SWIG_FILE_WITH_INIT
#include "mymath.h"
%}

%naturalvar;

// Convert all exceptions to RuntimeError
%include "exception.i"
%exception {
  try {
    $action
  } catch (const std::exception& e) {
    SWIG_exception(SWIG_RuntimeError, e.what());
  }
}

// Convert std::vector <-> python containers
%include <std_vector.i>
%template(VectorD) std::vector<double>;

// Doxygen typemaps
%typemap(doctype) std::vector<double> "Iterable[float]";

// Necessary for type hinting
%pythonbegin %{
from typing import Iterable
%}

// Include numpy.i typemaps
%include "numpy.i"

// Initialize NumPy
%init %{
import_array();
%}

// Apply the NumPy typemaps to the following signatures
%apply (double* IN_ARRAY1, int DIM1) {(double* in_1, unsigned size_in_1)};
%apply (double* IN_ARRAY1, int DIM1) {(double* in_2, unsigned size_in_2)};
%apply (double** ARGOUTVIEWM_ARRAY1, int* DIM1) {(double** out_1, int* size_out_1)};

// Create manually additional functions to allow using directly NumPy types
// without the need to alter the original C++ library
%inline %{
namespace numpy {
    double dot_numpy(double* in_1, unsigned size_in_1,
                     double* in_2, unsigned size_in_2)
    {
        const std::vector<double> vector1(in_1, in_1 + size_in_1);
        const std::vector<double> vector2(in_2, in_2 + size_in_2);

        return mymath::dot(vector1, vector2);
    }

    void normalize_numpy(double* in_1, unsigned size_in_1,
                         double** out_1, int* size_out_1)
    {
        const std::vector<double> vector(in_1, in_1 + size_in_1);

        auto result = mymath::normalize(vector);

        *out_1 = static_cast<double*>(malloc(result.size() * sizeof(double)));
        std::copy(result.begin(), result.end(), *out_1);

        *size_out_1 = result.size();
    }
}
%}

// Include the header with the symbols to wrap
%include "mymath.h"
