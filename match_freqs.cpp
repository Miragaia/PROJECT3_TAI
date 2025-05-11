#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <filesystem>
#include <algorithm>

namespace fs = std::filesystem;

// Compare the query and reference .freqs files and return a match score
int compare_freqs(const std::string& query_path, const std::string& ref_path, size_t window_size = 4) {
std::ifstream query_file(query_path, std::ios::binary);
std::ifstream ref_file(ref_path, std::ios::binary);

if (!query_file || !ref_file) {
    std::cerr << "Error opening files: " << query_path << " or " << ref_path << std::endl;
    return -1;
}

std::vector<unsigned char> query((std::istreambuf_iterator<char>(query_file)),
                                  std::istreambuf_iterator<char>());
std::vector<unsigned char> ref((std::istreambuf_iterator<char>(ref_file)),
                                std::istreambuf_iterator<char>());

int match_score = 0;
size_t num_windows = std::min(query.size(), ref.size()) / window_size;

for (size_t i = 0; i < num_windows; ++i) {
    for (size_t j = 0; j < window_size; ++j) {
        if (query[i * window_size + j] == ref[i * window_size + j]) {
            match_score++;
        }
    }
}

return match_score;
}

int main(int argc, char* argv[]) {
if (argc < 3) {
std::cerr << "Usage: " << argv[0] << " <query.freqs> <reference_folder>" << std::endl;
return 1;
}
std::string query_path = argv[1];
std::string ref_folder = argv[2];

std::vector<std::pair<std::string, int>> results;

for (const auto& entry : fs::directory_iterator(ref_folder)) {
    if (entry.path().extension() == ".freqs") {
        std::string ref_path = entry.path().string();
        int score = compare_freqs(query_path, ref_path);
        if (score >= 0) {
            results.emplace_back(entry.path().filename().string(), score);
        }
    }
}

// Sort by descending match score
std::sort(results.begin(), results.end(), [](const auto& a, const auto& b) {
    return a.second > b.second;
});

std::cout << "Similarity Ranking:\n";
for (const auto& [filename, score] : results) {
    std::cout << filename << ": " << score << std::endl;
}

return 0;
}