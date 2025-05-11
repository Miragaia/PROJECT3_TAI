#include <iostream>
#include <vector>
#include <string>
#include <filesystem>
#include <fstream>
#include <algorithm>
#include <limits>
#include <regex>
#include "freq_loader.hpp"
#include "ncd.hpp"

namespace fs = std::filesystem;

std::string extract_noise_type(const std::string& filename) {
std::smatch match;
if (std::regex_search(filename, match, std::regex("(white|pink|brown)"))) {
return match[1];
}
return "unknown";
}

std::string extract_intensity(const std::string& filename) {
std::smatch match;
if (std::regex_search(filename, match, std::regex("intensity_([\d.]+)"))) {
return match[1];
}
return "unknown";
}

int main(int argc, char* argv[]) {
    std::string db_dir = "database/";
    std::string query_dir = "queries/";
    std::string results_dir = "results/";
    std::string csv_path = results_dir + "results.csv";
    fs::create_directory(results_dir);
    std::ofstream csv(csv_path);
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

            std::vector<std::pair<std::string, double>> ncd_results;

            for (const auto& [dname, ddata] : database) {
                double ncd_value = compute_ncd(qdata, ddata);
                ncd_results.emplace_back(dname, ncd_value);
            }

            std::sort(ncd_results.begin(), ncd_results.end(),
                    [](const auto& a, const auto& b) {
                        return a.second < b.second;
                    });

            std::cout << "Query: " << qname << " => Top 3 Matches:\n";
            for (size_t i = 0; i < std::min<size_t>(3, ncd_results.size()); ++i) {
                std::cout << "  " << (i + 1) << ". " << ncd_results[i].first
                        << " (NCD = " << ncd_results[i].second << ")\n";
            }
            std::cout << std::endl;

            // Save top match to CSV
            if (!ncd_results.empty()) {
                csv << qname << ','
                    << extract_noise_type(qname) << ','
                    << extract_intensity(qname) << ','
                    << ncd_results[0].first << ','
                    << ncd_results[0].second << '\n';
            }
        }
    }

    csv.close();
    std::cout << "Results saved to: " << csv_path << std::endl;
    return 0;
}