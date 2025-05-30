import pandas as pd
import matplotlib.pyplot as plt
import os
import glob
import numpy as np
from collections import defaultdict
from scipy import stats

def extract_original_filename(query_filename):
    """Extract original filename from augmented filename."""
    import re
    pattern = r'_segment\d+_(white|pink|brown)_intensity_[\d.]+\.freqs$'
    original_name = re.sub(pattern, '.freqs', query_filename)
    return original_name

def extract_noise_info(query_filename):
    """Extract noise type and intensity from filename."""
    import re
    pattern = r'.*_segment\d+_(white|pink|brown)_intensity_([\d.]+)\.freqs$'
    match = re.search(pattern, query_filename)
    if match:
        noise_type = match.group(1)
        intensity = float(match.group(2))
        return noise_type, intensity
    return None, None

def calculate_accuracy_with_statistics(df, compressor_name):
    """Calculate accuracy with statistical analysis."""
    if df.empty:
        return {}
    
    # Extract information
    df['original_query'] = df['music query'].apply(extract_original_filename)
    noise_info = df['music query'].apply(extract_noise_info)
    df['extracted_noise_type'] = [info[0] for info in noise_info]
    df['extracted_intensity'] = [info[1] for info in noise_info]
    df['is_correct'] = df['original_query'] == df['result']
    
    # Remove invalid data
    valid_df = df.dropna(subset=['extracted_noise_type', 'extracted_intensity'])
    
    if len(valid_df) == 0:
        return {}
    
    results = {}
    
    for noise_type in valid_df['extracted_noise_type'].unique():
        if pd.isna(noise_type) or noise_type == '':
            continue
            
        noise_df = valid_df[valid_df['extracted_noise_type'] == noise_type]
        
        # Collect data for analysis
        intensities = []
        accuracies = []
        sample_counts = []
        confidence_intervals = []
        
        for intensity in sorted(noise_df['extracted_intensity'].unique()):
            if pd.isna(intensity):
                continue
                
            intensity_df = noise_df[noise_df['extracted_intensity'] == intensity]
            if not intensity_df.empty:
                correct_count = intensity_df['is_correct'].sum()
                total_count = len(intensity_df)
                accuracy = (correct_count / total_count) * 100
                
                # Calculate confidence interval using Wilson score interval
                if total_count > 0:
                    p = correct_count / total_count
                    n = total_count
                    z = 1.96  # 95% confidence
                    
                    # Wilson score interval
                    center = (p + z**2/(2*n)) / (1 + z**2/n)
                    margin = z * np.sqrt((p*(1-p) + z**2/(4*n)) / n) / (1 + z**2/n)
                    
                    ci_lower = max(0, (center - margin) * 100)
                    ci_upper = min(100, (center + margin) * 100)
                    
                    intensities.append(intensity)
                    accuracies.append(accuracy)
                    sample_counts.append(total_count)
                    confidence_intervals.append((ci_lower, ci_upper))
        
        if len(intensities) > 1:
            # Analyze the trend
            correlation, p_value = stats.pearsonr(intensities, accuracies)
            
            # Perform trend analysis
            slope, intercept, r_value, p_val_trend, std_err = stats.linregress(intensities, accuracies)
            
            # Check for statistical significance of differences
            significant_changes = []
            for i in range(1, len(accuracies)):
                # Check if confidence intervals don't overlap significantly
                prev_ci = confidence_intervals[i-1]
                curr_ci = confidence_intervals[i]
                
                # If the CIs don't overlap, it's likely a significant change
                if curr_ci[1] < prev_ci[0] or curr_ci[0] > prev_ci[1]:
                    change = accuracies[i] - accuracies[i-1]
                    significant_changes.append({
                        'from_intensity': intensities[i-1],
                        'to_intensity': intensities[i],
                        'change': change,
                        'from_samples': sample_counts[i-1],
                        'to_samples': sample_counts[i]
                    })
            
            # Store detailed results
            results[noise_type] = {
                'accuracy_data': dict(zip(intensities, accuracies)),
                'sample_counts': dict(zip(intensities, sample_counts)),
                'confidence_intervals': dict(zip(intensities, confidence_intervals)),
                'statistics': {
                    'correlation': correlation,
                    'correlation_p_value': p_value,
                    'slope': slope,
                    'r_squared': r_value**2,
                    'trend_p_value': p_val_trend,
                    'significant_changes': significant_changes
                }
            }
            
            # Print analysis
            print(f"\n=== {compressor_name} - {noise_type.upper()} NOISE ===")
            print(f"Intensities: {intensities}")
            print(f"Accuracies:  {[f'{acc:.1f}%' for acc in accuracies]}")
            print(f"Sample sizes: {sample_counts}")
            
            # Interpret the trend
            if abs(correlation) < 0.1:
                trend_desc = "No correlation"
            elif correlation < -0.3:
                trend_desc = "Strong negative correlation (accuracy decreases with noise)"
            elif correlation < 0:
                trend_desc = "Weak negative correlation (slight decrease with noise)"
            elif correlation < 0.3:
                trend_desc = "Weak positive correlation (slight increase with noise)"
            else:
                trend_desc = "Strong positive correlation (accuracy increases with noise)"
            
            print(f"Trend: {trend_desc} (r={correlation:.3f}, p={p_value:.3f})")
            print(f"Linear fit: slope={slope:.3f}, R²={r_value**2:.3f}, p={p_val_trend:.3f}")
            
            # Assess if flat trend is concerning
            if abs(slope) < 1.0 and p_val_trend > 0.05:
                print("✅ ASSESSMENT: Flat accuracy trend - not statistically significant change")
                print("   This could be normal if:")
                print("   - Algorithm is robust to this noise range")
                print("   - Noise levels are too low to affect fingerprints significantly")
                print("   - Sample size is small causing high variance")
            elif slope > 1.0 and p_val_trend < 0.05:
                print("⚠️  ASSESSMENT: Accuracy significantly INCREASES with noise")
                print("   This suggests a potential issue in your experimental setup")
            elif slope < -1.0 and p_val_trend < 0.05:
                print("✅ ASSESSMENT: Accuracy significantly DECREASES with noise (expected)")
            else:
                print("🤔 ASSESSMENT: Unclear trend - needs more investigation")
            
            # Check confidence intervals
            overlapping_intervals = 0
            for i in range(1, len(confidence_intervals)):
                prev_ci = confidence_intervals[i-1]
                curr_ci = confidence_intervals[i]
                if not (curr_ci[1] < prev_ci[0] or curr_ci[0] > prev_ci[1]):
                    overlapping_intervals += 1
            
            if overlapping_intervals == len(confidence_intervals) - 1:
                print("📊 STATISTICAL NOTE: All confidence intervals overlap")
                print("   -> Differences might not be statistically significant")
                print("   -> Consider collecting more samples or using different noise levels")
            
            print(f"Confidence intervals (95%):")
            for i, intensity in enumerate(intensities):
                ci = confidence_intervals[i]
                n = sample_counts[i]
                print(f"  {intensity}: {accuracies[i]:.1f}% [{ci[0]:.1f}%, {ci[1]:.1f}%] (n={n})")
    
    return results

