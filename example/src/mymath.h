#ifndef MYMATH_H
#define MYMATH_H

#include <vector>

namespace mymath {

    /**
     * Perform the inner product between two 1D vectors.
     *
     * @param vector1 The first vector.
     * @param vector2 The second vector.
     * @throws If the vectors sizes do not match.
     * @return The double product of the input vectors.
     */
    double dot(const std::vector<double>& vector1,
               const std::vector<double>& vector2);

    /**
     * Normalize a 1D vector.
     *
     * The normalization operation takes the input vector and divides
     * all its element by its norm. The resulting vector is a unit vector,
     * i.e. a vector with length 1.
     *
     * @param input The vector to normalize.
     * @return The unit vector computed by normalizing the input.
     */
    std::vector<double> normalize(const std::vector<double>& data);
} // namespace mymath

#endif // MYMATH_H
