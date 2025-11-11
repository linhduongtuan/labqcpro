# Advanced Fault/Abnormality Detection Guide

## Overview

This guide explains how to improve fault and abnormality detection in laboratory quality control using advanced statistical methods beyond basic Westgard rules.

## 🎯 Key Improvements Implemented

### 1. **Extended Westgard Rules (12 Rules)**
Beyond the basic 5 rules, we now include:

| Rule | Description | Sensitivity | Action |
|------|-------------|-------------|--------|
| **1-3s** | One value > ±3σ | Random error | REJECT - Critical |
| **2-2s** | Two consecutive > ±2σ (same side) | Systematic error | REJECT - Critical |
| **R-4s** | Range between consecutive > 4σ | High random error | REJECT - Critical |
| **4-1s** | Four consecutive > ±1σ (same side) | Trend | WARNING |
| **10-x** | Ten consecutive on same side of mean | Systematic bias | REJECT - Critical |
| **7-T** | Seven consecutive trending | Drift | WARNING |
| **8-x** | Eight consecutive avoid center (±1σ) | Increased variability | WARNING |
| **6-x** | Six consecutive trending | Early drift | WARNING |

### 2. **CUSUM (Cumulative Sum Control Chart)**

**Best for:** Detecting small, sustained shifts quickly

**How it works:**
- Accumulates deviations from target
- More sensitive than Shewhart charts for shifts < 1.5σ
- Detects shifts in ~5 runs vs 10-15 for Shewhart

**Parameters:**
- **k** (reference value): 0.5σ (typical)
- **h** (decision interval): 4-5σ (typical)

**When to use:**
- Monitoring critical analytes (troponin, drug levels)
- Early detection of reagent degradation
- Instrument calibration drift

**Advantages:**
- Detects shifts 2-3x faster than Shewhart
- Good for small systematic changes
- Visual trend identification

### 3. **EWMA (Exponentially Weighted Moving Average)**

**Best for:** Smoothing data and detecting gradual trends

**How it works:**
- Weighs recent data more heavily
- Creates smooth trend line
- Control limits tighter than Shewhart

**Parameters:**
- **λ** (lambda): 0.2-0.3 (typical weighting factor)
  - Small λ (0.05-0.2): More smoothing, detect small shifts
  - Large λ (0.4-0.5): Less smoothing, closer to Shewhart
- **L**: 2.7-3.0 (control limit multiplier)

**When to use:**
- Noisy data that needs smoothing
- Detecting gradual deterioration
- Temperature-dependent reactions

**Advantages:**
- Robust to outliers
- Smooth visualization
- Adjustable sensitivity

### 4. **Statistical Anomaly Detection**

**Best for:** Identifying unusual values independent of process control

**Methods:**
- **Modified Z-score**: Uses median absolute deviation (MAD)
  - More robust than standard Z-score
  - Threshold: 3.5 (typical)
- **Isolation Forest** (ML-based, future enhancement)
- **Local Outlier Factor** (ML-based, future enhancement)

**When to use:**
- Unknown fault patterns
- Multi-analyte correlation issues
- Identifying specimen problems

### 5. **Trend Detection**

**Best for:** Identifying systematic drift before Westgard violations

**How it works:**
- Moving window linear regression
- Tests slope significance (p < 0.05)
- Calculates change in σ units

**Parameters:**
- Window size: 10-15 runs
- Significance threshold: Change > 1.5σ

**When to use:**
- Predictive maintenance
- Reagent stability monitoring
- Environmental effects (temperature, humidity)

### 6. **Run Analysis**

**Best for:** Detecting unusual patterns in data

**Rules:**
- 6 out of 7 on same side of mean
- Excessive alternating (zigzag) patterns
- Clustering analysis

**When to use:**
- Carryover issues
- Sample preparation problems
- Systematic variation detection

## 📊 Sensitivity Levels

Configure detection sensitivity based on your needs:

```python
detector = AdvancedFaultDetector(mean, std, sensitivity='medium')
```

### Sensitivity Settings

