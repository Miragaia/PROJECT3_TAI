#ifndef NCD_HPP
#define NCD_HPP

#include <vector>
#include <cstdint>
#include <string>
#include "utils.hpp"

double compute_ncd(const std::vector<uint8_t>& x, const std::vector<uint8_t>& y, const std::string& compressor_str);

#endif