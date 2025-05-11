#pragma once
#include <vector>
#include <cstdint>

int compress_size(const std::vector<uint8_t>& data);
std::vector<uint8_t> concat_vectors(const std::vector<uint8_t>& a, const std::vector<uint8_t>& b);
