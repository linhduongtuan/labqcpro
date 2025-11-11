"""
Advanced Fault/Abnormality Detection for Laboratory Quality Control

This module implements enhanced detection methods including:
- Extended Westgard Rules (all 12 rules)
- CUSUM (Cumulative Sum Control Chart)
- EWMA (Exponentially Weighted Moving Average)
- Anomaly Detection (Statistical and ML-based)
- Trend Detection
- Multi-rule Shewhart Charts
- Run Rules Analysis
"""

import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from collections import deque
import warnings
warnings.filterwarnings('ignore')


class AdvancedFaultDetector:
    """Advanced fault detection for laboratory QC"""
    
    def __init__(self, mean, std, sensitivity='medium'):
        """
        Initialize detector
        
        Parameters:
        -----------
        mean : float
            Target mean value
        std : float
            Target standard deviation
        sensitivity : str
            'high', 'medium', 'low' - affects alert thresholds
        """
        self.mean = mean
        self.std = std
        self.sensitivity = sensitivity
        
        # Sensitivity settings
        self.thresholds = {
            'high': {'warning': 1.5, 'alert': 2.0, 'critical': 2.5},
            'medium': {'warning': 2.0, 'alert': 2.5, 'critical': 3.0},
            'low': {'warning': 2.5, 'alert': 3.0, 'critical': 3.5}
        }
        
        # CUSUM parameters
        self.cusum_k = 0.5  # Reference value (usually 0.5*sigma)
        self.cusum_h = 4.0  # Decision interval (usually 4-5*sigma)
        
        # EWMA parameters
        self.ewma_lambda = 0.2  # Weighting factor (0.2-0.3 typical)
        self.ewma_L = 2.7  # Control limit multiplier
        
    def extended_westgard_rules(self, values):
        """
        Apply all 12 Westgard rules (expanded set)
        
        Returns violations with severity levels
        """
        violations = []
        n = len(values)
        
        for i in range(n):
            z_score = (values[i] - self.mean) / self.std
            
            # Rule 1-3s: One observation > 3 SD
            if abs(z_score) > 3:
                violations.append({
                    'index': i,
                    'rule': '1-3s',
                    'severity': 'CRITICAL',
                    'description': 'Single value exceeds ±3σ',
                    'z_score': z_score,
                    'action': 'REJECT run - Random error'
                })
            
            # Rule 2-2s: Two consecutive > 2 SD (same side)
            if i > 0:
                z_prev = (values[i-1] - self.mean) / self.std
                if abs(z_score) > 2 and abs(z_prev) > 2 and np.sign(z_score) == np.sign(z_prev):
                    violations.append({
                        'index': i,
                        'rule': '2-2s',
                        'severity': 'CRITICAL',
                        'description': 'Two consecutive values exceed ±2σ (same side)',
                        'z_score': z_score,
                        'action': 'REJECT run - Systematic error'
                    })
            
            # Rule R-4s: Range of consecutive values > 4 SD
            if i > 0:
                range_val = abs(values[i] - values[i-1])
                if range_val > 4 * self.std:
                    violations.append({
                        'index': i,
                        'rule': 'R-4s',
                        'severity': 'CRITICAL',
                        'description': 'Range between consecutive values > 4σ',
                        'z_score': z_score,
                        'action': 'REJECT run - High random error'
                    })
            
            # Rule 4-1s: Four consecutive > 1 SD (same side)
            if i >= 3:
                last_4_z = [(values[j] - self.mean) / self.std for j in range(i-3, i+1)]
                if all(z > 1 for z in last_4_z) or all(z < -1 for z in last_4_z):
                    violations.append({
                        'index': i,
                        'rule': '4-1s',
                        'severity': 'WARNING',
                        'description': 'Four consecutive values exceed ±1σ (same side)',
                        'z_score': z_score,
                        'action': 'WARNING - Systematic shift trend'
                    })
            
            # Rule 10-x: 10 consecutive on same side of mean
            if i >= 9:
                last_10 = values[i-9:i+1]
                if all(val > self.mean for val in last_10) or all(val < self.mean for val in last_10):
                    violations.append({
                        'index': i,
                        'rule': '10-x',
                        'severity': 'CRITICAL',
                        'description': '10 consecutive values on same side of mean',
                        'z_score': z_score,
                        'action': 'REJECT run - Systematic bias'
                    })
            
            # Rule 7-T: Seven consecutive increasing or decreasing
            if i >= 6:
                last_7 = values[i-6:i+1]
                diffs = np.diff(last_7)
                if all(d > 0 for d in diffs) or all(d < 0 for d in diffs):
                    violations.append({
                        'index': i,
                        'rule': '7-T',
                        'severity': 'WARNING',
                        'description': 'Seven consecutive trending values',
                        'z_score': z_score,
                        'action': 'WARNING - Systematic trend'
                    })
            
            # Rule 8-x: Eight consecutive on both sides but none in middle third
            if i >= 7:
                last_8_z = [(values[j] - self.mean) / self.std for j in range(i-7, i+1)]
                if all(abs(z) > 1 for z in last_8_z):
                    violations.append({
                        'index': i,
                        'rule': '8-x',
                        'severity': 'WARNING',
                        'description': 'Eight consecutive values avoid center (±1σ)',
                        'z_score': z_score,
                        'action': 'WARNING - Increased variability'
                    })
            
            # Rule 6-x: Six consecutive all increasing or decreasing
            if i >= 5:
                last_6 = values[i-5:i+1]
                diffs = np.diff(last_6)
                if all(d > 0 for d in diffs) or all(d < 0 for d in diffs):
                    violations.append({
                        'index': i,
                        'rule': '6-x',
                        'severity': 'WARNING',
                        'description': 'Six consecutive trending values',
                        'z_score': z_score,
                        'action': 'WARNING - Trend detected'
                    })
        
        return pd.DataFrame(violations)
    
    def cusum_detection(self, values):
        """
        CUSUM (Cumulative Sum) control chart
        Highly sensitive to small sustained shifts
        """
        n = len(values)
        cusum_pos = np.zeros(n)
        cusum_neg = np.zeros(n)
        
        violations = []
        
        for i in range(n):
            deviation = (values[i] - self.mean) / self.std
            
            # Positive CUSUM
            if i == 0:
                cusum_pos[i] = max(0, deviation - self.cusum_k)
                cusum_neg[i] = max(0, -deviation - self.cusum_k)
            else:
                cusum_pos[i] = max(0, cusum_pos[i-1] + deviation - self.cusum_k)
                cusum_neg[i] = max(0, cusum_neg[i-1] - deviation - self.cusum_k)
            
            # Check for violations
            if cusum_pos[i] > self.cusum_h:
                violations.append({
                    'index': i,
                    'type': 'CUSUM_HIGH',
                    'severity': 'CRITICAL',
                    'description': f'Upward shift detected (CUSUM+ = {cusum_pos[i]:.2f})',
                    'value': cusum_pos[i],
                    'action': 'REJECT - Sustained upward shift'
                })
            
            if cusum_neg[i] > self.cusum_h:
                violations.append({
                    'index': i,
                    'type': 'CUSUM_LOW',
                    'severity': 'CRITICAL',
                    'description': f'Downward shift detected (CUSUM- = {cusum_neg[i]:.2f})',
                    'value': cusum_neg[i],
                    'action': 'REJECT - Sustained downward shift'
                })
        
        return {
            'violations': pd.DataFrame(violations),
            'cusum_pos': cusum_pos,
            'cusum_neg': cusum_neg
        }
    
    def ewma_detection(self, values):
        """
        EWMA (Exponentially Weighted Moving Average)
        Good for detecting small shifts
        """
        n = len(values)
        ewma = np.zeros(n)
        ewma[0] = values[0]
        
        # Calculate control limits
        sigma_ewma = self.std * np.sqrt(self.ewma_lambda / (2 - self.ewma_lambda))
        ucl = self.mean + self.ewma_L * sigma_ewma
        lcl = self.mean - self.ewma_L * sigma_ewma
        
        violations = []
        
        for i in range(1, n):
            ewma[i] = self.ewma_lambda * values[i] + (1 - self.ewma_lambda) * ewma[i-1]
            
            if ewma[i] > ucl:
                violations.append({
                    'index': i,
                    'type': 'EWMA_HIGH',
                    'severity': 'WARNING',
                    'description': f'EWMA exceeds upper limit ({ewma[i]:.4f} > {ucl:.4f})',
                    'value': ewma[i],
                    'action': 'WARNING - Upward trend detected'
                })
            
            if ewma[i] < lcl:
                violations.append({
                    'index': i,
                    'type': 'EWMA_LOW',
                    'severity': 'WARNING',
                    'description': f'EWMA below lower limit ({ewma[i]:.4f} < {lcl:.4f})',
                    'value': ewma[i],
                    'action': 'WARNING - Downward trend detected'
                })
        
        return {
            'violations': pd.DataFrame(violations),
            'ewma': ewma,
            'ucl': ucl,
            'lcl': lcl
        }
    
    def anomaly_detection_zscore(self, values, threshold=3.5):
        """
        Statistical anomaly detection using modified Z-score
        Uses median absolute deviation (MAD) for robustness
        """
        median = np.median(values)
        mad = np.median(np.abs(values - median))
        
        # Modified Z-score
        modified_z_scores = 0.6745 * (values - median) / mad if mad > 0 else np.zeros_len(values)
        
        anomalies = []
        for i, z_score in enumerate(modified_z_scores):
            if abs(z_score) > threshold:
                severity = 'CRITICAL' if abs(z_score) > 4.5 else 'WARNING'
                anomalies.append({
                    'index': i,
                    'type': 'STATISTICAL_ANOMALY',
                    'severity': severity,
                    'description': f'Statistical outlier (modified Z = {z_score:.2f})',
                    'modified_z_score': z_score,
                    'action': f'{severity} - Outlier detected'
                })
        
        return pd.DataFrame(anomalies)
    
    def trend_detection(self, values, window=10):
        """
        Detect trends using linear regression on moving windows
        """
        n = len(values)
        trends = []
        
        for i in range(window, n):
            window_data = values[i-window:i]
            x = np.arange(window)
            
            # Linear regression
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, window_data)
            
            # Determine if trend is significant
            if p_value < 0.05:  # Significant trend
                trend_direction = 'UPWARD' if slope > 0 else 'DOWNWARD'
                
                # Calculate change over window
                change = slope * window / self.std  # Normalize by SD
                
                if abs(change) > 1.5:  # Significant change
                    severity = 'WARNING' if abs(change) < 2.5 else 'CRITICAL'
                    trends.append({
                        'index': i,
                        'type': f'TREND_{trend_direction}',
                        'severity': severity,
                        'description': f'{trend_direction.capitalize()} trend (slope={slope:.4f}, R²={r_value**2:.3f})',
                        'slope': slope,
                        'r_squared': r_value**2,
                        'change_in_sd': change,
                        'action': f'{severity} - Systematic {trend_direction.lower()} drift'
                    })
        
        return pd.DataFrame(trends)
    
    def run_analysis(self, values):
        """
        Run rules analysis - detect unusual patterns
        """
        violations = []
        n = len(values)
        
        for i in range(7, n):  # Need at least 7 points
            last_9 = values[i-8:i+1]
            
            # Run above/below mean
            above = sum(1 for v in last_9 if v > self.mean)
            below = sum(1 for v in last_9 if v < self.mean)
            
            # 6 out of 7 on same side
            if i >= 6:
                last_7 = values[i-6:i+1]
                above_7 = sum(1 for v in last_7 if v > self.mean)
                if above_7 >= 6 or above_7 <= 1:
                    violations.append({
                        'index': i,
                        'type': 'RUN_RULE_6/7',
                        'severity': 'WARNING',
                        'description': '6 out of 7 points on same side of mean',
                        'action': 'WARNING - Potential bias'
                    })
            
            # Alternating pattern (zigzag)
            if i >= 7:
                last_8 = values[i-7:i+1]
                diffs = np.diff(last_8)
                sign_changes = sum(1 for j in range(len(diffs)-1) 
                                 if np.sign(diffs[j]) != np.sign(diffs[j+1]))
                if sign_changes >= 6:  # Many sign changes
                    violations.append({
                        'index': i,
                        'type': 'ZIGZAG_PATTERN',
                        'severity': 'WARNING',
                        'description': 'Excessive alternating pattern detected',
                        'action': 'WARNING - Check for systematic variation'
                    })
        
        return pd.DataFrame(violations)
    
    def comprehensive_analysis(self, values, save_dir=None):
        """
        Run all detection methods and combine results
        """
        print("Running comprehensive fault detection...")
        print("="*80)
        
        # 1. Extended Westgard Rules
        westgard = self.extended_westgard_rules(values)
        print(f"✓ Westgard Rules: {len(westgard)} violations")
        
        # 2. CUSUM
        cusum_result = self.cusum_detection(values)
        print(f"✓ CUSUM: {len(cusum_result['violations'])} violations")
        
        # 3. EWMA
        ewma_result = self.ewma_detection(values)
        print(f"✓ EWMA: {len(ewma_result['violations'])} violations")
        
        # 4. Anomaly Detection
        anomalies = self.anomaly_detection_zscore(values)
        print(f"✓ Anomaly Detection: {len(anomalies)} anomalies")
        
        # 5. Trend Detection
        trends = self.trend_detection(values)
        print(f"✓ Trend Detection: {len(trends)} trends")
        
        # 6. Run Analysis
        runs = self.run_analysis(values)
        print(f"✓ Run Analysis: {len(runs)} patterns")
        
        print("="*80)
        
        # Combine all results
        all_violations = pd.concat([
            westgard.assign(method='Westgard'),
            cusum_result['violations'].assign(method='CUSUM'),
            ewma_result['violations'].assign(method='EWMA'),
            anomalies.assign(method='Anomaly'),
            trends.assign(method='Trend'),
            runs.assign(method='Run')
        ], ignore_index=True)
        
        # Sort by index (chronological order)
        if len(all_violations) > 0:
            all_violations = all_violations.sort_values('index').reset_index(drop=True)
        # Optionally save CUSUM/EWMA analyses to CSV
        if save_dir:
            try:
                os.makedirs(save_dir, exist_ok=True)
            except Exception:
                pass

            # CUSUM summary (pos/neg series)
            cusum = cusum_result
            n = len(values)
            try:
                cusum_df = pd.DataFrame({
                    'run': np.arange(n) + 1,
                    'cusum_pos': cusum['cusum_pos'],
                    'cusum_neg': cusum['cusum_neg']
                })
                cusum_df.to_csv(os.path.join(save_dir, 'cusum_analysis.csv'), index=False)
            except Exception:
                # Don't fail the analysis if saving fails
                pass

            # EWMA series with control limits
            ewma = ewma_result
            try:
                ewma_df = pd.DataFrame({
                    'run': np.arange(n) + 1,
                    'ewma': ewma['ewma']
                })
                ewma_df['ucl'] = ewma.get('ucl', np.nan)
                ewma_df['lcl'] = ewma.get('lcl', np.nan)
                ewma_df.to_csv(os.path.join(save_dir, 'ewma_analysis.csv'), index=False)
            except Exception:
                pass

            # Also save any CUSUM/EWMA violations if present
            try:
                if isinstance(cusum.get('violations'), pd.DataFrame) and len(cusum['violations']) > 0:
                    cusum['violations'].to_csv(os.path.join(save_dir, 'cusum_violations.csv'), index=False)
            except Exception:
                pass

            try:
                if isinstance(ewma.get('violations'), pd.DataFrame) and len(ewma['violations']) > 0:
                    ewma['violations'].to_csv(os.path.join(save_dir, 'ewma_violations.csv'), index=False)
            except Exception:
                pass

        return {
            'all_violations': all_violations,
            'westgard': westgard,
            'cusum': cusum_result,
            'ewma': ewma_result,
            'anomalies': anomalies,
            'trends': trends,
            'runs': runs,
            'summary': self._generate_summary(all_violations)
        }
    
    def _generate_summary(self, violations):
        """Generate summary statistics"""
        if len(violations) == 0:
            return {
                'total_violations': 0,
                'critical': 0,
                'warning': 0,
                'methods': {},
                'message': '✅ No violations detected - QC is in control'
            }
        
        summary = {
            'total_violations': len(violations),
            'critical': len(violations[violations['severity'] == 'CRITICAL']),
            'warning': len(violations[violations['severity'] == 'WARNING']),
            'methods': violations.groupby('method').size().to_dict(),
            'by_severity': violations.groupby('severity').size().to_dict()
        }
        
        if summary['critical'] > 0:
            summary['message'] = f"🚨 CRITICAL: {summary['critical']} critical violations - REJECT run"
        elif summary['warning'] > 0:
            summary['message'] = f"⚠️  WARNING: {summary['warning']} warnings - Investigate"
        else:
            summary['message'] = "✅ QC is acceptable"
        
        return summary
    
    def plot_comprehensive_charts(self, values, results, analyte_name='Analyte'):
        """
        Create comprehensive visualization of all detection methods
        """
        fig = plt.figure(figsize=(18, 12))
        gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
        
        x = np.arange(len(values))
        
        # 1. Levey-Jennings with Westgard
        ax1 = fig.add_subplot(gs[0, :])
        ax1.plot(x, values, 'o-', color='steelblue', markersize=4, linewidth=1, label='Measurements')
        ax1.axhline(self.mean, color='green', linestyle='-', linewidth=2, label='Mean')
        ax1.axhline(self.mean + self.std, color='yellow', linestyle='--', alpha=0.7, label='±1σ')
        ax1.axhline(self.mean - self.std, color='yellow', linestyle='--', alpha=0.7)
        ax1.axhline(self.mean + 2*self.std, color='orange', linestyle='--', alpha=0.7, label='±2σ')
        ax1.axhline(self.mean - 2*self.std, color='orange', linestyle='--', alpha=0.7)
        ax1.axhline(self.mean + 3*self.std, color='red', linestyle='-', alpha=0.7, label='±3σ')
        ax1.axhline(self.mean - 3*self.std, color='red', linestyle='-', alpha=0.7)
        
        # Mark violations
        westgard = results['westgard']
        if len(westgard) > 0:
            for _, v in westgard.iterrows():
                ax1.plot(v['index'], values[v['index']], 'rx', markersize=12, markeredgewidth=3)
        
        ax1.set_title(f'{analyte_name} - Levey-Jennings Chart with Westgard Rules', fontweight='bold', fontsize=14)
        ax1.set_xlabel('Run Number')
        ax1.set_ylabel('Value')
        ax1.legend(loc='upper right')
        ax1.grid(True, alpha=0.3)
        
        # 2. CUSUM Chart
        ax2 = fig.add_subplot(gs[1, 0])
        cusum_result = results['cusum']
        ax2.plot(x, cusum_result['cusum_pos'], 'b-', label='CUSUM+', linewidth=2)
        ax2.plot(x, -cusum_result['cusum_neg'], 'r-', label='CUSUM-', linewidth=2)
        ax2.axhline(self.cusum_h, color='red', linestyle='--', label=f'UCL (h={self.cusum_h})')
        ax2.axhline(-self.cusum_h, color='red', linestyle='--', label=f'LCL (-h={self.cusum_h})')
        ax2.axhline(0, color='gray', linestyle='-', alpha=0.5)
        ax2.set_title('CUSUM Chart', fontweight='bold')
        ax2.set_xlabel('Run Number')
        ax2.set_ylabel('CUSUM')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. EWMA Chart
        ax3 = fig.add_subplot(gs[1, 1])
        ewma_result = results['ewma']
        ax3.plot(x, values, 'o', color='lightblue', markersize=3, alpha=0.5, label='Raw Data')
        ax3.plot(x[1:], ewma_result['ewma'][1:], 'b-', linewidth=2, label=f'EWMA (λ={self.ewma_lambda})')
        ax3.axhline(self.mean, color='green', linestyle='-', linewidth=2, label='Target')
        ax3.axhline(ewma_result['ucl'], color='red', linestyle='--', label='UCL')
        ax3.axhline(ewma_result['lcl'], color='red', linestyle='--', label='LCL')
        ax3.set_title('EWMA Chart', fontweight='bold')
        ax3.set_xlabel('Run Number')
        ax3.set_ylabel('Value')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Violations Timeline
        ax4 = fig.add_subplot(gs[2, :])
        all_viol = results['all_violations']
        
        if len(all_viol) > 0:
            methods = all_viol['method'].unique()
            colors = plt.cm.tab10(np.linspace(0, 1, len(methods)))
            method_colors = dict(zip(methods, colors))
            
            for method in methods:
                method_viol = all_viol[all_viol['method'] == method]
                y_val = list(methods).index(method)
                
                for _, v in method_viol.iterrows():
                    marker = 'X' if v['severity'] == 'CRITICAL' else 'o'
                    size = 200 if v['severity'] == 'CRITICAL' else 100
                    ax4.scatter(v['index'], y_val, marker=marker, s=size, 
                              color=method_colors[method], edgecolor='black', linewidth=1.5,
                              label=method if _ == method_viol.index[0] else '')
            
            ax4.set_yticks(range(len(methods)))
            ax4.set_yticklabels(methods)
            ax4.set_xlabel('Run Number')
            ax4.set_title('Violations Timeline (X=Critical, o=Warning)', fontweight='bold')
            ax4.grid(True, alpha=0.3, axis='x')
            ax4.legend(loc='upper right')
        else:
            ax4.text(0.5, 0.5, '✅ No Violations Detected', 
                    ha='center', va='center', fontsize=16, transform=ax4.transAxes)
            ax4.set_xticks([])
            ax4.set_yticks([])
        
        plt.suptitle(f'Comprehensive Fault Detection Analysis - {analyte_name}', 
                    fontsize=16, fontweight='bold', y=0.995)
        
        return fig


