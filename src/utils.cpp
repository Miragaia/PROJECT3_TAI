#include "utils.hpp"
#include <zlib.h>
#include <cstdint>


int compress_size(const std::vector<uint8_t>& data) {
    uLongf compressedSize = compressBound(data.size());
    std::vector<Bytef> compressed(compressedSize);
    compress(compressed.data(), &compressedSize, data.data(), data.size());
    return static_cast<int>(compressedSize);
}

std::vector<uint8_t> concat_vectors(const std::vector<uint8_t>& a, const std::vector<uint8_t>& b) {
    std::vector<uint8_t> result = a;
    result.insert(result.end(), b.begin(), b.end());
    return result;
}
