# Laboratory Quality Control Analysis for Creatinine and Urea

## 📊 Complete Implementation Guide

This toolkit provides comprehensive quality control and statistical analysis for laboratory data, specifically designed for **Creatinine** and **Urea** measurements.

---

## 🎯 Features Implemented

### 1. **Levey-Jennings Charts**
- **Purpose**: Monitor quality control measurements over time
- **Usage**: Detects shifts, trends, and random errors in QC data
- **Components**:
  - Mean line (target value)
  - ±1, ±2, ±3 SD control limits
  - Out-of-control point detection
  
**Code Example**:
```python
from lab_qc_analysis import LabQCAnalysis

qc = LabQCAnalysis()
qc_data = qc.generate_qc_data('creatinine', n_days=30, measurements_per_day=3)
fig = qc.levey_jennings_chart(qc_data, 'creatinine')
```

### 2. **Westgard Rules**
- **Purpose**: Multi-rule QC system for detecting analytical errors
- **Rules Implemented**:
  - **1-3s**: One control exceeds ±3 SD (Random error)
  - **2-2s**: Two consecutive controls exceed ±2 SD same side (Systematic error)
  - **R-4s**: Range between two controls exceeds 4 SD (Random error)
  - **4-1s**: Four consecutive controls exceed ±1 SD same side (Systematic trend)
  - **10-x**: Ten consecutive controls on same side of mean (Systematic error)

**Code Example**:
```python
violations = qc.apply_westgard_rules(qc_data, 'creatinine')
print(violations)
```

### 3. **Sigma Metrics and Total Allowable Error (TEa)**
- **Purpose**: Assess analytical quality using Six Sigma methodology
- **Formula**: `Sigma = (TEa - |Bias|) / CV`
- **Quality Levels**:
  - σ ≥ 6: World Class (Six Sigma)
  - σ ≥ 5: Excellent
  - σ ≥ 4: Good
  - σ ≥ 3: Marginal
  - σ < 3: Poor

**Parameters**:
- **Creatinine TEa**: 15%
- **Urea TEa**: 9%

**Code Example**:
```python
sigma_results = qc.calculate_sigma_metrics('creatinine', bias_pct=2.0, cv_pct=5.0)
print(f"Sigma: {sigma_results['sigma']:.2f}")
print(f"Quality: {sigma_results['quality']}")
```

### 4. **Bias Calculation**
- **Purpose**: Measure systematic deviation from true/target value
- **Formula**: 
  - Absolute: `Bias = Observed Mean - True Mean`
  - Relative: `Bias% = (Bias / True Mean) × 100`

**Code Example**:
```python
stats = qc.calculate_bias_cv(data, true_mean=1.0)
print(f"Bias: {stats['bias_pct']:.2f}%")
```

### 5. **Coefficient of Variation (CV)**
- **Purpose**: Measure precision/reproducibility
- **Formula**: `CV = (SD / Mean) × 100%`
- **Interpretation**:
  - CV < 5%: Excellent precision
  - CV 5-10%: Good precision
  - CV 10-20%: Acceptable precision
  - CV > 20%: Poor precision

**Code Example**:
```python
stats = qc.calculate_bias_cv(data)
print(f"CV: {stats['cv']:.2f}%")
```

### 6. **Bland-Altman Plot**
- **Purpose**: Assess agreement between two measurement methods
- **Components**:
  - Mean difference (bias between methods)
  - Limits of Agreement (LoA): Mean ± 1.96 SD
  - 95% confidence intervals for LoA
- **Interpretation**: 95% of differences should fall within LoA

**Code Example**:
```python
method_a = qc.generate_patient_data('creatinine', 100, 'A')
method_b = qc.generate_patient_data('creatinine', 100, 'B')
fig, stats = qc.bland_altman_plot(method_a, method_b, 'creatinine')
```

### 7. **Pearson Correlation**
- **Purpose**: Measure linear relationship between two methods
- **Range**: -1 (perfect negative) to +1 (perfect positive)
- **Interpretation**:
  - |r| > 0.9: Excellent correlation
  - |r| 0.7-0.9: Good correlation
  - |r| 0.5-0.7: Moderate correlation
  - |r| < 0.5: Poor correlation

