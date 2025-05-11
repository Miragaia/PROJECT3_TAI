#include "utils.hpp"
#include <zlib.h>
#include <bzlib.h>
#include <zstd.h>
#include <vector>
#include <cstring>
#include <stdexcept>

int compress_zlib(const std::vector<uint8_t>& data) {
    uLongf compressedSize = compressBound(data.size());
    std::vector<uint8_t> compressed(compressedSize);
    compress(compressed.data(), &compressedSize, data.data(), data.size());
    return compressedSize;
}

int compress_bzip2(const std::vector<uint8_t>& data) {
    unsigned int compressedSize = data.size() * 1.01 + 600; // Approximate upper bound
    std::vector<char> compressed(compressedSize);
    int ret = BZ2_bzBuffToBuffCompress(compressed.data(), &compressedSize,
                                      reinterpret_cast<char*>(const_cast<uint8_t*>(data.data())),
                                      data.size(), 9, 0, 30);
    if (ret != BZ_OK) throw std::runtime_error("BZIP2 compression failed");
    return compressedSize;
}

int compress_zstd(const std::vector<uint8_t>& data) {
    size_t compressedSize = ZSTD_compressBound(data.size());
    std::vector<uint8_t> compressed(compressedSize);
    size_t ret = ZSTD_compress(compressed.data(), compressedSize, data.data(), data.size(), 3);
    if (ZSTD_isError(ret)) throw std::runtime_error("ZSTD compression failed");
    return ret;
}

int compress_size(const std::vector<uint8_t>& data, Compressor compressor) {
    switch (compressor) {
        case Compressor::ZLIB:
            return compress_zlib(data);
        case Compressor::BZIP2:
            return compress_bzip2(data);
        case Compressor::ZSTD:
            return compress_zstd(data);
        default:
            throw std::invalid_argument("Unknown compressor type");
    }
}

std::vector<uint8_t> concat_vectors(const std::vector<uint8_t>& a, const std::vector<uint8_t>& b) {
    std::vector<uint8_t> result = a;
    result.insert(result.end(), b.begin(), b.end());
    return result;
}

Compressor compressor_from_string(const std::string& name) {
    if (name == "zlib") return Compressor::ZLIB;
    if (name == "bzip2") return Compressor::BZIP2;
    if (name == "zstd") return Compressor::ZSTD;
    throw std::invalid_argument("Unknown compressor name: " + name);
}

