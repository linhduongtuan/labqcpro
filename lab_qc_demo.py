"""
Interactive Demo: Laboratory Quality Control Analysis
Run specific analyses for Creatinine and Urea
"""

from lab_qc_analysis import LabQCAnalysis
import matplotlib.pyplot as plt
import numpy as np

def demo_levey_jennings():
    """Demonstrate Levey-Jennings Charts"""
    print("\n" + "="*80)
    print("DEMO: LEVEY-JENNINGS CHART")
    print("="*80)
    
    qc = LabQCAnalysis(seed=42)
    
    # Generate QC data for creatinine
    qc_data = qc.generate_qc_data('creatinine', n_days=30, measurements_per_day=3)
    
    # Create and display chart
    fig = qc.levey_jennings_chart(qc_data, 'creatinine')
    plt.savefig('results/demo_levey_jennings.png', dpi=300, bbox_inches='tight')
    print("✓ Chart saved: results/demo_levey_jennings.png")
    plt.show()

def demo_westgard_rules():
    """Demonstrate Westgard Rules Application"""
    print("\n" + "="*80)
    print("DEMO: WESTGARD RULES")
    print("="*80)
    
    qc = LabQCAnalysis(seed=42)
    qc_data = qc.generate_qc_data('urea', n_days=30, measurements_per_day=3)
    
    violations = qc.apply_westgard_rules(qc_data, 'urea')
    
    if len(violations) > 0:
        print(f"\n⚠ Found {len(violations)} Westgard rule violations:")
        print(violations.to_string(index=False))
    else:
        print("✓ No violations - QC is in control")

def demo_sigma_metrics():
    """Demonstrate Sigma Metrics Calculation"""
    print("\n" + "="*80)
    print("DEMO: SIGMA METRICS")
    print("="*80)
    
    qc = LabQCAnalysis(seed=42)
    
    # Example: CV = 5%, Bias = 2%
    cv_pct = 5.0
    bias_pct = 2.0
    
    for analyte in ['creatinine', 'urea']:
        sigma_results = qc.calculate_sigma_metrics(analyte, bias_pct, cv_pct)
        
        print(f"\n{analyte.upper()}:")
        print(f"  TEa: {sigma_results['tea_pct']:.1f}%")
        print(f"  Bias: {sigma_results['bias_pct']:.2f}%")
        print(f"  CV: {sigma_results['cv_pct']:.2f}%")
        print(f"  Sigma: {sigma_results['sigma']:.2f}")
        print(f"  Quality: {sigma_results['quality']}")
    
    # Create sigma chart
    fig = qc.plot_sigma_chart('creatinine')
    plt.savefig('results/demo_sigma_chart.png', dpi=300, bbox_inches='tight')
    print("\n✓ Sigma chart saved: results/demo_sigma_chart.png")
    plt.show()

def demo_bland_altman():
    """Demonstrate Bland-Altman Plot"""
    print("\n" + "="*80)
    print("DEMO: BLAND-ALTMAN PLOT")
    print("="*80)
    
    qc = LabQCAnalysis(seed=42)
    
    # Generate data from two methods
    method_a = qc.generate_patient_data('creatinine', n_samples=100, method='A')
    method_b = qc.generate_patient_data('creatinine', n_samples=100, method='B')
    
    fig, stats = qc.bland_altman_plot(method_a, method_b, 'creatinine')
    
    print(f"\nBland-Altman Statistics:")
    print(f"  Mean Difference: {stats['mean_difference']:.4f}")
    print(f"  Limits of Agreement: [{stats['lower_loa']:.4f}, {stats['upper_loa']:.4f}]")
    print(f"  % Within LoA: {stats['within_loa']:.1f}%")

    plt.savefig('results/demo_bland_altman.png', dpi=300, bbox_inches='tight')
    print("\n✓ Plot saved: results/demo_bland_altman.png")
    plt.show()

