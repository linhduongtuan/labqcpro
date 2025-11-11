"""
Real-Time QC Monitor using Matplotlib Animation
Simpler alternative that runs in a desktop window
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle
import numpy as np
from datetime import datetime, timedelta
from collections import deque
from lab_qc_analysis import LabQCAnalysis

class RealtimeQCMonitor:
    def __init__(self, analyte='creatinine', max_points=50):
        self.qc = LabQCAnalysis(seed=None)
        self.analyte = analyte
        self.params = self.qc.parameters[analyte]
        self.max_points = max_points
        
        # Data storage
        self.times = deque(maxlen=max_points)
        self.values = deque(maxlen=max_points)
        self.violations = []
        
        # Statistics
        self.current_stats = {'mean': 0, 'sd': 0, 'cv': 0, 'bias': 0, 'sigma': 0}
        
        # Initialize plot
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(14, 10))
        self.fig.suptitle(f'Real-Time QC Monitor - {analyte.capitalize()}', 
                         fontsize=16, fontweight='bold')
        
        # Add run number counter
        self.run_number = 0
        
    def generate_measurement(self):
        """Generate a new measurement with occasional anomalies"""
        # 70% normal, 15% shift, 15% outlier
        rand = np.random.random()
        
        if rand < 0.70:  # Normal
            value = np.random.normal(self.params['mean'], self.params['std'])
        elif rand < 0.85:  # Systematic shift
            value = np.random.normal(self.params['mean'] + 1.5 * self.params['std'], 
                                    self.params['std'])
        else:  # Outlier
            value = np.random.normal(self.params['mean'], self.params['std'])
            value += np.random.choice([-1, 1]) * 3.5 * self.params['std']
        
        return value
    
    def check_westgard(self, new_value):
        """Quick Westgard rule check"""
        if len(self.values) < 2:
            return None
        
        mean = self.params['mean']
        std = self.params['std']
        z_score = (new_value - mean) / std
        
        # Rule 1-3s
        if abs(z_score) > 3:
            return {'rule': '1-3s', 'severity': 'CRITICAL', 
                   'message': 'Control exceeds ±3 SD'}
        
        # Rule 2-2s
        if len(self.values) >= 1:
            z_prev = (self.values[-1] - mean) / std
            if abs(z_score) > 2 and abs(z_prev) > 2:
                if np.sign(z_score) == np.sign(z_prev):
                    return {'rule': '2-2s', 'severity': 'CRITICAL',
                           'message': '2 consecutive exceed ±2 SD'}
        
        # Rule R-4s
        if len(self.values) >= 1:
            if abs(new_value - self.values[-1]) > 4 * std:
                return {'rule': 'R-4s', 'severity': 'CRITICAL',
                       'message': 'Range exceeds 4 SD'}
        
        return None
    
    def update_statistics(self):
        """Calculate current statistics"""
        if len(self.values) < 3:
            return
        
        values_array = np.array(list(self.values))
        mean = np.mean(values_array)
        sd = np.std(values_array, ddof=1)
        cv = (sd / mean) * 100 if mean != 0 else 0
        bias = ((mean - self.params['mean']) / self.params['mean']) * 100
        
        tea_pct = self.params['tea'] * 100
        sigma = (tea_pct - abs(bias)) / cv if cv > 0 else 0
        
        self.current_stats = {
            'mean': mean,
            'sd': sd,
            'cv': cv,
            'bias': bias,
            'sigma': sigma
        }
    
    def animate(self, frame):
        """Animation function called for each frame"""
        # Generate new measurement
        self.run_number += 1
        new_value = self.generate_measurement()
        current_time = datetime.now()
        
        self.times.append(self.run_number)
        self.values.append(new_value)
        
        # Check for violations
        violation = self.check_westgard(new_value)
        if violation:
            violation['time'] = current_time
            violation['value'] = new_value
            violation['run'] = self.run_number
            self.violations.append(violation)
        
        # Update statistics
        self.update_statistics()
        
        # Clear axes
        self.ax1.clear()
        self.ax2.clear()
        
        # Plot 1: Levey-Jennings Chart
        mean = self.params['mean']
        std = self.params['std']
        
        # Plot data
        times_list = list(self.times)
        values_list = list(self.values)
        
        self.ax1.plot(times_list, values_list, 'o-', 
                     color='steelblue', markersize=8, linewidth=2, label='Measurements')
        
        # Control limits
        self.ax1.axhline(y=mean, color='green', linestyle='-', linewidth=2, label='Mean')
        self.ax1.axhline(y=mean + std, color='yellow', linestyle='--', linewidth=1.5, label='±1 SD')
        self.ax1.axhline(y=mean - std, color='yellow', linestyle='--', linewidth=1.5)
        self.ax1.axhline(y=mean + 2*std, color='orange', linestyle='--', linewidth=1.5, label='±2 SD')
        self.ax1.axhline(y=mean - 2*std, color='orange', linestyle='--', linewidth=1.5)
        self.ax1.axhline(y=mean + 3*std, color='red', linestyle='-', linewidth=2, label='±3 SD')
        self.ax1.axhline(y=mean - 3*std, color='red', linestyle='-', linewidth=2)
        
        # Highlight violations
        for v in self.violations:
            if v['run'] in times_list:
                idx = times_list.index(v['run'])
                self.ax1.plot(v['run'], values_list[idx], 'rx', 
                            markersize=15, markeredgewidth=3)
        
        self.ax1.set_xlabel('Run Number', fontsize=12, fontweight='bold')
        self.ax1.set_ylabel(f'{self.analyte.capitalize()} ({self.params["unit"]})', 
                           fontsize=12, fontweight='bold')
        self.ax1.set_title('Levey-Jennings Chart', fontsize=14, fontweight='bold')
        self.ax1.legend(loc='upper right', fontsize=10)
        self.ax1.grid(True, alpha=0.3)
        
        # Plot 2: Statistics Dashboard
        self.ax2.axis('off')
        
        # Title
        self.ax2.text(0.5, 0.95, 'Real-Time Statistics & Alerts', 
                     ha='center', va='top', fontsize=14, fontweight='bold',
                     transform=self.ax2.transAxes)
        
        # Statistics table
        stats_text = f"""