**Code Example**:
```python
fig, corr_stats = qc.correlation_analysis(method_a, method_b, 'urea')
print(f"Pearson r: {corr_stats['pearson_r']:.4f}")
print(f"R²: {corr_stats['r_squared']:.4f}")
```

### 8. **Paired t-test**
- **Purpose**: Compare means of two related samples (same patients, different methods)
- **Null Hypothesis**: No difference between methods (mean difference = 0)
- **Assumptions**: 
  - Paired observations
  - Differences are normally distributed

**Code Example**:
```python
test_results = qc.statistical_tests(method_a, method_b)
print(f"t-statistic: {test_results['paired_t_test']['t_statistic']:.4f}")
print(f"p-value: {test_results['paired_t_test']['p_value']:.4e}")
print(f"Significant: {test_results['paired_t_test']['significant']}")
```

### 9. **Independent t-test**
- **Purpose**: Compare means of two independent groups
- **Null Hypothesis**: No difference between group means
- **Use Case**: Compare different patient groups or batches

### 10. **Mann-Whitney U Test**
- **Purpose**: Non-parametric alternative to t-test
- **Advantages**: 
  - No normality assumption
  - Robust to outliers
  - Works with ordinal data
- **Use Case**: When data is not normally distributed

**Code Example**:
```python
test_results = qc.statistical_tests(method_a, method_b)
print(f"U-statistic: {test_results['mann_whitney_u']['u_statistic']:.4f}")
print(f"p-value: {test_results['mann_whitney_u']['p_value']:.4e}")
```

### 11. **ANOVA (Analysis of Variance)**
- **Purpose**: Compare means of three or more groups
- **Null Hypothesis**: All group means are equal
- **Use Case**: Compare multiple instruments, methods, or laboratories
- **Post-hoc**: If significant, perform pairwise comparisons

**Code Example**:
```python
groups = np.array(['Inst1']*50 + ['Inst2']*50 + ['Inst3']*50)
test_results = qc.statistical_tests(inst1_data, inst2_data, groups=groups)
print(f"F-statistic: {test_results['anova']['f_statistic']:.4f}")
print(f"p-value: {test_results['anova']['p_value']:.4e}")
```

---

## 📁 Generated Output Files

When you run `lab_qc_analysis.py`, it generates:

### Charts (PNG files):
1. `levey_jennings_creatinine.png` - QC chart for creatinine
2. `levey_jennings_urea.png` - QC chart for urea
3. `sigma_chart_creatinine.png` - Sigma quality chart for creatinine
4. `sigma_chart_urea.png` - Sigma quality chart for urea
5. `bland_altman_creatinine.png` - Method comparison for creatinine
6. `bland_altman_urea.png` - Method comparison for urea
7. `correlation_creatinine.png` - Correlation plot for creatinine
8. `correlation_urea.png` - Correlation plot for urea
9. `anova_creatinine.png` - Multi-instrument comparison for creatinine
10. `anova_urea.png` - Multi-instrument comparison for urea

### Data Files (CSV):
1. `westgard_violations_creatinine.csv` - Westgard rule violations
2. `westgard_violations_urea.csv` - Westgard rule violations
3. `qc_summary_report.csv` - Comprehensive summary statistics

---

## 🚀 Quick Start

### Run Full Analysis:
```bash
uv run lab_qc_analysis.py
```

### Run Interactive Demo:
```bash
# Interactive menu
uv run lab_qc_demo.py

# Specific demo
uv run lab_qc_demo.py levey        # Levey-Jennings chart
uv run lab_qc_demo.py westgard     # Westgard rules
uv run lab_qc_demo.py sigma        # Sigma metrics
uv run lab_qc_demo.py bland        # Bland-Altman plot
uv run lab_qc_demo.py correlation  # Correlation analysis
uv run lab_qc_demo.py tests        # Statistical tests
uv run lab_qc_demo.py anova        # ANOVA
uv run lab_qc_demo.py bias         # Bias and CV
uv run lab_qc_demo.py all          # All demos
```

---

## 📊 Clinical Reference Ranges

