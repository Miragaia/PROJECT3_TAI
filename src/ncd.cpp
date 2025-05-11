#include "ncd.hpp"
#include "utils.hpp"
#include <cstdint>

double compute_ncd(const std::vector<uint8_t>& x, const std::vector<uint8_t>& y) {
    auto cx = compress_size(x);
    auto cy = compress_size(y);
    auto cxy = compress_size(concat_vectors(x, y));
    return static_cast<double>(cxy - std::min(cx, cy)) / std::max(cx, cy);
}
