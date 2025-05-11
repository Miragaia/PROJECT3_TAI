#include "freq_loader.hpp"
#include <fstream>
std::vector<uint8_t> load_freq_file(const std::string& filename) {
    std::ifstream in(filename, std::ios::binary);
    return std::vector<uint8_t>((std::istreambuf_iterator<char>(in)),
                                 std::istreambuf_iterator<char>());
}
