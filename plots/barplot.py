import pandas as pd
import matplotlib.pyplot as plt
import os
import glob
import numpy as np

def extract_original_filename(query_filename):
    """Extract original filename from augmented filename."""
    import re
    # Remove the noise pattern: _{noise_type}_intensity_{value}.freqs
    pattern = r'_segment(1|2|3|4|5|6|7|8|9|10)_(white|pink|brown)_intensity_[\d.]+\.freqs$'
    original_name = re.sub(pattern, '.freqs', query_filename)
    return original_name

def calculate_accuracy(df):
    """Calculate accuracy by comparing original filenames."""
    if df.empty:
        return 0, 0, 0
    
    # Extract original filenames from queries
    df['original_query'] = df['music query'].apply(extract_original_filename)
    
    # Check if prediction is correct (query matches result)
    df['is_correct'] = df['original_query'] == df['result']
    
    total_queries = len(df)
    correct_predictions = df['is_correct'].sum()
    accuracy = (correct_predictions / total_queries) * 100 if total_queries > 0 else 0
    
    return accuracy, correct_predictions, total_queries

def process_results_folder(results_folder):
    """Process all CSV files in the results folder."""
    compressor_results = {}
    
    # Find all CSV files in the results folder
    csv_files = glob.glob(os.path.join(results_folder, "*.csv"))
    
    if not csv_files:
        print(f"No CSV files found in {results_folder}")
        return compressor_results
    
    for csv_file in csv_files:
        try:
            # Extract compressor name from filename
            compressor_name = os.path.splitext(os.path.basename(csv_file))[0]
            
            # Read CSV file
            df = pd.read_csv(csv_file)
            
            # Calculate accuracy
            accuracy, correct, total = calculate_accuracy(df)
            
            compressor_results[compressor_name] = {
                'accuracy': accuracy,
                'correct': correct,
                'total': total,
                'data': df
            }
            
            print(f"{compressor_name}: {accuracy:.2f}% ({correct}/{total})")
            
        except Exception as e:
            print(f"Error processing {csv_file}: {e}")
    
    return compressor_results

def create_accuracy_plot(compressor_results, save_path=None):
    """Create bar plot showing accuracy for each compressor."""
    if not compressor_results:
        print("No data to plot")
        return
    
    # Prepare data for plotting
    compressors = list(compressor_results.keys())
    accuracies = [compressor_results[comp]['accuracy'] for comp in compressors]
    correct_counts = [compressor_results[comp]['correct'] for comp in compressors]
    total_counts = [compressor_results[comp]['total'] for comp in compressors]
    
    # Sort by accuracy (descending)
    sorted_data = sorted(zip(compressors, accuracies, correct_counts, total_counts), 
                        key=lambda x: x[1], reverse=True)
    compressors, accuracies, correct_counts, total_counts = zip(*sorted_data)
    
    # Create the plot
    plt.figure(figsize=(12, 8))
    bars = plt.bar(range(len(compressors)), accuracies, 
                   color='steelblue', alpha=0.8, edgecolor='navy', linewidth=1)
    
    # Customize the plot
    plt.xlabel('Compressor', fontsize=12, fontweight='bold')
    plt.ylabel('Accuracy (%)', fontsize=12, fontweight='bold')
    plt.title('Audio Compressor Accuracy Comparison', fontsize=16, fontweight='bold', pad=20)
    plt.xticks(range(len(compressors)), compressors, rotation=45, ha='right')
    plt.ylim(0, 100)
    
    # Add value labels on top of bars
    for i, (bar, acc, correct, total) in enumerate(zip(bars, accuracies, correct_counts, total_counts)):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                f'{acc:.1f}%\n({correct}/{total})', 
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Add grid for better readability
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Save or show plot
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to: {save_path}")
    
    plt.show()

