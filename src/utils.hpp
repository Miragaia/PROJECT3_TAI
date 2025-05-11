#ifndef UTILS_HPP
#define UTILS_HPP

#include <vector>
#include <cstdint>
#include <string>

enum class Compressor {
    ZLIB,
    BZIP2,
    ZSTD
};

int compress_size(const std::vector<uint8_t>& data, Compressor compressor);
std::vector<uint8_t> concat_vectors(const std::vector<uint8_t>& a, const std::vector<uint8_t>& b);
Compressor compressor_from_string(const std::string& str);

#endif