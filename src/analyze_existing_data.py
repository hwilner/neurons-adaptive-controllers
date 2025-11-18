"""
Analyze existing Buzsaki dataset (25 neurons)
This serves as a baseline before scaling up to larger datasets.

Author: Harel Joseph Wilner
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys

# Add code directory to path
sys.path.insert(0, '/home/user/paper1_upgrade/code')
from control_models import OptimalController, compare_models, preprocess_spike_train

# Set style
sns.set_style('whitegrid')
sns.set_context('paper')

def load_buzsaki_data(data_dir: str = '/home/user/papers/paper1_review'):
    """
    Load existing results from Paper 1.
    
    Returns:
    --------
    results_df : pd.DataFrame
        Existing analysis results
    """
    data_path = Path(data_dir)
    
    # Load existing results
    results_file = data_path / 'final_curated_results.csv'
    
    if results_file.exists():
        try:
            df = pd.read_csv(results_file)
            if len(df) > 0:
                print(f"Loaded {len(df)} neurons from existing analysis")
                return df
            else:
                print(f"Results file is empty")
                return None
        except Exception as e:
            print(f"Error loading results: {e}")
            return None
    else:
        print(f"Results file not found: {results_file}")
        return None


def analyze_single_neuron_example(neuron_idx: int = 0):
    """
    Detailed analysis of a single example neuron.
    """
    print(f"\n{'='*60}")
    print(f"SINGLE NEURON EXAMPLE ANALYSIS (Neuron {neuron_idx})")
    print(f"{'='*60}\n")
    
    # Generate example data (replace with real data loading)
    # In real analysis, you would load from spike times
    np.random.seed(neuron_idx)
    t = np.linspace(0, 600, 6000)  # 600 seconds, 100ms bins
    
    # Simulate realistic hippocampal firing
    # CA1 neurons typically fire 0.5-5 Hz with bursting
    base_rate = np.random.uniform(1, 5)
    firing_rate = base_rate + 2*np.sin(2*np.pi*0.01*t)  # Slow modulation
    firing_rate += 1*np.sin(2*np.pi*0.1*t)  # Faster modulation
    firing_rate += np.random.randn(len(t)) * 0.5  # Noise
    firing_rate = np.maximum(firing_rate, 0.1)  # No zero rates
    
    print(f"Neuron properties:")
    print(f"  Mean firing rate: {np.mean(firing_rate):.2f} Hz")
    print(f"  Std: {np.std(firing_rate):.2f} Hz")
    print(f"  Duration: {len(firing_rate)/10:.1f} seconds")
    
    # Fit all models
    print(f"\nFitting control models...")
    results = compare_models(firing_rate, verbose=True)
    
    # Display results
    print(f"\n{'='*60}")
    print("MODEL COMPARISON RESULTS")
    print(f"{'='*60}")
    
    results_list = []
    for model_name, model_results in results.items():
        if 'r2' in model_results:
            print(f"\n{model_name}:")
            print(f"  R² = {model_results['r2']:.4f}")
            if 'mse' in model_results:
                print(f"  MSE = {model_results['mse']:.4f}")
            if 'correlation' in model_results:
                print(f"  Correlation = {model_results['correlation']:.4f}")
            
            results_list.append({
                'model': model_name,
                'r2': model_results['r2'],
                'n_params': model_results.get('n_params', np.nan)
            })
    
    results_df = pd.DataFrame(results_list)
    
    # Create visualization
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    
    # Panel A: Firing rate trace
    ax = axes[0, 0]
    ax.plot(t[:1000], firing_rate[:1000], 'k-', linewidth=0.5, alpha=0.7)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Firing Rate (Hz)')
    ax.set_title('A. Example Neural Activity')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Panel B: Model comparison
    ax = axes[0, 1]
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
    results_df_sorted = results_df.sort_values('r2', ascending=False)
    bars = ax.barh(range(len(results_df_sorted)), results_df_sorted['r2'], color=colors)
    ax.set_yticks(range(len(results_df_sorted)))
    ax.set_yticklabels(results_df_sorted['model'])
    ax.set_xlabel('R² Score')
    ax.set_title('B. Model Performance')
    ax.axvline(0, color='k', linewidth=0.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Panel C: Optimal Controller fit
    ax = axes[1, 0]
    oc_results = results['Optimal Controller']
    if 'predictions' in oc_results and 'targets' in oc_results:
        pred = oc_results['predictions'][:200]
        target = oc_results['targets'][:200]
        time_test = np.arange(len(pred)) * 0.1
        
        ax.plot(time_test, target, 'k-', alpha=0.5, linewidth=1, label='Actual')
        ax.plot(time_test, pred, 'r-', linewidth=1, label='Predicted')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Firing Rate (Hz)')
        ax.set_title(f'C. Optimal Controller Fit (R²={oc_results["r2"]:.3f})')
        ax.legend(frameon=False)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    
    # Panel D: Prediction scatter
    ax = axes[1, 1]
    if 'predictions' in oc_results and 'targets' in oc_results:
        pred = oc_results['predictions']
        target = oc_results['targets']
        
        ax.scatter(target, pred, s=1, alpha=0.3, c='#2E86AB')
        
        # Unity line
        min_val = min(target.min(), pred.min())
        max_val = max(target.max(), pred.max())
        ax.plot([min_val, max_val], [min_val, max_val], 'k--', linewidth=1, alpha=0.5)
        
        ax.set_xlabel('Actual Firing Rate (Hz)')
        ax.set_ylabel('Predicted Firing Rate (Hz)')
        ax.set_title(f'D. Prediction vs Actual (r={oc_results["correlation"]:.3f})')
        ax.axis('equal')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    
    # Save figure
    output_dir = Path('/home/user/paper1_upgrade/figures')
    output_dir.mkdir(exist_ok=True)
    fig.savefig(output_dir / f'example_neuron_{neuron_idx}_analysis.png', 
                dpi=300, bbox_inches='tight')
    print(f"\nFigure saved to: {output_dir / f'example_neuron_{neuron_idx}_analysis.png'}")
    
    plt.close()
    
    return results


def summarize_existing_results():
    """
    Summarize the existing 25-neuron analysis.
    """
    print(f"\n{'='*60}")
    print("SUMMARY OF EXISTING ANALYSIS (25 NEURONS)")
    print(f"{'='*60}\n")
    
    # Load existing results
    df = load_buzsaki_data()
    
    if df is not None:
        print(f"Dataset: Buzsaki Lab - Hippocampus CA1")
        print(f"Number of neurons: {len(df)}")
        print(f"Brain region: Hippocampus")
        
        # Find Optimal Controller and AR model columns
        oc_col = [col for col in df.columns if 'Optimal' in col and 'r2' in col.lower()]
        ar_col = [col for col in df.columns if 'AR' in col and 'r2' in col.lower()]
        
        if oc_col:
            oc_r2 = df[oc_col[0]]
            print(f"\nOptimal Controller:")
            print(f"  Mean R² = {oc_r2.mean():.3f} ± {oc_r2.std():.3f}")
            print(f"  Median R² = {oc_r2.median():.3f}")
            print(f"  Range: [{oc_r2.min():.3f}, {oc_r2.max():.3f}]")
        
        if ar_col:
            ar_r2 = df[ar_col[0]]
            print(f"\nAR Model:")
            print(f"  Mean R² = {ar_r2.mean():.3f} ± {ar_r2.std():.3f}")
            print(f"  Median R² = {ar_r2.median():.3f}")
            print(f"  Range: [{ar_r2.min():.3f}, {ar_r2.max():.3f}]")
        
        print(f"\n{'='*60}")
        print("NEXT STEPS:")
        print(f"{'='*60}")
        print("1. Expand to 300-500 neurons from multiple brain regions")
        print("2. Add behavioral alignment analysis")
        print("3. Test hierarchical scaling hypothesis")
        print("4. Create publication-quality figures")
        print(f"{'='*60}\n")
    
    return df


def main():
    """Main analysis pipeline."""
    print(f"\n{'='*80}")
    print("PAPER 1 UPGRADE - BASELINE ANALYSIS")
    print(f"{'='*80}\n")
    
    # Step 1: Summarize existing results
    existing_df = summarize_existing_results()
    
    # Step 2: Analyze example neuron in detail
    example_results = analyze_single_neuron_example(neuron_idx=0)
    
    # Step 3: Test on a few more examples
    print(f"\nTesting on additional synthetic neurons...")
    all_results = []
    
    for i in range(5):
        results = analyze_single_neuron_example(neuron_idx=i)
        if 'Optimal Controller' in results:
            all_results.append({
                'neuron_id': i,
                'r2_optimal': results['Optimal Controller']['r2'],
                'r2_ar': results['AR Model']['r2'],
                'r2_pid': results['PID Controller']['r2']
            })
    
    results_df = pd.DataFrame(all_results)
    
    print(f"\nSynthetic Test Results (n={len(results_df)}):")
    print(f"  Optimal Controller: R² = {results_df['r2_optimal'].mean():.3f} ± {results_df['r2_optimal'].std():.3f}")
    print(f"  AR Model: R² = {results_df['r2_ar'].mean():.3f} ± {results_df['r2_ar'].std():.3f}")
    print(f"  PID Controller: R² = {results_df['r2_pid'].mean():.3f} ± {results_df['r2_pid'].std():.3f}")
    
    print(f"\n{'='*80}")
    print("BASELINE ANALYSIS COMPLETE!")
    print(f"{'='*80}")
    print("\nNext: Run 'python code/download_ibl_data.py' to access larger datasets")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
