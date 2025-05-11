#ifndef FREQ_LOADER_HPP
#define FREQ_LOADER_HPP

#include <vector>
#include <string>
#include <cstdint>

std::vector<uint8_t> load_freq_file(const std::string& path);

#endif