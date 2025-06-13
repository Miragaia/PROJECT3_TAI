#include <iostream>
#include <vector>
#include <string>
#include <filesystem>
#include <fstream>
#include <algorithm>
#include <limits>
#include <cstring>
#include <map>
#include "freq_loader.hpp"
#include "ncd.hpp"
#include "utils.hpp"

namespace fs = std::filesystem;

struct GenreDatabase {
    std::map<std::string, std::vector<std::pair<std::string, std::vector<uint8_t>>>> genres;

    void load_from_directory(const std::string& base_dir) {
        for (const auto& genre_entry : fs::directory_iterator(base_dir)) {
            if (genre_entry.is_directory()) {
                std::string genre_name = genre_entry.path().filename().string();
                
                for (const auto& file_entry : fs::directory_iterator(genre_entry.path())) {
                    if (file_entry.path().extension() == ".freqs") {
                        std::vector<uint8_t> data = load_freq_file(file_entry.path().string());
                        genres[genre_name] = {
                            std::make_pair(file_entry.path().filename().string(), std::move(data))
                        };
                        break;  // Only one .freqs file per folder
                    }
                }
            }
        }
    }
};

std::string identify_genre(const std::vector<uint8_t>& query_data, 
                          const GenreDatabase& genre_db, 
                          const std::string& compressor) {
    std::map<std::string, double> genre_scores;
    std::map<std::string, int> genre_counts;
    
    // Initialize genre scores
    for (const auto& [genre, files] : genre_db.genres) {
        genre_scores[genre] = 0.0;
        genre_counts[genre] = 0;
    }
    
    // Compute NCD with all files in each genre
    for (const auto& [genre, files] : genre_db.genres) {
        for (const auto& [filename, file_data] : files) {
            std::cout<<compressor<<std::endl;
            double ncd_value = compute_ncd(query_data, file_data, compressor);
            genre_scores[genre] += ncd_value;
            genre_counts[genre]++;
        }
    }
    
    // Calculate average NCD for each genre
    std::string best_genre;
    double best_avg_ncd = std::numeric_limits<double>::max();
    
    for (const auto& [genre, total_score] : genre_scores) {
        if (genre_counts[genre] > 0) {
            double avg_ncd = total_score / genre_counts[genre];
            std::cout << "Genre: " << genre << " - Average NCD: " << avg_ncd << std::endl;
            
            if (avg_ncd < best_avg_ncd) {
                best_avg_ncd = avg_ncd;
                best_genre = genre;
            }
        }
    }
    std::cout << "Identified Genre: " << best_genre << " with avg NCD: " << best_avg_ncd << std::endl;
    return best_genre;
}