| Level | Warning | Alert | Critical | Use Case |
|-------|---------|-------|----------|----------|
| **High** | 1.5σ | 2.0σ | 2.5σ | Critical care, stat labs |
| **Medium** | 2.0σ | 2.5σ | 3.0σ | General chemistry (default) |
| **Low** | 2.5σ | 3.0σ | 3.5σ | Research, high variation |

## 🚀 How to Use

### Basic Usage

```python
from advanced_fault_detection import AdvancedFaultDetector

# Initialize detector
detector = AdvancedFaultDetector(
    mean=1.0,           # Target mean
    std=0.05,           # Target SD
    sensitivity='medium'  # 'high', 'medium', or 'low'
)

# Run comprehensive analysis
results = detector.comprehensive_analysis(qc_values)

# Display summary
summary = results['summary']
print(summary['message'])
print(f"Total violations: {summary['total_violations']}")
print(f"Critical: {summary['critical']}")
print(f"Warning: {summary['warning']}")

# Create visualization
fig = detector.plot_comprehensive_charts(qc_values, results, 'Creatinine')
plt.savefig('fault_detection.png', dpi=300)
plt.show()
```

### Individual Methods

```python
# 1. Extended Westgard only
westgard_violations = detector.extended_westgard_rules(values)

# 2. CUSUM only
cusum_results = detector.cusum_detection(values)
print(f"CUSUM violations: {len(cusum_results['violations'])}")

# 3. EWMA only
ewma_results = detector.ewma_detection(values)
print(f"EWMA violations: {len(ewma_results['violations'])}")

# 4. Anomaly detection only
anomalies = detector.anomaly_detection_zscore(values, threshold=3.5)

# 5. Trend detection only
trends = detector.trend_detection(values, window=10)
```

### Interpreting Results

```python
results = detector.comprehensive_analysis(values)

# Access specific results
westgard_viol = results['westgard']
cusum_viol = results['cusum']['violations']
ewma_viol = results['ewma']['violations']
anomalies = results['anomalies']
trends = results['trends']

# All violations combined
all_violations = results['all_violations']

# Display detailed violations
print(all_violations[['index', 'method', 'severity', 'description', 'action']])
```

## 📈 Visualization Components

The comprehensive chart includes:

1. **Levey-Jennings Chart** (top)
   - All measurements with control limits
   - Westgard violations marked with red X
   
2. **CUSUM Chart** (middle-left)
   - CUSUM+ (upward shifts)
   - CUSUM- (downward shifts)
   - Decision limits (h)
   
3. **EWMA Chart** (middle-right)
   - Raw data (light blue dots)
   - EWMA trend line (blue)
   - Control limits (red dashed)
   
4. **Violations Timeline** (bottom)
   - All violations chronologically
   - X = Critical, o = Warning
   - Color-coded by method

## 🎯 Recommended Workflows

### Workflow 1: Daily QC Monitoring
```
1. Run Westgard rules (traditional)
2. Run EWMA (trend monitoring)
3. Check for violations
4. If violations → investigate
```

### Workflow 2: Predictive Maintenance
```
1. Run CUSUM (sensitive to small shifts)
2. Run trend detection (early warning)
3. If trends detected → schedule maintenance
4. Document baseline performance
```

### Workflow 3: Troubleshooting
```
1. Run comprehensive analysis
2. Review all violation types
3. Identify pattern:
   - CUSUM only → Sustained shift
   - Westgard + Anomaly → Random errors
   - Trend → Systematic drift
   - Run patterns → Operational issues
```

### Workflow 4: Method Validation
```
1. Collect 20+ days of data
2. Run comprehensive analysis
3. Evaluate sigma metrics
4. Assess control stability
5. Determine optimal sensitivity
```

## ⚙️ Parameter Tuning

### CUSUM Parameters

```python
# More sensitive (detect smaller shifts faster)
detector.cusum_k = 0.25  # Default: 0.5
detector.cusum_h = 3.0   # Default: 4.0

# Less sensitive (fewer false alarms)
detector.cusum_k = 0.75
detector.cusum_h = 5.0
```

### EWMA Parameters

```python
# More smoothing (good for noisy data)
detector.ewma_lambda = 0.1   # Default: 0.2
detector.ewma_L = 2.5        # Default: 2.7

# Less smoothing (quicker response)
detector.ewma_lambda = 0.3
detector.ewma_L = 3.0
```