def demo_correlation():
    """Demonstrate Pearson Correlation"""
    print("\n" + "="*80)
    print("DEMO: CORRELATION ANALYSIS")
    print("="*80)
    
    qc = LabQCAnalysis(seed=42)
    
    method_a = qc.generate_patient_data('urea', n_samples=100, method='A')
    method_b = qc.generate_patient_data('urea', n_samples=100, method='B')
    
    fig, corr_stats = qc.correlation_analysis(method_a, method_b, 'urea')
    
    print(f"\nCorrelation Statistics:")
    print(f"  Pearson r: {corr_stats['pearson_r']:.4f} (p = {corr_stats['pearson_p']:.2e})")
    print(f"  Spearman ρ: {corr_stats['spearman_r']:.4f}")
    print(f"  R²: {corr_stats['r_squared']:.4f}")
    print(f"  Regression: y = {corr_stats['slope']:.4f}x + {corr_stats['intercept']:.4f}")

    plt.savefig('results/demo_correlation.png', dpi=300, bbox_inches='tight')
    print("\n✓ Plot saved: results/demo_correlation.png")
    plt.show()

def demo_statistical_tests():
    """Demonstrate Statistical Tests"""
    print("\n" + "="*80)
    print("DEMO: STATISTICAL TESTS")
    print("="*80)
    
    qc = LabQCAnalysis(seed=42)
    
    method_a = qc.generate_patient_data('creatinine', n_samples=100, method='A')
    method_b = qc.generate_patient_data('creatinine', n_samples=100, method='B')
    
    test_results = qc.statistical_tests(method_a, method_b)
    
    print("\nPaired t-test:")
    print(f"  t-statistic: {test_results['paired_t_test']['t_statistic']:.4f}")
    print(f"  p-value: {test_results['paired_t_test']['p_value']:.4e}")
    print(f"  Significant (α=0.05): {test_results['paired_t_test']['significant']}")
    
    print("\nMann-Whitney U test:")
    print(f"  U-statistic: {test_results['mann_whitney_u']['u_statistic']:.4f}")
    print(f"  p-value: {test_results['mann_whitney_u']['p_value']:.4e}")
    print(f"  Significant (α=0.05): {test_results['mann_whitney_u']['significant']}")

def demo_anova():
    """Demonstrate ANOVA"""
    print("\n" + "="*80)
    print("DEMO: ANOVA (Multiple Instruments)")
    print("="*80)
    
    qc = LabQCAnalysis(seed=42)
    
    # Simulate 3 instruments
    n = 50
    inst1 = qc.generate_patient_data('creatinine', n_samples=n, method='A')
    inst2 = qc.generate_patient_data('creatinine', n_samples=n, method='B')
    inst3 = qc.generate_patient_data('creatinine', n_samples=n, method='A')
    inst3 += np.random.normal(0.02, 0.01, n)
    
    # Combine all data
    all_data = np.concatenate([inst1, inst2, inst3])
    groups = np.array(['Instrument_1']*n + ['Instrument_2']*n + ['Instrument_3']*n)
    
    test_results = qc.statistical_tests(inst1, inst2, groups=groups, all_data=all_data)
    
    print("\nANOVA Results:")
    print(f"  F-statistic: {test_results['anova']['f_statistic']:.4f}")
    print(f"  p-value: {test_results['anova']['p_value']:.4e}")
    print(f"  Significant (α=0.05): {test_results['anova']['significant']}")
    
    # Show group statistics
    print("\nGroup Statistics:")
    for i, inst_data in enumerate([inst1, inst2, inst3], 1):
        stats = qc.calculate_bias_cv(inst_data)
        print(f"  Instrument {i}: Mean={stats['mean']:.4f}, SD={stats['std']:.4f}, CV={stats['cv']:.2f}%")

def demo_bias_cv():
    """Demonstrate Bias and CV Calculation"""
    print("\n" + "="*80)
    print("DEMO: BIAS AND COEFFICIENT OF VARIATION")
    print("="*80)
    
    qc = LabQCAnalysis(seed=42)
    qc_data = qc.generate_qc_data('creatinine', n_days=30, measurements_per_day=3)
    
    true_mean = qc.parameters['creatinine']['mean']
    stats = qc.calculate_bias_cv(qc_data['value'].values, true_mean)
    
    print(f"\nCreatinine QC Statistics:")
    print(f"  Target Mean: {true_mean:.4f} mg/dL")
    print(f"  Observed Mean: {stats['mean']:.4f} mg/dL")
    print(f"  Standard Deviation: {stats['std']:.4f}")
    print(f"  CV: {stats['cv']:.2f}%")
    print(f"  Bias: {stats['bias']:.4f} mg/dL")
    print(f"  Bias %: {stats['bias_pct']:.2f}%")
    print(f"  N: {stats['n']}")


