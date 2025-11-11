# 🔴 Real-Time Laboratory QC Monitoring Guide

## 📊 Two Approaches for Real-Time Monitoring

I've created **two different real-time monitoring solutions** for your laboratory QC data:

---

## 🌐 Option 1: Web Dashboard (Recommended)

**File:** `realtime_qc_monitor.py`

### ✨ Features:
- **Web-based interface** - Access from any browser
- **Live updating charts** - Refreshes every second
- **Dual analyte monitoring** - Creatinine & Urea simultaneously
- **Automatic Westgard checking** - Real-time rule violations
- **Alert system** - Visual warnings for out-of-control conditions
- **Statistics dashboard** - Live Mean, SD, CV, Bias, Sigma
- **Violations log** - Track all quality issues
- **Data export** - Download CSV of all measurements
- **Reset function** - Clear data and start fresh

### 🚀 How to Run:

```bash
# Install dependencies first
uv add dash plotly

# Run the dashboard
uv run realtime_qc_monitor.py
```

### 🌐 Access:
Open your browser to: **http://127.0.0.1:8050**

### 📸 What You'll See:

```
┌──────────────────────────────────────────────────────┐
│   🔬 Laboratory QC Real-Time Monitoring Dashboard   │
│        Last Update: 2025-11-10 22:15:30             │
└──────────────────────────────────────────────────────┘

┌─────────────────────┐  ┌────────────────────────┐
│ ✅ CREATININE OK    │  │ 🚨 UREA ALERT         │
│ All controls within │  │ Two consecutive exceed │
│ limits              │  │ Total Violations: 3    │
└─────────────────────┘  └────────────────────────┘

[Creatinine Levey-Jennings Chart - Live updating line chart]

[Urea Levey-Jennings Chart - Live updating line chart]

┌──────────────────────────────────────────────────────┐
│              📊 Current Statistics                   │
├───────────────────────┬──────────────────────────────┤
│ Creatinine Stats      │ Urea Stats                  │
│ Target: 1.0000 mg/dL  │ Target: 25.0000 mg/dL       │
│ Mean:   1.0084 mg/dL  │ Mean:   25.6407 mg/dL       │
│ SD:     0.0528        │ SD:     1.7782              │
│ CV:     5.23%         │ CV:     6.94%               │
│ Bias:   0.84%         │ Bias:   2.56%               │
│ Sigma:  2.71 (Poor)   │ Sigma:  1.24 (Poor)         │
└───────────────────────┴──────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│              ⚠️  Recent Violations                    │
├──────────────────────────────────────────────────────┤
│ UREA     [2-2s]  22:15:25                           │
│ Two consecutive controls exceed ±2 SD                │
│ Value: 28.4521                                       │
│                                                      │
│ CREATININE [R-4s]  22:14:58                         │
│ Range exceeds 4 SD                                   │
│ Value: 1.2341                                        │
└──────────────────────────────────────────────────────┘

        [🔄 Reset Data]  [📊 Export CSV]
```

### ⚙️ Configuration:

Edit `realtime_qc_monitor.py` to customize:

```python
# Update interval (line ~265)
interval=1000  # 1 second (change to 500 for 0.5s, 2000 for 2s)

# Maximum points displayed (line ~21)
max_points = 100  # Change to show more/less history

# Data generation speed (line ~220)
time.sleep(2)  # Wait 2 seconds between measurements
```

---

## 🖥️ Option 2: Desktop Application

**File:** `realtime_qc_desktop.py`

### ✨ Features:
- **Matplotlib animation** - Native desktop window
- **No web browser needed** - Runs as standalone app
- **Choose analyte** - Monitor Creatinine, Urea, or both
- **Live charts** - Updates every 2 seconds
- **Statistics panel** - Real-time metrics display
- **Violation tracking** - Shows recent Westgard violations
- **Quality indicator** - Color-coded Sigma status

### 🚀 How to Run:

```bash
# Run the desktop monitor
uv run realtime_qc_desktop.py
```