def create_detailed_analysis(compressor_results, save_path=None):
    """Create detailed analysis with noise type breakdown."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Overall accuracy plot
    compressors = list(compressor_results.keys())
    accuracies = [compressor_results[comp]['accuracy'] for comp in compressors]
    
    # Sort by accuracy
    sorted_data = sorted(zip(compressors, accuracies), key=lambda x: x[1], reverse=True)
    compressors, accuracies = zip(*sorted_data)
    
    bars1 = ax1.bar(range(len(compressors)), accuracies, 
                    color='steelblue', alpha=0.8, edgecolor='navy')
    ax1.set_xlabel('Compressor', fontweight='bold')
    ax1.set_ylabel('Accuracy (%)', fontweight='bold')
    ax1.set_title('Overall Accuracy by Compressor', fontweight='bold')
    ax1.set_xticks(range(len(compressors)))
    ax1.set_xticklabels(compressors, rotation=45, ha='right')
    ax1.set_ylim(0, 100)
    ax1.grid(axis='y', alpha=0.3)
    
    # Add labels on bars
    for bar, acc in zip(bars1, accuracies):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                f'{acc:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    # Noise type analysis (if we have enough data)
    noise_accuracy = {}
    for comp_name, comp_data in compressor_results.items():
        df = comp_data['data']
        for noise_type in ['white', 'pink', 'brown']:
            noise_df = df[df['noise type'] == noise_type]
            if not noise_df.empty:
                acc, _, _ = calculate_accuracy(noise_df)
                if noise_type not in noise_accuracy:
                    noise_accuracy[noise_type] = []
                noise_accuracy[noise_type].append(acc)
    
    if noise_accuracy:
        noise_types = list(noise_accuracy.keys())
        avg_accuracies = [np.mean(noise_accuracy[nt]) for nt in noise_types]
        colors = ['lightcoral', 'lightgreen', 'lightskyblue']
        
        bars2 = ax2.bar(noise_types, avg_accuracies, color=colors, alpha=0.8, edgecolor='black')
        ax2.set_xlabel('Noise Type', fontweight='bold')
        ax2.set_ylabel('Average Accuracy (%)', fontweight='bold')
        ax2.set_title('Average Accuracy by Noise Type', fontweight='bold')
        ax2.set_ylim(0, 100)
        ax2.grid(axis='y', alpha=0.3)
        
        # Add labels
        for bar, acc in zip(bars2, avg_accuracies):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                    f'{acc:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Detailed analysis saved to: {save_path}")
    
    plt.show()

def main():
    # Configuration
    results_folder = "../results"  # Change this to your results folder path
    
    print("Processing audio compressor results...")
    print("=" * 50)
    
    # Process all CSV files
    compressor_results = process_results_folder(results_folder)
    
    if compressor_results:
        print("\n" + "=" * 50)
        print("Creating visualizations...")
        
        # Create simple accuracy plot
        create_accuracy_plot(compressor_results, "compressor_accuracy.png")
        
        # Create detailed analysis
        create_detailed_analysis(compressor_results, "detailed_analysis.png")
        
        # Print summary statistics
        print("\n" + "=" * 50)
        print("SUMMARY STATISTICS")
        print("=" * 50)
        
        best_compressor = max(compressor_results.items(), key=lambda x: x[1]['accuracy'])
        worst_compressor = min(compressor_results.items(), key=lambda x: x[1]['accuracy'])
        avg_accuracy = np.mean([data['accuracy'] for data in compressor_results.values()])
        
        print(f"Best Compressor: {best_compressor[0]} ({best_compressor[1]['accuracy']:.2f}%)")
        print(f"Worst Compressor: {worst_compressor[0]} ({worst_compressor[1]['accuracy']:.2f}%)")
        print(f"Average Accuracy: {avg_accuracy:.2f}%")
        print(f"Total Compressors Tested: {len(compressor_results)}")
    else:
        print("No valid results found. Please check your results folder path.")

if __name__ == "__main__":
    main()