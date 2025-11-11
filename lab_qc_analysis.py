"""
Laboratory Quality Control and Statistical Analysis
for Creatinine and Urea Real-time Mocked Data

This script implements:
- Levey-Jennings Charts
- Control Charts with Westgard Rules
- Total Allowable Error (TEa) Analysis
- Sigma and Six Sigma Methods
- Statistical Tests (Mann-Whitney U, t-test, ANOVA, Paired t-test)
- Bias and CV Analysis
- Bland-Altman Plots
- Correlation Analysis (Pearson)
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


class LabQCAnalysis:
    """Class for laboratory quality control analysis"""
    
    def __init__(self, seed=42):
        np.random.seed(seed)
        
        # Clinical reference ranges and QC parameters
        self.parameters = {
            'creatinine': {
                'mean': 1.0,  # mg/dL
                'std': 0.05,
                'tea': 0.15,  # Total Allowable Error (15%)
                'reference_range': (0.6, 1.2),
                'unit': 'mg/dL'
            },
            'urea': {
                'mean': 25.0,  # mg/dL
                'std': 1.5,
                'tea': 0.09,  # Total Allowable Error (9%)
                'reference_range': (15, 40),
                'unit': 'mg/dL'
            }
        }
    
    def generate_qc_data(self, analyte, n_days=30, measurements_per_day=3):
        """Generate mock QC data for quality control charts"""
        params = self.parameters[analyte]
        n_total = n_days * measurements_per_day
        
        # Generate dates
        start_date = datetime.now() - timedelta(days=n_days)
        dates = [start_date + timedelta(days=i//measurements_per_day) for i in range(n_total)]
        
        # Generate QC values with occasional shifts and outliers
        values = np.random.normal(params['mean'], params['std'], n_total)
        
        # Add some controlled variations
        # Shift in middle period (simulate reagent change)
        shift_start, shift_end = n_total//3, 2*n_total//3
        values[shift_start:shift_end] += params['std'] * 0.5
        
        # Add 2-3 outliers
        outlier_indices = np.random.choice(range(n_total), size=3, replace=False)
        values[outlier_indices] += np.random.choice([-1, 1], 3) * params['std'] * 3
        
        df = pd.DataFrame({
            'date': dates,
            'run_number': range(1, n_total + 1),
            'value': values,
            'analyte': analyte
        })
        
        return df
    
    def generate_patient_data(self, analyte, n_samples=100, method='A'):
        """Generate mock patient data for method comparison"""
        params = self.parameters[analyte]
        
        # Generate values across the clinical range
        min_val, max_val = params['reference_range']
        true_values = np.random.uniform(min_val, max_val, n_samples)
        
        # Add measurement error
        if method == 'A':
            measured = true_values + np.random.normal(0, params['std'], n_samples)
        else:  # Method B with slight bias
            bias = 0.05 * params['mean']
            measured = true_values + bias + np.random.normal(0, params['std'] * 1.2, n_samples)
        
        return measured
    
    def levey_jennings_chart(self, qc_data, analyte):
        """Create Levey-Jennings chart"""
        params = self.parameters[analyte]
        mean = params['mean']
        std = params['std']
        
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # Plot data points
        ax.plot(qc_data['run_number'], qc_data['value'], 
                marker='o', linestyle='-', markersize=6, linewidth=1.5, 
                color='steelblue', label='QC Measurements')
        
        # Control limits
        ax.axhline(y=mean, color='green', linestyle='-', linewidth=2, label='Mean')
        ax.axhline(y=mean + std, color='yellow', linestyle='--', linewidth=1.5, label='+1 SD')
        ax.axhline(y=mean - std, color='yellow', linestyle='--', linewidth=1.5)
        ax.axhline(y=mean + 2*std, color='orange', linestyle='--', linewidth=1.5, label='+2 SD')
        ax.axhline(y=mean - 2*std, color='orange', linestyle='--', linewidth=1.5)
        ax.axhline(y=mean + 3*std, color='red', linestyle='--', linewidth=2, label='+3 SD')
        ax.axhline(y=mean - 3*std, color='red', linestyle='--', linewidth=2)
        
        # Highlight out-of-control points
        outliers = qc_data[np.abs(qc_data['value'] - mean) > 3*std]
        if len(outliers) > 0:
            ax.scatter(outliers['run_number'], outliers['value'], 
                      color='red', s=100, marker='x', linewidths=3, 
                      label='Out of Control', zorder=5)
        
        ax.set_xlabel('Run Number', fontsize=12, fontweight='bold')
        ax.set_ylabel(f'{analyte.capitalize()} ({params["unit"]})', fontsize=12, fontweight='bold')
        ax.set_title(f'Levey-Jennings Chart - {analyte.capitalize()}', 
                    fontsize=14, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def apply_westgard_rules(self, qc_data, analyte):
        """Apply Westgard rules to QC data"""
        params = self.parameters[analyte]
        mean = params['mean']
        std = params['std']
        
        values = qc_data['value'].values
        violations = []
        
        for i in range(len(values)):
            z_score = (values[i] - mean) / std
            
            # Rule 1-3s: One control exceeds mean ± 3SD
            if abs(z_score) > 3:
                violations.append({
                    'run': i+1,
                    'rule': '1-3s',
                    'description': 'One control exceeds ±3 SD',
                    'action': 'REJECT - Random error'
                })
            
            # Rule 2-2s: Two consecutive controls exceed mean ± 2SD on same side
            if i > 0:
                z_prev = (values[i-1] - mean) / std
                if abs(z_score) > 2 and abs(z_prev) > 2:
                    if np.sign(z_score) == np.sign(z_prev):
                        violations.append({
                            'run': i+1,
                            'rule': '2-2s',
                            'description': 'Two consecutive controls exceed ±2 SD (same side)',
                            'action': 'REJECT - Systematic error'
                        })
            
            # Rule R-4s: Range between controls exceeds 4SD
            if i > 0:
                range_val = abs(values[i] - values[i-1])
                if range_val > 4 * std:
                    violations.append({
                        'run': i+1,
                        'rule': 'R-4s',
                        'description': 'Range exceeds 4 SD',
                        'action': 'REJECT - Random error'
                    })
            
            # Rule 4-1s: Four consecutive controls exceed mean ± 1SD on same side
            if i >= 3:
                last_4_z = [(values[j] - mean) / std for j in range(i-3, i+1)]
                if all(z > 1 for z in last_4_z) or all(z < -1 for z in last_4_z):
                    violations.append({
                        'run': i+1,
                        'rule': '4-1s',
                        'description': 'Four consecutive controls exceed ±1 SD (same side)',
                        'action': 'WARNING - Systematic error trend'
                    })
            
            # Rule 10-x: 10 consecutive controls on same side of mean
            if i >= 9:
                last_10 = values[i-9:i+1]
                if all(val > mean for val in last_10) or all(val < mean for val in last_10):
                    violations.append({
                        'run': i+1,
                        'rule': '10-x',
                        'description': '10 consecutive controls on same side of mean',
                        'action': 'REJECT - Systematic error'
                    })
        
        return pd.DataFrame(violations)
    
    def calculate_sigma_metrics(self, analyte, bias_pct, cv_pct):
        """Calculate Sigma metrics"""
        params = self.parameters[analyte]
        tea_pct = params['tea'] * 100  # Convert to percentage
        
        # Sigma = (TEa - |Bias|) / CV
        sigma = (tea_pct - abs(bias_pct)) / cv_pct
        
        # Quality level interpretation
        if sigma >= 6:
            quality = "World Class (Six Sigma)"
        elif sigma >= 5:
            quality = "Excellent"
        elif sigma >= 4:
            quality = "Good"
        elif sigma >= 3:
            quality = "Marginal"
        else:
            quality = "Poor"
        
        return {
            'sigma': sigma,
            'quality': quality,
            'tea_pct': tea_pct,
            'bias_pct': bias_pct,
            'cv_pct': cv_pct
        }
    
    def plot_sigma_chart(self, analyte, cv_range=(1, 10), bias_range=(-10, 10)):
        """Create Sigma quality chart (Normalized Method Decision Chart)"""
        params = self.parameters[analyte]
        tea_pct = params['tea'] * 100
        
        # Create grid
        cv_vals = np.linspace(cv_range[0], cv_range[1], 100)
        bias_vals = np.linspace(bias_range[0], bias_range[1], 100)
        CV, BIAS = np.meshgrid(cv_vals, bias_vals)
        
        # Calculate Sigma for each point
        SIGMA = (tea_pct - np.abs(BIAS)) / CV
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Contour plot
        levels = [0, 2, 3, 4, 5, 6]
        contour = ax.contourf(CV, BIAS, SIGMA, levels=levels, 
                              cmap='RdYlGn', alpha=0.7)
        
        # Contour lines
        cs = ax.contour(CV, BIAS, SIGMA, levels=levels, 
                       colors='black', linewidths=1.5)
        ax.clabel(cs, inline=True, fontsize=10, fmt='σ=%1.0f')
        
        # Add colorbar
        cbar = plt.colorbar(contour, ax=ax)
        cbar.set_label('Sigma Value', fontsize=12, fontweight='bold')
        
        # Add quality zones text
        ax.text(8.5, 8, 'Poor\n(σ<3)', fontsize=11, ha='center', 
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        ax.text(8.5, 4, 'Marginal\n(σ=3-4)', fontsize=11, ha='center',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        ax.text(4, 0, 'Good (σ=4-5)', fontsize=11, ha='center',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        ax.text(2, 0, 'Excellent\n(σ=5-6)', fontsize=11, ha='center',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        ax.set_xlabel('Coefficient of Variation (CV) %', fontsize=12, fontweight='bold')
        ax.set_ylabel('Bias %', fontsize=12, fontweight='bold')
        ax.set_title(f'Sigma Quality Chart - {analyte.capitalize()} (TEa = {tea_pct}%)', 
                    fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        return fig
    
    def bland_altman_plot(self, method_a, method_b, analyte):
        """Create Bland-Altman plot for method comparison"""
        mean_values = (method_a + method_b) / 2
        differences = method_a - method_b
        
        mean_diff = np.mean(differences)
        std_diff = np.std(differences, ddof=1)
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Scatter plot
        ax.scatter(mean_values, differences, alpha=0.6, s=50, color='steelblue')
        
        # Mean difference line
        ax.axhline(y=mean_diff, color='blue', linestyle='-', linewidth=2, 
                  label=f'Mean Difference = {mean_diff:.3f}')
        
        # Limits of agreement (±1.96 SD)
        upper_loa = mean_diff + 1.96 * std_diff
        lower_loa = mean_diff - 1.96 * std_diff
        
        ax.axhline(y=upper_loa, color='red', linestyle='--', linewidth=2, 
                  label=f'Upper LoA = {upper_loa:.3f}')
        ax.axhline(y=lower_loa, color='red', linestyle='--', linewidth=2, 
                  label=f'Lower LoA = {lower_loa:.3f}')
        
        # 95% confidence intervals for LoA
        n = len(differences)
        se_loa = std_diff * np.sqrt(3 / n)
        
        # Create x-range for fill_between
        x_range = np.array([mean_values.min(), mean_values.max()])
        
        # Upper LoA confidence interval
        ax.fill_between(x_range, 
                        upper_loa - 1.96*se_loa, upper_loa + 1.96*se_loa,
                        alpha=0.2, color='red')
        # Lower LoA confidence interval
        ax.fill_between(x_range,
                        lower_loa - 1.96*se_loa, lower_loa + 1.96*se_loa,
                        alpha=0.2, color='red')
        
        params = self.parameters[analyte]
        ax.set_xlabel(f'Mean of Two Methods ({params["unit"]})', 
                     fontsize=12, fontweight='bold')
        ax.set_ylabel(f'Difference (Method A - Method B) ({params["unit"]})', 
                     fontsize=12, fontweight='bold')
        ax.set_title(f'Bland-Altman Plot - {analyte.capitalize()}', 
                    fontsize=14, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Return statistics
        stats_dict = {
            'mean_difference': mean_diff,
            'std_difference': std_diff,
            'upper_loa': upper_loa,
            'lower_loa': lower_loa,
            'within_loa': np.sum((differences >= lower_loa) & (differences <= upper_loa)) / n * 100
        }
        
        return fig, stats_dict
    
    def correlation_analysis(self, method_a, method_b, analyte):
        """Perform correlation analysis between two methods"""
        # Pearson correlation
        pearson_r, pearson_p = stats.pearsonr(method_a, method_b)
        
        # Spearman correlation
        spearman_r, spearman_p = stats.spearmanr(method_a, method_b)
        
        # Linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(method_a, method_b)
        
        # Create plot
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Scatter plot
        ax.scatter(method_a, method_b, alpha=0.6, s=50, color='steelblue', 
                  label='Data Points')
        
        # Regression line
        x_line = np.array([method_a.min(), method_a.max()])
        y_line = slope * x_line + intercept
        ax.plot(x_line, y_line, 'r-', linewidth=2, 
               label=f'y = {slope:.3f}x + {intercept:.3f}')
        
        # Identity line
        ax.plot(x_line, x_line, 'k--', linewidth=2, alpha=0.5, label='y = x (Identity)')
        
        params = self.parameters[analyte]
        ax.set_xlabel(f'Method A ({params["unit"]})', fontsize=12, fontweight='bold')
        ax.set_ylabel(f'Method B ({params["unit"]})', fontsize=12, fontweight='bold')
        ax.set_title(f'Method Comparison - {analyte.capitalize()}\n' + 
                    f'Pearson r = {pearson_r:.4f} (p = {pearson_p:.4e})', 
                    fontsize=14, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # Add text box with statistics
        textstr = f'Pearson r = {pearson_r:.4f}\n'
        textstr += f'Spearman ρ = {spearman_r:.4f}\n'
        textstr += f'R² = {r_value**2:.4f}\n'
        textstr += f'Slope = {slope:.4f}\n'
        textstr += f'Intercept = {intercept:.4f}'
        
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=10,
               verticalalignment='top', bbox=props)
        
        plt.tight_layout()
        
        return fig, {
            'pearson_r': pearson_r,
            'pearson_p': pearson_p,
            'spearman_r': spearman_r,
            'spearman_p': spearman_p,
            'slope': slope,
            'intercept': intercept,
            'r_squared': r_value**2
        }
    
    def statistical_tests(self, method_a, method_b, groups=None, all_data=None):
        """Perform various statistical tests
        
        Parameters:
        -----------
        method_a : array-like
            Data from method/group A
        method_b : array-like
            Data from method/group B
        groups : array-like, optional
            Group labels for ANOVA (when comparing 3+ groups)
        all_data : array-like, optional
            Combined data from all groups (required when groups is provided for ANOVA)
        """
        results = {}
        
        # Paired t-test (for same samples measured by two methods)
        t_stat, t_p = stats.ttest_rel(method_a, method_b)
        results['paired_t_test'] = {
            't_statistic': t_stat,
            'p_value': t_p,
            'significant': t_p < 0.05
        }
        
        # Independent t-test
        t_stat_ind, t_p_ind = stats.ttest_ind(method_a, method_b)
        results['independent_t_test'] = {
            't_statistic': t_stat_ind,
            'p_value': t_p_ind,
            'significant': t_p_ind < 0.05
        }
        
        # Mann-Whitney U test (non-parametric alternative to t-test)
        u_stat, u_p = stats.mannwhitneyu(method_a, method_b, alternative='two-sided')
        results['mann_whitney_u'] = {
            'u_statistic': u_stat,
            'p_value': u_p,
            'significant': u_p < 0.05
        }
        
        # If groups are provided, perform ANOVA
        if groups is not None and all_data is not None:
            unique_groups = np.unique(groups)
            group_data = [all_data[groups == g] for g in unique_groups]
            f_stat, anova_p = stats.f_oneway(*group_data)
            results['anova'] = {
                'f_statistic': f_stat,
                'p_value': anova_p,
                'significant': anova_p < 0.05
            }
        
        return results
    
    def calculate_bias_cv(self, data, true_mean=None):
        """Calculate Bias and Coefficient of Variation"""
        mean_val = np.mean(data)
        std_val = np.std(data, ddof=1)
        cv = (std_val / mean_val) * 100  # CV in percentage
        
        if true_mean is not None:
            bias = mean_val - true_mean
            bias_pct = (bias / true_mean) * 100
        else:
            bias = 0
            bias_pct = 0
        
        return {
            'mean': mean_val,
            'std': std_val,
            'cv': cv,
            'bias': bias,
            'bias_pct': bias_pct,
            'n': len(data)
        }


def main():
    """Main function to run all analyses"""
    
    print("="*80)
    print("LABORATORY QUALITY CONTROL AND STATISTICAL ANALYSIS")
    print("For Creatinine and Urea")
    print("="*80)
    print()
    
    # Initialize QC Analysis
    qc = LabQCAnalysis(seed=42)
    
    # ========================================================================
    # 1. LEVEY-JENNINGS CHARTS AND WESTGARD RULES
    # ========================================================================
    print("\n" + "="*80)
    print("1. LEVEY-JENNINGS CHARTS AND WESTGARD RULES")
    print("="*80)
    
    for analyte in ['creatinine', 'urea']:
        print(f"\n--- {analyte.upper()} ---")
        
        # Generate QC data
        qc_data = qc.generate_qc_data(analyte, n_days=30, measurements_per_day=3)
        
        # Create Levey-Jennings chart
        fig = qc.levey_jennings_chart(qc_data, analyte)
        plt.savefig(f'results/levey_jennings_{analyte}.png', dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Levey-Jennings chart saved: results/levey_jennings_{analyte}.png")
        
        # Apply Westgard rules
        violations = qc.apply_westgard_rules(qc_data, analyte)
        if len(violations) > 0:
            print(f"\n⚠ Westgard Rule Violations ({len(violations)} found):")
            print(violations.to_string(index=False))
            violations.to_csv(f'results/westgard_violations_{analyte}.csv', index=False)
        else:
            print("✓ No Westgard rule violations detected - QC is in control")
        
        # Calculate QC statistics
        qc_stats = qc.calculate_bias_cv(qc_data['value'].values, 
                                        qc.parameters[analyte]['mean'])
        print(f"\nQC Statistics:")
        print(f"  Mean: {qc_stats['mean']:.4f} {qc.parameters[analyte]['unit']}")
        print(f"  SD: {qc_stats['std']:.4f}")
        print(f"  CV: {qc_stats['cv']:.2f}%")
        print(f"  Bias: {qc_stats['bias_pct']:.2f}%")
    
    # ========================================================================
    # 2. SIGMA METRICS AND TEa ANALYSIS
    # ========================================================================
    print("\n\n" + "="*80)
    print("2. SIGMA METRICS AND TOTAL ALLOWABLE ERROR (TEa) ANALYSIS")
    print("="*80)
    
    for analyte in ['creatinine', 'urea']:
        print(f"\n--- {analyte.upper()} ---")
        
        # Use QC statistics from above
        qc_data = qc.generate_qc_data(analyte, n_days=30, measurements_per_day=3)
        qc_stats = qc.calculate_bias_cv(qc_data['value'].values,
                                        qc.parameters[analyte]['mean'])
        
        # Calculate Sigma
        sigma_results = qc.calculate_sigma_metrics(analyte, 
                                                    qc_stats['bias_pct'], 
                                                    qc_stats['cv'])
        
        print(f"  TEa: {sigma_results['tea_pct']:.1f}%")
        print(f"  Bias: {sigma_results['bias_pct']:.2f}%")
        print(f"  CV: {sigma_results['cv_pct']:.2f}%")
        print(f"  Sigma: {sigma_results['sigma']:.2f}")
        print(f"  Quality Level: {sigma_results['quality']}")
        
        # Create Sigma chart
        fig = qc.plot_sigma_chart(analyte)
        plt.savefig(f'results/sigma_chart_{analyte}.png', dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Sigma chart saved: results/sigma_chart_{analyte}.png")

    # ========================================================================
    # 3. METHOD COMPARISON - BLAND-ALTMAN AND CORRELATION
    # ========================================================================
    print("\n\n" + "="*80)
    print("3. METHOD COMPARISON ANALYSIS")
    print("="*80)
    
    for analyte in ['creatinine', 'urea']:
        print(f"\n--- {analyte.upper()} ---")
        
        # Generate patient data for two methods
        n_samples = 100
        method_a_data = qc.generate_patient_data(analyte, n_samples, method='A')
        method_b_data = qc.generate_patient_data(analyte, n_samples, method='B')
        
        # Bland-Altman plot
        fig_ba, ba_stats = qc.bland_altman_plot(method_a_data, method_b_data, analyte)
        plt.savefig(f'results/bland_altman_{analyte}.png', dpi=300, bbox_inches='tight')
        plt.close()
        print(f"\n✓ Bland-Altman plot saved: results/bland_altman_{analyte}.png")
        print(f"  Mean Difference: {ba_stats['mean_difference']:.4f}")
        print(f"  Limits of Agreement: [{ba_stats['lower_loa']:.4f}, {ba_stats['upper_loa']:.4f}]")
        print(f"  % Within LoA: {ba_stats['within_loa']:.1f}%")
        
        # Correlation analysis
        fig_corr, corr_stats = qc.correlation_analysis(method_a_data, method_b_data, analyte)
        plt.savefig(f'results/correlation_{analyte}.png', dpi=300, bbox_inches='tight')
        plt.close()
        print(f"\n✓ Correlation plot saved: results/correlation_{analyte}.png")
        print(f"  Pearson r: {corr_stats['pearson_r']:.4f} (p = {corr_stats['pearson_p']:.4e})")
        print(f"  Spearman ρ: {corr_stats['spearman_r']:.4f}")
        print(f"  R²: {corr_stats['r_squared']:.4f}")
        print(f"  Regression: y = {corr_stats['slope']:.4f}x + {corr_stats['intercept']:.4f}")
        
        # Statistical tests
        print(f"\n  Statistical Tests:")
        test_results = qc.statistical_tests(method_a_data, method_b_data)
        
        print(f"    Paired t-test:")
        print(f"      t = {test_results['paired_t_test']['t_statistic']:.4f}")
        print(f"      p = {test_results['paired_t_test']['p_value']:.4e}")
        print(f"      Significant: {test_results['paired_t_test']['significant']}")
        
        print(f"    Mann-Whitney U test:")
        print(f"      U = {test_results['mann_whitney_u']['u_statistic']:.4f}")
        print(f"      p = {test_results['mann_whitney_u']['p_value']:.4e}")
        print(f"      Significant: {test_results['mann_whitney_u']['significant']}")
    
    # ========================================================================
    # 4. ANOVA EXAMPLE (Multiple Methods/Instruments)
    # ========================================================================
    print("\n\n" + "="*80)
    print("4. ANOVA - COMPARISON OF MULTIPLE METHODS/INSTRUMENTS")
    print("="*80)
    
    for analyte in ['creatinine', 'urea']:
        print(f"\n--- {analyte.upper()} ---")
        
        # Simulate 3 different instruments
        n_per_instrument = 50
        instrument_1 = qc.generate_patient_data(analyte, n_per_instrument, method='A')
        instrument_2 = qc.generate_patient_data(analyte, n_per_instrument, method='B')
        
        # Instrument 3 with different characteristics
        params = qc.parameters[analyte]
        instrument_3 = qc.generate_patient_data(analyte, n_per_instrument, method='A')
        instrument_3 += np.random.normal(0.02 * params['mean'], params['std'], n_per_instrument)
        
        # Combine data
        all_data = np.concatenate([instrument_1, instrument_2, instrument_3])
        groups = np.array(['Instrument_1']*n_per_instrument + 
                         ['Instrument_2']*n_per_instrument + 
                         ['Instrument_3']*n_per_instrument)
        
        # Perform ANOVA
        test_results = qc.statistical_tests(instrument_1, instrument_2, 
                                            groups=groups, all_data=all_data)
        
        print(f"  ANOVA Results:")
        print(f"    F-statistic: {test_results['anova']['f_statistic']:.4f}")
        print(f"    p-value: {test_results['anova']['p_value']:.4e}")
        print(f"    Significant: {test_results['anova']['significant']}")
        
        # Summary statistics for each group
        print(f"\n  Group Statistics:")
        for i, inst_data in enumerate([instrument_1, instrument_2, instrument_3], 1):
            stats_i = qc.calculate_bias_cv(inst_data)
            print(f"    Instrument {i}:")
            print(f"      Mean: {stats_i['mean']:.4f}")
            print(f"      SD: {stats_i['std']:.4f}")
            print(f"      CV: {stats_i['cv']:.2f}%")
        
        # Visualization
        fig, ax = plt.subplots(figsize=(10, 6))
        
        data_list = [instrument_1, instrument_2, instrument_3]
        positions = [1, 2, 3]
        bp = ax.boxplot(data_list, positions=positions, widths=0.6,
                        patch_artist=True, notch=True)
        
        # Color boxes
        colors = ['lightblue', 'lightgreen', 'lightcoral']
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
        
        ax.set_xticklabels(['Instrument 1', 'Instrument 2', 'Instrument 3'])
        ax.set_ylabel(f'{analyte.capitalize()} ({params["unit"]})', 
                     fontsize=12, fontweight='bold')
        ax.set_title(f'ANOVA - Multiple Instrument Comparison\n{analyte.capitalize()}', 
                    fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(f'results/anova_{analyte}.png', dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ ANOVA plot saved: results/anova_{analyte}.png")

    # ========================================================================
    # 5. COMPREHENSIVE SUMMARY REPORT
    # ========================================================================
    print("\n\n" + "="*80)
    print("5. SUMMARY REPORT")
    print("="*80)
    
    summary_data = []
    
    for analyte in ['creatinine', 'urea']:
        qc_data = qc.generate_qc_data(analyte, n_days=30, measurements_per_day=3)
        qc_stats = qc.calculate_bias_cv(qc_data['value'].values,
                                        qc.parameters[analyte]['mean'])
        sigma_results = qc.calculate_sigma_metrics(analyte,
                                                    qc_stats['bias_pct'],
                                                    qc_stats['cv'])
        
        summary_data.append({
            'Analyte': analyte.capitalize(),
            'Mean': f"{qc_stats['mean']:.4f}",
            'SD': f"{qc_stats['std']:.4f}",
            'CV (%)': f"{qc_stats['cv']:.2f}",
            'Bias (%)': f"{qc_stats['bias_pct']:.2f}",
            'TEa (%)': f"{sigma_results['tea_pct']:.1f}",
            'Sigma': f"{sigma_results['sigma']:.2f}",
            'Quality': sigma_results['quality']
        })
    
    summary_df = pd.DataFrame(summary_data)
    print("\n" + summary_df.to_string(index=False))
    summary_df.to_csv('results/qc_summary_report.csv', index=False)
    print(f"\n✓ Summary report saved: results/qc_summary_report.csv")

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE!")
    print("="*80)
    print("\nGenerated Files:")
    print("  - Levey-Jennings charts (2 files)")
    print("  - Sigma quality charts (2 files)")
    print("  - Bland-Altman plots (2 files)")
    print("  - Correlation plots (2 files)")
    print("  - ANOVA plots (2 files)")
    print("  - Westgard violations reports (CSV files)")
    print("  - QC summary report (CSV)")
    print("\nTotal: ~15 output files")
    print("="*80)


if __name__ == "__main__":
    main()
