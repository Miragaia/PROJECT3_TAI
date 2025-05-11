#include <iostream>
#include <vector>
#include <string>
#include <filesystem>
#include <fstream>
#include <algorithm>
#include <limits>
#include <cstring>
#include "freq_loader.hpp"
#include "ncd.hpp"
#include "utils.hpp"

namespace fs = std::filesystem;

int main(int argc, char* argv[]) {
    std::string db_dir = "database/";
    std::string query_dir = "queries/";
    std::string output_csv = "results/results.csv";
    std::string compressor = "zlib";  // default compressor

    for (int i = 1; i < argc; ++i) {
    if (strcmp(argv[i], "--compressor") == 0 && i + 1 < argc) {
        compressor = argv[i + 1];
        ++i;
    }
}

std::ofstream csv(output_csv);
csv << "music query,noise type,noise intensity,result,NCD\n";

// Load database .freqs files
std::vector<std::pair<std::string, std::vector<uint8_t>>> database;
for (const auto& entry : fs::directory_iterator(db_dir)) {
    if (entry.path().extension() == ".freqs") {
        database.emplace_back(entry.path().filename().string(), load_freq_file(entry.path().string()));
    }
}

// Process each query
for (const auto& qentry : fs::directory_iterator(query_dir)) {
    if (qentry.path().extension() == ".freqs") {
        std::string qname = qentry.path().filename().string();
        auto qdata = load_freq_file(qentry.path().string());

        std::string best_match;
        double best_ncd = std::numeric_limits<double>::max();

        for (const auto& [dname, ddata] : database) {
            double ncd_value = compute_ncd(qdata, ddata, compressor);
            if (ncd_value < best_ncd) {
                best_ncd = ncd_value;
                best_match = dname;
            }
        }

        std::cout << "Query: " << qname << " => Best Match: " << best_match << " (NCD = " << best_ncd << ")\n";

        std::string noise_type = "unknown", intensity = "unknown";
        size_t p1 = qname.find("_");
        size_t p2 = qname.find("_intensity_");
        if (p1 != std::string::npos && p2 != std::string::npos) {
            noise_type = qname.substr(p1 + 1, p2 - p1 - 1);
            intensity = qname.substr(p2 + 11);
        }

        csv << qname << "," << noise_type << "," << intensity << ","
            << best_match << "," << best_ncd << "\n";
    }
}

return 0;
}