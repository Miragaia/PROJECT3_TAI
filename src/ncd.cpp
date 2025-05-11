#include "ncd.hpp"
#include "utils.hpp"

double compute_ncd(const std::vector<uint8_t>& x, const std::vector<uint8_t>& y, const std::string& compressor_str) {
    Compressor compressor = compressor_from_string(compressor_str);

    int Cx = compress_size(x, compressor);
    int Cy = compress_size(y, compressor);
    auto xy = concat_vectors(x, y);
    int Cxy = compress_size(xy, compressor);

    return static_cast<double>(Cxy - std::min(Cx, Cy)) / std::max(Cx, Cy);
}