def demo_advanced_fault_detection():
    """Demonstrate Advanced Fault Detection"""
    print("\n" + "="*80)
    print("DEMO: ADVANCED FAULT DETECTION")
    print("="*80)
    
    from advanced_fault_detection import AdvancedFaultDetector
    
    qc = LabQCAnalysis(seed=42)
    
    # Generate data with injected faults
    values = qc.generate_qc_data('creatinine', n_days=50, measurements_per_day=2)['value'].values
    
    # Inject additional faults for demonstration
    values[30:40] += 0.08  # Systematic shift
    values[25] += 3 * qc.parameters['creatinine']['std']  # Outlier
    
    # Initialize detector
    detector = AdvancedFaultDetector(
        mean=qc.parameters['creatinine']['mean'],
        std=qc.parameters['creatinine']['std'],
        sensitivity='medium'
    )
    
    # Run comprehensive analysis (save CUSUM/EWMA outputs to results/)
    results = detector.comprehensive_analysis(values, save_dir='results')
    
    # Display summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    summary = results['summary']
    print(summary['message'])
    print(f"\nTotal violations: {summary['total_violations']}")
    print(f"  Critical: {summary.get('critical', 0)}")
    print(f"  Warning: {summary.get('warning', 0)}")
    
    if summary['total_violations'] > 0:
        print("\nViolations by method:")
        for method, count in summary['methods'].items():
            print(f"  {method}: {count}")
        
        # Show top 10 violations
        print("\n" + "="*80)
        print("TOP 10 VIOLATIONS")
        print("="*80)
        top_violations = results['all_violations'].head(10)
        print(top_violations[['index', 'method', 'severity', 'description']].to_string(index=False))
    
    # Create visualization
    fig = detector.plot_comprehensive_charts(values, results, 'Creatinine')
    plt.savefig('results/demo_advanced_fault_detection.png', dpi=300, bbox_inches='tight')
    print("\n✓ Chart saved: results/demo_advanced_fault_detection.png")
    plt.show()


def main_menu():
    """Interactive menu for demos"""
    print("\n" + "="*80)
    print("LABORATORY QC ANALYSIS - INTERACTIVE DEMO")
    print("="*80)
    print("\nAvailable Demos:")
    print("1. Levey-Jennings Chart")
    print("2. Westgard Rules")
    print("3. Sigma Metrics & TEa")
    print("4. Bland-Altman Plot")
    print("5. Correlation Analysis (Pearson)")
    print("6. Statistical Tests (t-test, Mann-Whitney U)")
    print("7. ANOVA (Multiple Groups)")
    print("8. Bias and CV Calculation")
    print("9. Advanced Fault Detection (CUSUM, EWMA, Anomaly Detection)")
    print("10. Run ALL demos")
    print("0. Exit")
    print("="*80)
    
    while True:
        choice = input("\nEnter your choice (0-10): ").strip()
        
        if choice == '1':
            demo_levey_jennings()
        elif choice == '2':
            demo_westgard_rules()
        elif choice == '3':
            demo_sigma_metrics()
        elif choice == '4':
            demo_bland_altman()
        elif choice == '5':
            demo_correlation()
        elif choice == '6':
            demo_statistical_tests()
        elif choice == '7':
            demo_anova()
        elif choice == '8':
            demo_bias_cv()
        elif choice == '9':
            demo_advanced_fault_detection()
        elif choice == '10':
            print("\nRunning all demos...")
            demo_levey_jennings()
            demo_westgard_rules()
            demo_sigma_metrics()
            demo_bland_altman()
            demo_correlation()
            demo_statistical_tests()
            demo_anova()
            demo_bias_cv()
            demo_advanced_fault_detection()
            print("\n✓ All demos completed!")
        elif choice == '0':
            print("\nExiting demo. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    # Run specific demo or show menu
    import sys
    
    if len(sys.argv) > 1:
        demo_name = sys.argv[1].lower()
        demos = {
            'levey': demo_levey_jennings,
            'westgard': demo_westgard_rules,
            'sigma': demo_sigma_metrics,
            'bland': demo_bland_altman,
            'correlation': demo_correlation,
            'tests': demo_statistical_tests,
            'anova': demo_anova,
            'bias': demo_bias_cv,
            'advanced': demo_advanced_fault_detection
        }
        
        if demo_name in demos:
            demos[demo_name]()
        elif demo_name == 'all':
            for demo_func in demos.values():
                demo_func()
        else:
            print(f"Unknown demo: {demo_name}")
            print(f"Available: {', '.join(demos.keys())}, all")
    else:
        # Interactive menu
        main_menu()
