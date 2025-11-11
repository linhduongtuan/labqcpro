"""
Quick Reference: All QC Methods in One Place
Copy and paste these snippets to use individual components
"""

from lab_qc_analysis import LabQCAnalysis
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ============================================================================
# INITIALIZE
# ============================================================================
qc = LabQCAnalysis(seed=42)

# ============================================================================
# 1. LEVEY-JENNINGS CHART
# ============================================================================
print("1. LEVEY-JENNINGS CHART")
qc_data = qc.generate_qc_data('creatinine', n_days=30, measurements_per_day=3)
fig = qc.levey_jennings_chart(qc_data, 'creatinine')
plt.savefig('results/output_levey_jennings.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: results/output_levey_jennings.png\n")

# ============================================================================
# 2. WESTGARD RULES
# ============================================================================
print("2. WESTGARD RULES")
violations = qc.apply_westgard_rules(qc_data, 'creatinine')
if len(violations) > 0:
    print(f"Found {len(violations)} violations:")
    print(violations[['run', 'rule', 'action']].to_string(index=False))
else:
    print("✓ No violations - QC in control")
print()

# ============================================================================
# 3. SIGMA METRICS
# ============================================================================
print("3. SIGMA METRICS")
# Calculate from QC data
stats = qc.calculate_bias_cv(qc_data['value'].values, 
                              qc.parameters['creatinine']['mean'])
sigma_results = qc.calculate_sigma_metrics('creatinine', 
                                            stats['bias_pct'], 
                                            stats['cv'])
print(f"TEa: {sigma_results['tea_pct']:.1f}%")
print(f"Bias: {sigma_results['bias_pct']:.2f}%")
print(f"CV: {sigma_results['cv_pct']:.2f}%")
print(f"Sigma: {sigma_results['sigma']:.2f}")
print(f"Quality: {sigma_results['quality']}")

# Create sigma chart
fig = qc.plot_sigma_chart('creatinine')
plt.savefig('results/output_sigma_chart.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: results/output_sigma_chart.png\n")

# ============================================================================
# 4. BIAS CALCULATION
# ============================================================================
print("4. BIAS AND CV")
target = qc.parameters['creatinine']['mean']
bias_stats = qc.calculate_bias_cv(qc_data['value'].values, target)
print(f"Target: {target:.4f}")
print(f"Observed: {bias_stats['mean']:.4f}")
print(f"Bias: {bias_stats['bias']:.4f} ({bias_stats['bias_pct']:.2f}%)")
print(f"SD: {bias_stats['std']:.4f}")
print(f"CV: {bias_stats['cv']:.2f}%")
print()

# ============================================================================
# 5. BLAND-ALTMAN PLOT
# ============================================================================
print("5. BLAND-ALTMAN PLOT")
method_a = qc.generate_patient_data('creatinine', 100, 'A')
method_b = qc.generate_patient_data('creatinine', 100, 'B')
fig, ba_stats = qc.bland_altman_plot(method_a, method_b, 'creatinine')
print(f"Mean Difference: {ba_stats['mean_difference']:.4f}")
print(f"Lower LoA: {ba_stats['lower_loa']:.4f}")
print(f"Upper LoA: {ba_stats['upper_loa']:.4f}")
print(f"Within LoA: {ba_stats['within_loa']:.1f}%")
plt.savefig('results/output_bland_altman.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: results/output_bland_altman.png\n")

# ============================================================================
# 6. CORRELATION (PEARSON)
# ============================================================================
print("6. PEARSON CORRELATION")
fig, corr_stats = qc.correlation_analysis(method_a, method_b, 'creatinine')
print(f"Pearson r: {corr_stats['pearson_r']:.4f}")
print(f"p-value: {corr_stats['pearson_p']:.2e}")
print(f"R²: {corr_stats['r_squared']:.4f}")
print(f"Slope: {corr_stats['slope']:.4f}")
print(f"Intercept: {corr_stats['intercept']:.4f}")
plt.savefig('results/output_correlation.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: results/output_correlation.png\n")

# ============================================================================
# 7. PAIRED T-TEST
# ============================================================================
print("7. PAIRED T-TEST")
test_results = qc.statistical_tests(method_a, method_b)
print(f"t-statistic: {test_results['paired_t_test']['t_statistic']:.4f}")
print(f"p-value: {test_results['paired_t_test']['p_value']:.4e}")
print(f"Significant (α=0.05): {test_results['paired_t_test']['significant']}")
print()

# ============================================================================
# 8. MANN-WHITNEY U TEST
# ============================================================================
print("8. MANN-WHITNEY U TEST")
print(f"U-statistic: {test_results['mann_whitney_u']['u_statistic']:.4f}")
print(f"p-value: {test_results['mann_whitney_u']['p_value']:.4e}")
print(f"Significant (α=0.05): {test_results['mann_whitney_u']['significant']}")
print()

# ============================================================================
# 9. ANOVA (3+ Groups)
# ============================================================================
print("9. ANOVA (Multiple Instruments)")
n = 50
inst1 = qc.generate_patient_data('creatinine', n, 'A')
inst2 = qc.generate_patient_data('creatinine', n, 'B')
inst3 = qc.generate_patient_data('creatinine', n, 'A')
inst3 += np.random.normal(0.02, 0.01, n)

# Combine all data
all_data = np.concatenate([inst1, inst2, inst3])
groups = np.array(['Inst1']*n + ['Inst2']*n + ['Inst3']*n)
anova_results = qc.statistical_tests(inst1, inst2, groups=groups, all_data=all_data)
print(f"F-statistic: {anova_results['anova']['f_statistic']:.4f}")
print(f"p-value: {anova_results['anova']['p_value']:.4e}")
print(f"Significant (α=0.05): {anova_results['anova']['significant']}")

# Show means
for i, data in enumerate([inst1, inst2, inst3], 1):
    print(f"  Instrument {i}: Mean = {np.mean(data):.4f}")
print()

# ============================================================================
# SUMMARY TABLE
# ============================================================================
print("="*80)
print("SUMMARY REPORT")
print("="*80)

summary_data = []
for analyte in ['creatinine', 'urea']:
    params = qc.parameters[analyte]
    qc_data = qc.generate_qc_data(analyte, n_days=30, measurements_per_day=3)
    stats = qc.calculate_bias_cv(qc_data['value'].values, params['mean'])
    sigma = qc.calculate_sigma_metrics(analyte, stats['bias_pct'], stats['cv'])
    
    summary_data.append({
        'Analyte': analyte.capitalize(),
        'Target': f"{params['mean']:.2f} {params['unit']}",
        'CV': f"{stats['cv']:.2f}%",
        'Bias': f"{stats['bias_pct']:.2f}%",
        'Sigma': f"{sigma['sigma']:.2f}",
        'Quality': sigma['quality']
    })

summary_df = pd.DataFrame(summary_data)
print(summary_df.to_string(index=False))
print("="*80)
print("✓ All analyses complete!")
print("="*80)