def create_enhanced_plots(compressor_results, save_dir=None):
    """Create plots with confidence intervals and statistical information."""
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
    
    # Get all noise types
    noise_types = set()
    for comp_data in compressor_results.values():
        noise_types.update(comp_data.keys())
    
    for noise_type in sorted(noise_types):
        plt.figure(figsize=(14, 8))
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                  '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        
        legend_info = []
        
        for i, (compressor_name, comp_data) in enumerate(compressor_results.items()):
            if noise_type in comp_data:
                data = comp_data[noise_type]
                intensities = sorted(data['accuracy_data'].keys())
                accuracies = [data['accuracy_data'][intensity] for intensity in intensities]
                cis = [data['confidence_intervals'][intensity] for intensity in intensities]
                
                # Plot main line
                plt.plot(intensities, [acc/100 for acc in accuracies], 
                        marker='o', linewidth=2, markersize=8, 
                        color=colors[i % len(colors)], alpha=0.8, label=compressor_name)
                
                # Plot confidence intervals
                ci_lower = [ci[0]/100 for ci in cis]
                ci_upper = [ci[1]/100 for ci in cis]
                plt.fill_between(intensities, ci_lower, ci_upper, 
                               color=colors[i % len(colors)], alpha=0.2)
                
                # Add trend info to legend
                stats_data = data['statistics']
                r = stats_data['correlation']
                p_val = stats_data['trend_p_value']
                trend_sig = "*" if p_val < 0.05 else ""
                legend_info.append(f"{compressor_name} (r={r:.2f}{trend_sig})")
        
        # Customize plot
        plt.xlabel('Noise Intensity', fontsize=12, fontweight='bold')
        plt.ylabel('Accuracy', fontsize=12, fontweight='bold')
        plt.title(f'Accuracy vs {noise_type.title()} Noise Intensity\n(with 95% confidence intervals)', 
                  fontsize=14, fontweight='bold')
        
        plt.ylim(0, 1.0)
        plt.grid(True, alpha=0.3, linestyle='--')
        plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.1%}'))
        
        # Enhanced legend
        plt.legend(legend_info, title='Compressor (correlation*=significant)', 
                  loc='best', framealpha=0.9)
        
        # Add note about statistical significance
        plt.figtext(0.02, 0.02, "* = statistically significant trend (p < 0.05)\nShaded areas = 95% confidence intervals", 
                   fontsize=9, style='italic')
        
        plt.tight_layout()
        
        if save_dir:
            save_path = os.path.join(save_dir, f"enhanced_accuracy_{noise_type}.png")
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Enhanced plot saved: {save_path}")
        
        plt.show()

def main():
    results_folder = "../results"
    
    print("🔬 STATISTICAL ANALYSIS OF AUDIO FINGERPRINTING ACCURACY")
    print("=" * 70)
    
    # Process files
    csv_files = glob.glob(os.path.join(results_folder, "*.csv"))
    compressor_results = {}
    
    for csv_file in csv_files:
        try:
            compressor_name = os.path.splitext(os.path.basename(csv_file))[0]
            df = pd.read_csv(csv_file)
            
            results = calculate_accuracy_with_statistics(df, compressor_name)
            if results:
                compressor_results[compressor_name] = results
                
        except Exception as e:
            print(f"Error processing {csv_file}: {e}")
    
    if compressor_results:
        print(f"\n" + "=" * 70)
        print("📈 CREATING ENHANCED PLOTS WITH STATISTICAL ANALYSIS")
        print("=" * 70)
        create_enhanced_plots(compressor_results, "statistical_plots")
    else:
        print("No valid data found!")

if __name__ == "__main__":
    main()