int main(int argc, char* argv[]) {
    std::string db_dir = "database/";
    std::string query_dir = "queries/";
    std::string compressor = "gzip";
    std::string single_query_file;
    std::string output_csv;
    bool genre_mode = false;
    std::string genre_db_dir = "database2/";

    // Parse command line arguments
    for (int i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--compressor") == 0 && i + 1 < argc) {
            compressor = argv[i + 1];
            ++i;
        } else if (strcmp(argv[i], "--query") == 0 && i + 1 < argc) {
            single_query_file = argv[i + 1];
            ++i;
        } else if (strcmp(argv[i], "--output") == 0 && i + 1 < argc) {
            output_csv = argv[i + 1];
            ++i;
        } else if (strcmp(argv[i], "--genre") == 0) {
            genre_mode = true;
        } else {
            output_csv = "results/results_" + compressor + ".csv";
        }
    }

    if (output_csv.empty()) {
        output_csv = "results/results_" + compressor + ".csv";
    }

    if (genre_mode) {
        // Genre identification mode
        GenreDatabase genre_db;
        genre_db.load_from_directory(genre_db_dir);
        
        std::cout << "Loaded genres: ";
        for (const auto& [genre, files] : genre_db.genres) {
            std::cout << genre << "(" << files.size() << " files) ";
        }
        std::cout << std::endl;

        if (!single_query_file.empty()) {
            if (!fs::exists(single_query_file)) {
                std::cerr << "[ERRO] O ficheiro de consulta \"" << single_query_file << "\" não existe." << std::endl;
                return 1;
            }
            // Single query genre identification
            std::cout<<single_query_file<<std::endl;
            std::string qname = fs::path(single_query_file).filename().string();
            std::cout<<qname<<std::endl;
            auto qdata = load_freq_file(single_query_file);
            
            std::string identified_genre = identify_genre(qdata, genre_db, compressor);
            std::cout << "Query: " << qname << " => Identified Genre: " << identified_genre << std::endl;
            
        } else {
            // Batch genre identification with CSV output
            std::ofstream csv("results/genre/results_genre_"+compressor+".csv");
            csv << "music query,identified genre,confidence,expected genre,correct\n";
            
            for (const auto& qentry : fs::directory_iterator("queries_genre/")) {
                if (qentry.path().extension() == ".freqs") {
                    std::string qname = qentry.path().filename().string();
                    auto qdata = load_freq_file(qentry.path().string());

                    std::cout << "\nProcessing: " << qname << std::endl;
                    std::string identified_genre = identify_genre(qdata, genre_db, compressor);

                    // Calcular confiança (inverso da NCD média do género identificado)
                    double confidence = 0.0;
                    double best_avg_ncd = std::numeric_limits<double>::max();

                    for (const auto& [genre, files] : genre_db.genres) {
                        double total_ncd = 0.0;
                        for (const auto& [filename, file_data] : files) {
                            total_ncd += compute_ncd(qdata, file_data, compressor);
                        }
                        if (!files.empty()) {
                            double avg_ncd = total_ncd / files.size();
                            if (genre == identified_genre) {
                                confidence = 1.0 - avg_ncd;
                            }
                            if (avg_ncd < best_avg_ncd) {
                                best_avg_ncd = avg_ncd;
                            }
                        }
                    }

                    // Extrair género esperado do nome do ficheiro (antes do primeiro '_')
                    std::string expected_genre;
                    size_t underscore_pos = qname.find('_');
                    if (underscore_pos != std::string::npos) {
                        expected_genre = qname.substr(0, underscore_pos);
                    } else {
                        expected_genre = "unknown";
                    }

                    bool correct = (expected_genre == identified_genre);

                    std::cout << "Result: " << qname << " => Genre: " << identified_genre 
                            << " (Expected: " << expected_genre << ", Confidence: " << confidence << ")\n";

                    csv << qname << "," << identified_genre << "," << confidence << ","
                        << expected_genre << "," << (correct ? "true" : "false") << "\n";
                }
            }

        }
        
    } else {
        // Original music identification mode
        std::vector<std::pair<std::string, std::vector<uint8_t>>> database;
        for (const auto& entry : fs::directory_iterator(db_dir)) {
            if (entry.path().extension() == ".freqs") {
                database.emplace_back(entry.path().filename().string(), load_freq_file(entry.path().string()));
            }
        }

        if (!single_query_file.empty()) {
            // Handle single query mode
            std::string qname = fs::path(single_query_file).filename().string();
            auto qdata = load_freq_file(single_query_file);

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

        } else {
            // Batch mode with CSV output
            std::ofstream csv(output_csv);
            csv << "music query,noise type,noise intensity,result,NCD,expected\n";



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

                    std::string base_name = qname;
                    if (base_name.size() >= 6 && base_name.substr(base_name.size() - 6) == ".freqs") {
                        base_name = base_name.substr(0, base_name.size() - 6);
                    }
                    std::string noise_type = "unknown", intensity = "unknown";
                    size_t p1 = base_name.find("_");
                    size_t p2 = base_name.find("_intensity_");
                    if (p1 != std::string::npos && p2 != std::string::npos) {
                        noise_type = base_name.substr(p1 + 1, p2 - p1 - 1);
                        intensity = base_name.substr(p2 + 11);
                    }

                    std::string expected_base = qname.substr(0, qname.find('_'));
                    std::string actual_base = best_match.substr(0, best_match.find('.'));
                    std::transform(expected_base.begin(), expected_base.end(), expected_base.begin(), ::tolower);
                    std::transform(actual_base.begin(), actual_base.end(), actual_base.begin(), ::tolower);
                    bool is_expected = actual_base.find(expected_base) != std::string::npos;

                    csv << qname << "," << noise_type << "," << intensity << ","
                        << best_match << "," << best_ncd << "," << (is_expected ? "true" : "false") << "\n";
                }
            }
        }
    }

    return 0;
}