### 📋 Interactive Menu:
```
Select analyte to monitor:
1. Creatinine
2. Urea
3. Both (split screen)

Enter choice (1-3): 1
```

### 📸 What You'll See:

```
┌──────────────────────────────────────────────────────┐
│   Real-Time QC Monitor - Creatinine                 │
├──────────────────────────────────────────────────────┤
│  [Levey-Jennings Chart with control limits]         │
│  • Blue line: measurements                           │
│  • Green line: mean                                  │
│  • Yellow: ±1 SD                                     │
│  • Orange: ±2 SD                                     │
│  • Red: ±3 SD                                        │
│  • Red X: violations                                 │
├──────────────────────────────────────────────────────┤
│  Real-Time Statistics & Alerts                       │
│                                                      │
│  Run Number: 42                                      │
│  Last Update: 22:30:15                               │
│                                                      │
│  Current Statistics:                                 │
│    Mean:  1.0084 mg/dL                              │
│    SD:    0.0528                                     │
│    CV:    5.23%                                      │
│    Bias:  0.84%                                      │
│    Sigma: 2.71                                       │
│                                                      │
│  ┌──────────────────┐                               │
│  │ Quality: Poor    │  [Red/Yellow/Green box]       │
│  └──────────────────┘                               │
│                                                      │
│  Recent Westgard Violations:                         │
│  ⚠ Run 38: 1-3s - Control exceeds ±3 SD            │
│  ⚠ Run 35: R-4s - Range exceeds 4 SD               │
└──────────────────────────────────────────────────────┘
```

---

## 📊 How Real-Time Monitoring Works

### 1. **Data Generation**
- Simulates real laboratory measurements
- 70% normal values (within expected range)
- 15% systematic shifts (calibration drift)
- 15% random outliers (analytical errors)

### 2. **Westgard Rule Checking**
Every new measurement is automatically checked against:
- **1-3s**: Single point exceeds ±3 SD → CRITICAL
- **2-2s**: Two consecutive exceed ±2 SD (same side) → CRITICAL
- **R-4s**: Range between two points > 4 SD → CRITICAL
- **4-1s**: Four consecutive exceed ±1 SD → WARNING
- **10-x**: Ten consecutive on same side of mean → CRITICAL

### 3. **Statistics Calculation**
Real-time updates of:
- **Mean**: Running average
- **SD**: Standard deviation
- **CV**: Coefficient of variation (precision)
- **Bias**: Deviation from target
- **Sigma**: Six Sigma quality metric

### 4. **Alert System**
- **Green (OK)**: All measurements within control
- **Red (ALERT)**: Westgard rule violation detected
- Displays violation count and specific rule broken

---

## 🎯 Use Cases

### 1. **Training & Education**
- Demonstrate QC principles to lab staff
- Show how Westgard rules work in real-time
- Visualize impact of systematic errors vs random errors

### 2. **Method Validation**
- Monitor new instruments during validation
- Compare performance across different lots
- Track stability over time

### 3. **Continuous Monitoring**
- Keep dashboard open during production runs
- Immediate notification of quality issues
- Historical trend analysis

### 4. **Troubleshooting**
- Identify patterns in QC failures
- Distinguish systematic from random errors
- Track effectiveness of corrective actions

---

## 🔧 Customization Options

### Modify Target Values:
```python
# In lab_qc_analysis.py, change parameters
self.parameters = {
    'creatinine': {
        'mean': 1.2,     # Your target value
        'std': 0.06,     # Your acceptable SD
        'tea': 0.15,     # Your TEa limit
    }
}
```

### Adjust Westgard Rules:
```python
# In realtime_qc_monitor.py or realtime_qc_desktop.py
# Modify check_westgard_violation() function
# Add or remove rules as needed
```

### Change Update Speed:
```python
# Web dashboard (realtime_qc_monitor.py)
interval=1000  # milliseconds (line ~265)
time.sleep(2)  # seconds between measurements (line ~220)

# Desktop app (realtime_qc_desktop.py)
monitor.run(interval=2000)  # milliseconds (line ~258)
```

---

## 📥 Data Export