### Creatinine:
- **Reference Range**: 0.6 - 1.2 mg/dL
- **Target Mean**: 1.0 mg/dL
- **Target SD**: 0.05 mg/dL
- **TEa**: 15%

### Urea:
- **Reference Range**: 15 - 40 mg/dL
- **Target Mean**: 25.0 mg/dL
- **Target SD**: 1.5 mg/dL
- **TEa**: 9%

---

## 🔬 Real-time Data Simulation

The toolkit generates realistic mocked data with:
- **Normal distribution** around target values
- **Controlled shifts** (simulating reagent changes)
- **Random outliers** (simulating analytical errors)
- **Method bias** (for comparison studies)
- **Temporal trends** (for QC monitoring)

---

## 📈 Interpretation Guidelines

### Westgard Rules - Action Required:
| Rule | Action | Cause |
|------|--------|-------|
| 1-3s | REJECT run | Random error |
| 2-2s | REJECT run | Systematic error |
| R-4s | REJECT run | Random error increased |
| 4-1s | WARNING | Systematic error developing |
| 10-x | REJECT run | Systematic error present |

### Sigma Interpretation:
| Sigma | Quality | Defect Rate | Action |
|-------|---------|-------------|--------|
| ≥6 | World Class | 3.4 per million | Maintain |
| 5-6 | Excellent | 233 per million | Optimize |
| 4-5 | Good | 6,210 per million | Improve |
| 3-4 | Marginal | 66,807 per million | Troubleshoot |
| <3 | Poor | >66,807 per million | **Urgent action** |

### Statistical Significance:
- **p < 0.05**: Statistically significant (reject null hypothesis)
- **p ≥ 0.05**: Not significant (fail to reject null hypothesis)
- **95% CI**: If includes 0 (for differences) → not significant

---

## 🛠️ Customization

### Modify QC Parameters:
```python
qc = LabQCAnalysis()
qc.parameters['creatinine']['mean'] = 1.1  # New target
qc.parameters['creatinine']['std'] = 0.06   # New SD
qc.parameters['creatinine']['tea'] = 0.20   # New TEa (20%)
```

### Generate More Data:
```python
# More days, more measurements per day
qc_data = qc.generate_qc_data('urea', n_days=60, measurements_per_day=5)

# More patient samples
patient_data = qc.generate_patient_data('creatinine', n_samples=200)
```

---

## 📚 Key Formulas Summary

1. **Sigma**: `(TEa - |Bias|) / CV`
2. **CV**: `(SD / Mean) × 100%`
3. **Bias %**: `((Observed - True) / True) × 100%`
4. **Limits of Agreement**: `Mean Difference ± 1.96 × SD of Differences`
5. **Z-score**: `(Value - Mean) / SD`
6. **Pearson r**: Measures linear correlation
7. **t-statistic**: `Mean Difference / (SD / √n)`
8. **F-statistic**: `Between-group Variance / Within-group Variance`

---

## 🎓 Educational Use

This toolkit is perfect for:
- **Lab technicians**: Understanding QC procedures
- **Lab managers**: Quality assurance and method validation
- **Students**: Learning clinical chemistry QC concepts
- **Researchers**: Method comparison studies
- **Auditors**: QC compliance verification

---

## 📖 References

1. **Westgard QC**: https://www.westgard.com/
2. **Six Sigma in Healthcare**: Nevalainen D, et al. (2000)
3. **Bland-Altman Method**: Bland JM, Altman DG (1986)
4. **CLSI Guidelines**: EP05-A3, EP09-A3, EP15-A3

---

## ⚠️ Important Notes

- This uses **simulated data** for demonstration purposes
- For production use, replace with actual laboratory data
- Always validate QC procedures with your laboratory's specific requirements
- Consult with laboratory director for clinical implementation

---

## 🤝 Support

For questions or issues:
1. Check the generated CSV reports for detailed statistics
2. Review the PNG charts for visual interpretation
3. Consult Westgard QC guidelines for rule interpretation
4. Refer to CLSI documents for method validation

---

**Created**: November 2025  
**Version**: 1.0  
**License**: Educational Use  
**Author**: Laboratory QC Analysis System