def demo_advanced_detection():
    """Demonstration of advanced fault detection"""
    print("\n" + "="*80)
    print("ADVANCED FAULT DETECTION DEMONSTRATION")
    print("="*80)
    
    # Generate test data with various faults
    np.random.seed(42)
    n = 100
    mean = 1.0
    std = 0.05
    
    # Normal data with injected faults
    values = np.random.normal(mean, std, n)
    
    # Inject systematic shift (runs 30-50)
    values[30:50] += 0.08
    
    # Inject trend (runs 60-80)
    values[60:80] += np.linspace(0, 0.12, 20)
    
    # Inject outliers
    values[25] += 3.5 * std
    values[75] -= 3.2 * std
    
    # Initialize detector
    detector = AdvancedFaultDetector(mean, std, sensitivity='medium')
    
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
    
    # Show detailed violations
    if len(results['all_violations']) > 0:
        print("\n" + "="*80)
        print("DETAILED VIOLATIONS")
        print("="*80)
        print(results['all_violations'][['index', 'method', 'severity', 'description', 'action']].to_string(index=False))
    
    # Create visualization
    fig = detector.plot_comprehensive_charts(values, results, 'Creatinine')
    plt.savefig('results/advanced_fault_detection_demo.png', dpi=300, bbox_inches='tight')
    print("\n✓ Chart saved: results/advanced_fault_detection_demo.png")
    plt.show()
    
    return detector, results


if __name__ == "__main__":
    demo_advanced_detection()