### Web Dashboard:
1. Click **"📊 Export CSV"** button
2. File downloads automatically: `qc_data_YYYYMMDD_HHMMSS.csv`

### CSV Format:
```csv
Analyte,Time,Value,Mean,SD,CV,Bias,Sigma
creatinine,2025-11-10 22:15:30,1.0084,1.0050,0.0528,5.23,0.84,2.71
urea,2025-11-10 22:15:30,25.6407,25.4500,1.7782,6.94,2.56,1.24
```

---

## 🔄 Connecting to Real Laboratory Instruments

To connect to actual instruments instead of simulated data:

### 1. **Replace Data Generator**
```python
# Instead of generate_new_measurement()
def read_from_instrument(analyte):
    # Example: Read from serial port
    import serial
    ser = serial.Serial('/dev/ttyUSB0', 9600)
    data = ser.readline().decode('utf-8')
    value = float(data.split(',')[1])  # Parse your format
    return value
```

### 2. **Database Integration**
```python
# Read from laboratory information system (LIS)
import sqlite3

def read_from_database(analyte):
    conn = sqlite3.connect('lab_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT value FROM qc_results 
        WHERE analyte=? 
        ORDER BY timestamp DESC LIMIT 1
    ''', (analyte,))
    value = cursor.fetchone()[0]
    return value
```

### 3. **API Integration**
```python
# Read from instrument API
import requests

def read_from_api(analyte):
    response = requests.get(f'http://instrument-ip/api/qc/{analyte}')
    data = response.json()
    return data['value']
```

---

## ⚠️ Troubleshooting

### Web Dashboard Won't Start:
```bash
# Install dependencies
uv add dash plotly pandas numpy matplotlib scipy

# Check port availability
lsof -i :8050  # Kill process if occupied
```

### Desktop App Won't Show:
```bash
# Install matplotlib with GUI backend
uv add matplotlib

# On macOS, you may need:
export MPLBACKEND=TkAgg
```

### Charts Not Updating:
- Check that data generation thread is running
- Verify no errors in terminal
- Try refreshing browser (web) or restarting app (desktop)

---

## 📚 Comparison: Web vs Desktop

| Feature | Web Dashboard | Desktop App |
|---------|--------------|-------------|
| **Accessibility** | Any browser | Local only |
| **Multi-user** | Yes | No |
| **Dual monitoring** | Built-in | Separate windows |
| **Data export** | Built-in button | Manual |
| **Resource usage** | Higher | Lower |
| **Setup** | Requires Dash | Requires matplotlib |
| **Remote access** | Possible | No |
| **Mobile friendly** | Yes | No |

---

## 🎓 Best Practices

1. **Set Appropriate Update Intervals**
   - Too fast: Hard to read, high CPU usage
   - Too slow: Miss critical events
   - Recommended: 1-2 seconds

2. **Monitor Data History**
   - Keep 50-100 points visible
   - Export data periodically
   - Review trends daily

3. **Respond to Alerts**
   - **1-3s or R-4s**: Check immediately, may reject run
   - **2-2s or 10-x**: Investigate systematic error
   - **4-1s**: Warning sign, monitor closely

4. **Regular Validation**
   - Compare simulated vs actual instrument
   - Verify Westgard rules match your SOP
   - Update target values from proficiency testing

---

## 🚀 Quick Start Guide

### Fastest Way to See It Working:

```bash
# Option 1: Web Dashboard (best for demonstration)
uv add dash plotly
uv run realtime_qc_monitor.py
# Open browser to http://127.0.0.1:8050

# Option 2: Desktop App (simpler setup)
uv run realtime_qc_desktop.py
# Select option 1 (Creatinine)
```

---

## 📞 Support

For issues or customization:
1. Check the inline comments in both files
2. Modify parameters in `lab_qc_analysis.py`
3. Refer to Dash documentation: https://dash.plotly.com
4. Matplotlib animation: https://matplotlib.org/stable/api/animation_api.html

---

**Created**: November 10, 2025  
**Version**: 1.0  
**Status**: Production Ready  
**Testing**: Simulated data - adapt for real instruments
