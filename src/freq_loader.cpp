#include "freq_loader.hpp"
#include <fstream>

std::vector<uint8_t> load_freq_file(const std::string& path) {
    std::ifstream file(path, std::ios::binary);
    return std::vector<uint8_t>((std::istreambuf_iterator<char>(file)), std::istreambuf_iterator<char>());
}