## 📋 Decision Matrix

| Violation Pattern | Likely Cause | Action |
|------------------|--------------|--------|
| **1-3s only** | Random error, specimen issue | Repeat measurement |
| **2-2s, 10-x** | Systematic bias | Recalibrate |
| **R-4s** | High random error | Check precision, reagents |
| **CUSUM sustained** | Reagent lot change, drift | Verify calibration |
| **EWMA trending** | Temperature, reagent aging | Environmental control |
| **Trend upward/downward** | Calibration drift | Recalibrate soon |
| **Multiple methods** | Serious problem | Stop testing, investigate |

## 🔧 Integration with Real-Time Monitor

The advanced detection is already integrated into the real-time monitors:

### Desktop Monitor
```bash
python3.14 realtime_qc_desktop.py
# Select option 1, 2, or 3
```

### Web Dashboard
```bash
python3.14 realtime_qc_monitor.py
# Open http://127.0.0.1:8050
```

Both monitors use Westgard rules by default. To add advanced detection, they would need enhancement (future feature).

## 📚 Demo and Examples

### Run the demo:
```bash
python3.14 advanced_fault_detection.py
```

### Run via lab_qc_demo:
```bash
python3.14 lab_qc_demo.py
# Select option 9: Advanced Fault Detection
```

### Command-line demo:
```bash
python3.14 lab_qc_demo.py advanced
```

## 🎓 Best Practices

1. **Start with Westgard** - Foundation of QC
2. **Add CUSUM for critical analytes** - Early shift detection
3. **Use EWMA for noisy data** - Better visualization
4. **Enable trend detection** - Predictive maintenance
5. **Tune sensitivity** - Balance false positives vs detection power
6. **Document baselines** - Know normal variation
7. **Review patterns** - Multiple violations indicate serious issues
8. **Regular review** - Weekly trend analysis

## 🔍 When Each Method Excels

| Scenario | Best Method | Why |
|----------|-------------|-----|
| Small systematic shift (0.5-1.0σ) | CUSUM | Detects 2-3x faster |
| Noisy data | EWMA | Smooths variation |
| Sudden large error | Westgard (1-3s) | Immediate detection |
| Gradual drift | Trend Detection | Early warning |
| Unknown patterns | Anomaly Detection | Pattern-free |
| Carryover issues | Run Analysis | Detects alternating patterns |

## 📊 Performance Comparison

| Method | Shift Size | Average Detection Time | False Alarm Rate |
|--------|-----------|----------------------|------------------|
| Shewhart (1-3s) | 3.0σ | 1 run | ~0.3% |
| Shewhart (2-2s) | 2.0σ | 2 runs | ~0.5% |
| CUSUM | 1.0σ | 5 runs | ~1% |
| CUSUM | 0.5σ | 10 runs | ~1% |
| EWMA (λ=0.2) | 1.0σ | 4-6 runs | ~1% |
| EWMA (λ=0.2) | 0.5σ | 8-12 runs | ~1% |

## 🚨 Alert Prioritization

### Critical (REJECT Run)
- 1-3s violation
- 2-2s violation
- R-4s violation
- 10-x violation
- CUSUM exceeds h
- Multiple concurrent violations

### Warning (Investigate)
- 4-1s violation
- Trend detected
- EWMA near limits
- Run patterns
- Single anomaly

### Information (Monitor)
- Approaching control limits
- Slight trends
- Occasional run patterns

## 📈 Future Enhancements

Potential additions:
- **Machine Learning models** (Isolation Forest, LSTM)
- **Multi-analyte correlation** analysis
- **Bayesian change point** detection
- **Automated root cause** suggestions
- **Integration with LIMS**
- **Mobile alerts**

## 💡 Summary

**Key Takeaway:** Use multiple methods for comprehensive detection:
- **Westgard** = Foundation
- **CUSUM** = Early shift detection
- **EWMA** = Trend visualization
- **Anomaly** = Unknown patterns
- **Trend** = Predictive maintenance

Together, these methods provide defense-in-depth for laboratory quality control.
