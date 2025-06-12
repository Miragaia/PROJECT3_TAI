#include "utils.hpp"
#include <zlib.h>
#include <bzlib.h>
#include <zstd.h>
#include <lzma.h>
#include <lzo/lzo1x.h>
#include <snappy.h>
#include <vector>
#include <cstring>
#include <stdexcept>
#include <lz4.h>

int compress_zlib(const std::vector<uint8_t>& data) {
    uLongf compressedSize = compressBound(data.size());
    std::vector<uint8_t> compressed(compressedSize);
    compress(compressed.data(), &compressedSize, data.data(), data.size());
    return compressedSize;
}

int compress_bzip2(const std::vector<uint8_t>& data) {
    unsigned int compressedSize = data.size() * 1.01 + 600;
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

int compress_lzma(const std::vector<uint8_t>& data) {
    size_t out_pos = 0;
    size_t out_size = data.size() * 2;
    std::vector<uint8_t> compressed(out_size);
    lzma_ret ret = lzma_easy_buffer_encode(6, LZMA_CHECK_CRC64, NULL,
                                           data.data(), data.size(),
                                           compressed.data(), &out_pos, out_size);
    if (ret != LZMA_OK) throw std::runtime_error("LZMA compression failed");
    return out_pos;
}

int compress_lzo(const std::vector<uint8_t>& data) {
    static bool lzo_initialized = false;
    if (!lzo_initialized) {
        if (lzo_init() != LZO_E_OK) throw std::runtime_error("LZO initialization failed");
        lzo_initialized = true;
    }
    std::vector<uint8_t> compressed(data.size() + data.size() / 16 + 64 + 3);
    std::vector<uint8_t> wrkmem(LZO1X_1_MEM_COMPRESS);
    lzo_uint out_len;
    int r = lzo1x_1_compress(data.data(), data.size(), compressed.data(), &out_len, wrkmem.data());
    if (r != LZO_E_OK) throw std::runtime_error("LZO compression failed");
    return out_len;
}

int compress_snappy(const std::vector<uint8_t>& data) {
    size_t max_len = snappy::MaxCompressedLength(data.size());
    std::string output;
    output.resize(max_len);
    size_t out_len;
    snappy::RawCompress(reinterpret_cast<const char*>(data.data()), data.size(), &output[0], &out_len);
    if (out_len == 0) throw std::runtime_error("Snappy compression failed");
    return static_cast<int>(out_len);
}

int compress_lz4(const std::vector<uint8_t>& data) {
    int max_dst_size = LZ4_compressBound(data.size());
    std::vector<char> compressed(max_dst_size);

    int compressed_size = LZ4_compress_default(
        reinterpret_cast<const char*>(data.data()), 
        compressed.data(),                           
        data.size(),                                 
        max_dst_size                               
    );

    if (compressed_size <= 0) {
        throw std::runtime_error("LZ4 compression failed");
    }

    return compressed_size;
}



int compress_size(const std::vector<uint8_t>& data, Compressor compressor) {
    switch (compressor) {
        case Compressor::ZLIB:
            return compress_zlib(data);
        case Compressor::BZIP2:
            return compress_bzip2(data);
        case Compressor::ZSTD:
            return compress_zstd(data);
        case Compressor::LZMA:
            return compress_lzma(data);
        case Compressor::LZO:
            return compress_lzo(data);
        case Compressor::SNAPPY:
            return compress_snappy(data);
        case Compressor::LZ4:
            return compress_lz4(data);
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
    if (name == "gzip") return Compressor::ZLIB;
    if (name == "bzip2") return Compressor::BZIP2;
    if (name == "zstd") return Compressor::ZSTD;
    if (name == "lzma") return Compressor::LZMA;
    if (name == "lzo") return Compressor::LZO;
    if (name == "snappy") return Compressor::SNAPPY;
    if (name == "lz4") return Compressor::LZ4;
    throw std::invalid_argument("Unknown compressor name: " + name);
}