Run Number: {self.run_number}
Last Update: {current_time.strftime('%H:%M:%S')}

Current Statistics:
  Mean:  {self.current_stats['mean']:.4f} {self.params['unit']}
  SD:    {self.current_stats['sd']:.4f}
  CV:    {self.current_stats['cv']:.2f}%
  Bias:  {self.current_stats['bias']:.2f}%
  Sigma: {self.current_stats['sigma']:.2f}

Target Values:
  Mean:  {self.params['mean']:.4f} {self.params['unit']}
  SD:    {self.params['std']:.4f}
  TEa:   {self.params['tea']*100:.1f}%
"""
        
        self.ax2.text(0.05, 0.85, stats_text, ha='left', va='top', 
                     fontsize=11, family='monospace',
                     transform=self.ax2.transAxes)
        
        # Sigma quality indicator
        sigma = self.current_stats['sigma']
        if sigma >= 6:
            sigma_color = 'green'
            sigma_label = 'World Class'
        elif sigma >= 5:
            sigma_color = 'lightgreen'
            sigma_label = 'Excellent'
        elif sigma >= 4:
            sigma_color = 'yellow'
            sigma_label = 'Good'
        elif sigma >= 3:
            sigma_color = 'orange'
            sigma_label = 'Marginal'
        else:
            sigma_color = 'red'
            sigma_label = 'Poor'
        
        # Sigma box
        sigma_rect = Rectangle((0.55, 0.70), 0.4, 0.15, 
                               facecolor=sigma_color, alpha=0.3,
                               transform=self.ax2.transAxes)
        self.ax2.add_patch(sigma_rect)
        self.ax2.text(0.75, 0.775, f'Quality: {sigma_label}', 
                     ha='center', va='center', fontsize=12, fontweight='bold',
                     transform=self.ax2.transAxes)
        
        # Recent violations
        violations_text = 'Recent Westgard Violations:\n'
        if len(self.violations) == 0:
            violations_text += '  ✓ No violations detected'
            alert_color = 'lightgreen'
        else:
            recent = self.violations[-5:]  # Last 5
            for v in reversed(recent):
                violations_text += f"  ⚠ Run {v['run']}: {v['rule']} - {v['message']}\n"
            alert_color = 'lightcoral'
        
        # Alert box
        alert_rect = Rectangle((0.05, 0.05), 0.9, 0.35, 
                               facecolor=alert_color, alpha=0.3,
                               transform=self.ax2.transAxes)
        self.ax2.add_patch(alert_rect)
        self.ax2.text(0.5, 0.35, violations_text, 
                     ha='center', va='top', fontsize=10, family='monospace',
                     transform=self.ax2.transAxes)
        
        plt.tight_layout()
        
    def run(self, interval=2000):
        """Start the real-time monitor"""
        ani = animation.FuncAnimation(self.fig, self.animate, 
                                     interval=interval, cache_frame_data=False)
        plt.show()


class DualRealtimeQCMonitor:
    """Monitor both Creatinine and Urea in a single window"""
    
    def __init__(self, max_points=50):
        self.qc = LabQCAnalysis(seed=None)
        self.max_points = max_points
        
        # Data storage for both analytes
        self.monitors = {
            'creatinine': {
                'times': deque(maxlen=max_points),
                'values': deque(maxlen=max_points),
                'violations': [],
                'stats': {'mean': 0, 'sd': 0, 'cv': 0, 'bias': 0, 'sigma': 0}
            },
            'urea': {
                'times': deque(maxlen=max_points),
                'values': deque(maxlen=max_points),
                'violations': [],
                'stats': {'mean': 0, 'sd': 0, 'cv': 0, 'bias': 0, 'sigma': 0}
            }
        }
        
        self.run_number = 0
        
        # Initialize plot with 2 rows, 2 columns
        self.fig = plt.figure(figsize=(16, 12))
        self.fig.suptitle('Real-Time QC Monitor - Dual Analyte', 
                         fontsize=16, fontweight='bold')
        
        # Create subplots: [Creat Chart, Urea Chart, Creat Stats, Urea Stats]
        self.ax_creat_chart = plt.subplot(2, 2, 1)
        self.ax_urea_chart = plt.subplot(2, 2, 2)
        self.ax_creat_stats = plt.subplot(2, 2, 3)
        self.ax_urea_stats = plt.subplot(2, 2, 4)
    
    def generate_measurement(self, analyte):
        """Generate a new measurement"""
        params = self.qc.parameters[analyte]
        rand = np.random.random()
        
        if rand < 0.70:  # Normal
            value = np.random.normal(params['mean'], params['std'])
        elif rand < 0.85:  # Systematic shift
            value = np.random.normal(params['mean'] + 1.5 * params['std'], params['std'])
        else:  # Outlier
            value = np.random.normal(params['mean'], params['std'])
            value += np.random.choice([-1, 1]) * 3.5 * params['std']
        
        return value
    
    def check_westgard(self, analyte, new_value):
        """Quick Westgard rule check"""
        monitor = self.monitors[analyte]
        values = monitor['values']
        
        if len(values) < 2:
            return None
        
        params = self.qc.parameters[analyte]
        mean = params['mean']
        std = params['std']
        z_score = (new_value - mean) / std
        
        # Rule 1-3s
        if abs(z_score) > 3:
            return {'rule': '1-3s', 'severity': 'CRITICAL'}
        
        # Rule 2-2s
        if len(values) >= 1:
            z_prev = (values[-1] - mean) / std
            if abs(z_score) > 2 and abs(z_prev) > 2 and np.sign(z_score) == np.sign(z_prev):
                return {'rule': '2-2s', 'severity': 'CRITICAL'}
        
        return None
    
    def update_statistics(self, analyte):
        """Calculate current statistics"""
        monitor = self.monitors[analyte]
        values = list(monitor['values'])
        
        if len(values) < 3:
            return
        
        params = self.qc.parameters[analyte]
        values_array = np.array(values)
        mean = np.mean(values_array)
        sd = np.std(values_array, ddof=1)
        cv = (sd / mean) * 100 if mean != 0 else 0
        bias = ((mean - params['mean']) / params['mean']) * 100
        
        tea_pct = params['tea'] * 100
        sigma = (tea_pct - abs(bias)) / cv if cv > 0 else 0
        
        monitor['stats'] = {'mean': mean, 'sd': sd, 'cv': cv, 'bias': bias, 'sigma': sigma}
    
    def plot_chart(self, ax, analyte, color):
        """Plot Levey-Jennings chart for one analyte"""
        ax.clear()
        
        monitor = self.monitors[analyte]
        params = self.qc.parameters[analyte]
        mean = params['mean']
        std = params['std']
        
        times_list = list(monitor['times'])
        values_list = list(monitor['values'])
        
        if len(times_list) > 0:
            ax.plot(times_list, values_list, 'o-', color=color, 
                   markersize=6, linewidth=2, label='Measurements')
        
        # Control limits
        ax.axhline(y=mean, color='green', linestyle='-', linewidth=2, alpha=0.7)
        ax.axhline(y=mean + std, color='yellow', linestyle='--', linewidth=1.5, alpha=0.7)
        ax.axhline(y=mean - std, color='yellow', linestyle='--', linewidth=1.5, alpha=0.7)
        ax.axhline(y=mean + 2*std, color='orange', linestyle='--', linewidth=1.5, alpha=0.7)
        ax.axhline(y=mean - 2*std, color='orange', linestyle='--', linewidth=1.5, alpha=0.7)
        ax.axhline(y=mean + 3*std, color='red', linestyle='-', linewidth=2, alpha=0.7)
        ax.axhline(y=mean - 3*std, color='red', linestyle='-', linewidth=2, alpha=0.7)
        
        # Violations
        for v in monitor['violations']:
            if v['run'] in times_list:
                idx = times_list.index(v['run'])
                ax.plot(v['run'], values_list[idx], 'rx', markersize=12, markeredgewidth=3)
        
        ax.set_xlabel('Run Number', fontsize=10, fontweight='bold')
        ax.set_ylabel(f'{analyte.capitalize()} ({params["unit"]})', fontsize=10, fontweight='bold')
        ax.set_title(f'{analyte.capitalize()} - Levey-Jennings Chart', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
    
    def plot_stats(self, ax, analyte):
        """Plot statistics panel"""
        ax.clear()
        ax.axis('off')
        
        monitor = self.monitors[analyte]
        params = self.qc.parameters[analyte]
        stats = monitor['stats']
        
        # Sigma quality
        sigma = stats['sigma']
        if sigma >= 6:
            sigma_color = 'green'
            sigma_label = 'World Class'
        elif sigma >= 5:
            sigma_color = 'lightgreen'
            sigma_label = 'Excellent'
        elif sigma >= 4:
            sigma_color = 'yellow'
            sigma_label = 'Good'
        elif sigma >= 3:
            sigma_color = 'orange'
            sigma_label = 'Marginal'
        else:
            sigma_color = 'red'
            sigma_label = 'Poor'
        
        stats_text = f"{analyte.upper()} Statistics\n\n"
        stats_text += f"Run: {self.run_number}\n"
        stats_text += f"Mean:  {stats['mean']:.4f}\n"
        stats_text += f"SD:    {stats['sd']:.4f}\n"
        stats_text += f"CV:    {stats['cv']:.2f}%\n"
        stats_text += f"Bias:  {stats['bias']:.2f}%\n"
        stats_text += f"Sigma: {sigma:.2f}\n"
        stats_text += f"Quality: {sigma_label}"
        
        ax.text(0.1, 0.9, stats_text, ha='left', va='top', 
               fontsize=11, family='monospace', transform=ax.transAxes)
        
        # Quality box
        rect = Rectangle((0.1, 0.05), 0.8, 0.15, 
                        facecolor=sigma_color, alpha=0.4, transform=ax.transAxes)
        ax.add_patch(rect)
        
        # Violations
        violations_text = f"\nViolations: {len(monitor['violations'])}"
        if len(monitor['violations']) > 0:
            recent = monitor['violations'][-3:]
            for v in reversed(recent):
                violations_text += f"\n  Run {v['run']}: {v['rule']}"
        
        ax.text(0.1, 0.35, violations_text, ha='left', va='top',
               fontsize=10, family='monospace', transform=ax.transAxes)
    
    def animate(self, frame):
        """Animation function"""
        self.run_number += 1
        
        # Update both analytes
        for analyte in ['creatinine', 'urea']:
            monitor = self.monitors[analyte]
            
            # Generate measurement
            new_value = self.generate_measurement(analyte)
            monitor['times'].append(self.run_number)
            monitor['values'].append(new_value)
            
            # Check violations
            violation = self.check_westgard(analyte, new_value)
            if violation:
                violation['run'] = self.run_number
                violation['value'] = new_value
                monitor['violations'].append(violation)
            
            # Update statistics
            self.update_statistics(analyte)
        
        # Plot all panels
        self.plot_chart(self.ax_creat_chart, 'creatinine', 'steelblue')
        self.plot_chart(self.ax_urea_chart, 'urea', 'purple')
        self.plot_stats(self.ax_creat_stats, 'creatinine')
        self.plot_stats(self.ax_urea_stats, 'urea')
        
        plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    def run(self, interval=2000):
        """Start the dual monitor"""
        ani = animation.FuncAnimation(self.fig, self.animate, 
                                     interval=interval, cache_frame_data=False)
        plt.show()


def run_monitor(analyte):
    """Run monitor for a specific analyte (used by multiprocessing)"""
    monitor = RealtimeQCMonitor(analyte, max_points=50)
    monitor.run(interval=2000)


def main():
    print("\n" + "="*80)
    print("🔬 REAL-TIME QC MONITOR - Desktop Application")
    print("="*80)
    print("\nSelect analyte to monitor:")
    print("1. Creatinine")
    print("2. Urea")
    print("3. Both (split screen)")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == '1':
        print("\n📊 Starting Creatinine monitor...")
        print("⚠️  Close the window to stop monitoring\n")
        monitor = RealtimeQCMonitor('creatinine', max_points=50)
        monitor.run(interval=2000)  # Update every 2 seconds
    
    elif choice == '2':
        print("\n📊 Starting Urea monitor...")
        print("⚠️  Close the window to stop monitoring\n")
        monitor = RealtimeQCMonitor('urea', max_points=50)
        monitor.run(interval=2000)
    
    elif choice == '3':
        print("\n📊 Starting dual monitor (side-by-side)...")
        print("⚠️  Close the window to stop monitoring\n")
        
        # Create a dual monitor with both analytes in one window
        dual_monitor = DualRealtimeQCMonitor(max_points=50)
        dual_monitor.run(interval=2000)
    
    else:
        print("Invalid choice. Exiting.")


if __name__ == '__main__':
    main()
