# Laboratory Quality Control & Sigma Abnormality Detection System

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A comprehensive Python-based quality control system for clinical laboratory testing, implementing advanced statistical methods including Westgard Rules, Six Sigma metrics, real-time monitoring, and anomaly detection for Creatinine and Urea measurements.

## 🎯 Features

### Core QC Analysis (`lab_qc_analysis.py`)
- **Levey-Jennings Charts**: Visual representation of QC data with control limits
- **Westgard Rules**: Implementation of multi-rule quality control (1-2s, 1-3s, 2-2s, R-4s, 4-1s, 10-x)
- **Six Sigma Metrics**: Calculate sigma values and quality levels
- **Total Allowable Error (TEa)**: CLIA-based performance evaluation
- **Statistical Analysis**: 
  - Method comparison (Bland-Altman plots)
  - Correlation analysis (Pearson, Spearman)
  - Hypothesis testing (t-tests, Mann-Whitney U, ANOVA)
  - Bias and CV calculations

### Real-Time Monitoring
- **Web-based Dashboard** (`realtime_qc_monitor.py`): Interactive Dash application with live updates
- **Desktop Monitor** (`realtime_qc_desktop.py`): Matplotlib-based real-time visualization
- **Auto-refresh**: Configurable update intervals (1-10 seconds)
- **Alert System**: Visual and textual alerts for rule violations

### Advanced Fault Detection (`advanced_fault_detection.py`)
- **Extended Westgard Rules**: All 12 rules including 2-3s, 3-1s, 6-x, 8-x, 9-x, 12-x
- **CUSUM (Cumulative Sum)**: Detect small systematic shifts
- **EWMA (Exponentially Weighted Moving Average)**: Sensitive to process changes
- **Anomaly Detection**: Statistical and ML-based outlier detection
- **Trend Analysis**: Identify systematic trends in QC data
- **Multi-rule Shewhart Charts**: Comprehensive quality control charting

### Interactive Demo (`lab_qc_demo.py`)
- Guided demonstrations of all QC features
- Command-line interface for easy exploration
- Pre-configured scenarios for training and validation

## 📊 Screenshots

### Levey-Jennings Chart with Westgard Rules
![Levey-Jennings Chart](results/levey_jennings_example.png)

### Real-Time Monitoring Dashboard
![Real-Time Monitor](results/realtime_monitor.png)

### Six Sigma Quality Assessment
![Sigma Metrics](results/sigma_chart.png)

## 🚀 Quick Start

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/QC_sigma_abnormality_detection.git
cd QC_sigma_abnormality_detection
```

2. **Create virtual environment**
```bash
# Using uv (recommended - faster)
uv venv
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows

# Using traditional venv
python -m venv .venv
source .venv/bin/activate
```

3. **Install dependencies**
```bash
# Using uv
uv pip install numpy pandas matplotlib seaborn scipy plotly dash

# Using pip
pip install numpy pandas matplotlib seaborn scipy plotly dash
```

### Usage

#### 1. Run Complete QC Analysis
```bash
python lab_qc_analysis.py
```
Generates comprehensive reports with charts and CSV outputs in the `results/` directory.

#### 2. Interactive Demo
```bash
python lab_qc_demo.py
```

Available demo modes:
- `levey`: Levey-Jennings charts
- `westgard`: Westgard rules analysis
- `sigma`: Six Sigma metrics
- `comparison`: Method comparison
- `correlation`: Correlation analysis
- `statistical`: Statistical tests
- `advanced`: All analyses
- `realtime`: Real-time monitoring

Example:
```bash
python lab_qc_demo.py sigma
```

#### 3. Real-Time Web Dashboard
```bash
python realtime_qc_monitor.py
```
Then open your browser to `http://localhost:8050`

#### 4. Real-Time Desktop Monitor
```bash
python realtime_qc_desktop.py
```

#### 5. Advanced Fault Detection
```bash
python advanced_fault_detection.py
```

## 📁 Project Structure

```
QC_sigma_abnormality_detection/
├── lab_qc_analysis.py           # Core QC analysis engine
├── lab_qc_demo.py                # Interactive demonstration
├── realtime_qc_monitor.py        # Web-based real-time dashboard
├── realtime_qc_desktop.py        # Desktop real-time monitor
├── advanced_fault_detection.py   # Advanced detection methods
├── start_realtime_monitor.py     # Quick start script
├── quick_reference.py            # API reference guide
├── test_dual_monitor.py          # Multi-monitor testing
├── validate_fix.py               # Validation utilities
├── pyproject.toml                # Project dependencies
├── requirements.txt              # Pip requirements
├── data/                         # Sample QC data
├── results/                      # Generated reports and charts
├── docs/                         # Documentation
│   ├── TECHNICAL_REPORT.md       # Detailed technical documentation
│   ├── API_REFERENCE.md          # API documentation
│   └── USER_GUIDE.md             # User guide
└── README.md                     # This file
```

## 🔬 Scientific Background

### Westgard Rules
Multi-rule quality control system designed to detect analytical errors:
- **1-2s**: Warning rule - one control exceeds ±2 SD
- **1-3s**: Rejection rule - one control exceeds ±3 SD (random error)
- **2-2s**: Two consecutive controls exceed ±2 SD on same side (systematic error)
- **R-4s**: Range rule - difference between controls exceeds 4 SD
- **4-1s**: Four consecutive controls exceed ±1 SD on same side
- **10-x**: Ten consecutive controls on same side of mean

### Six Sigma Methodology
Quality metric expressing defects per million opportunities:
- **Sigma ≥ 6**: World Class (3.4 DPMO)
- **Sigma 5-6**: Excellent (233 DPMO)
- **Sigma 4-5**: Good (6,210 DPMO)
- **Sigma 3-4**: Marginal (66,807 DPMO)
- **Sigma < 3**: Poor (>66,807 DPMO)

Formula: `Sigma = (TEa - |Bias|) / CV`

### Clinical Significance
- **Creatinine**: Kidney function marker (TEa = 15% per CLIA)
- **Urea**: Kidney function and protein metabolism (TEa = 9% per CLIA)

## 📊 Output Files

The system generates multiple output files:

### Charts (PNG)
- `levey_jennings_*.png` - Control charts with Westgard rules
- `sigma_chart_*.png` - Sigma quality assessment
- `bland_altman_*.png` - Method comparison plots
- `correlation_*.png` - Correlation analysis
- `anova_*.png` - Multi-group comparison

### Data Files (CSV)
- `qc_summary_report.csv` - Summary statistics
- `westgard_violations_*.csv` - Detected rule violations
- `cusum_analysis.csv` - CUSUM results
- `ewma_analysis.csv` - EWMA results

## 🛠️ Technical Requirements

### Dependencies
- Python ≥ 3.9
- NumPy ≥ 1.24.0
- Pandas ≥ 2.0.0
- Matplotlib ≥ 3.7.0
- Seaborn ≥ 0.12.0
- SciPy ≥ 1.10.0
- Plotly ≥ 5.14.0
- Dash ≥ 2.9.0

### System Requirements
- RAM: Minimum 2GB, Recommended 4GB
- Display: Minimum 1280x720, Recommended 1920x1080 or dual monitors
- OS: Windows 10/11, macOS 10.15+, Linux (Ubuntu 20.04+)

## 📖 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Technical Report](TECHNICAL_REPORT.md)**: Detailed system architecture and algorithms
- **[User Guide](docs/USER_GUIDE.md)**: Step-by-step tutorials
- **[API Reference](docs/API_REFERENCE.md)**: Complete API documentation
- **[Quick Start Guide](REALTIME_QUICK_START.md)**: Get started in 5 minutes

## 🧪 Testing

Run validation tests:
```bash
python validate_fix.py
python test_dual_monitor.py
```

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style
- Follow PEP 8 guidelines
- Use type hints where applicable
- Add docstrings to all functions and classes
- Write unit tests for new features

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Westgard QC**: Based on the quality control rules developed by Dr. James O. Westgard
- **CLIA Standards**: Total Allowable Error limits from Clinical Laboratory Improvement Amendments
- **Six Sigma**: Quality methodology adapted from Motorola's Six Sigma framework
- **Clinical Chemistry**: Methods aligned with CLSI (Clinical and Laboratory Standards Institute) guidelines

## 📧 Contact

For questions, suggestions, or collaborations:
- **Issues**: [GitHub Issues](https://github.com/yourusername/QC_sigma_abnormality_detection/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/QC_sigma_abnormality_detection/discussions)

## 🔄 Version History

### Version 1.0.0 (2025-11-11)
- Initial release
- Core QC analysis with Westgard Rules
- Six Sigma metrics implementation
- Real-time monitoring (web and desktop)
- Advanced fault detection methods
- Comprehensive documentation

## 📚 References

1. Westgard, J.O., et al. (1981). "A multi-rule Shewhart chart for quality control in clinical chemistry." *Clinical Chemistry*, 27(3), 493-501.
2. Nevalainen, D., et al. (2000). "Evaluating laboratory performance on quality indicators with the six sigma scale." *Archives of Pathology & Laboratory Medicine*, 124(4), 516-519.
3. CLSI EP28-A3c. (2010). "Defining, establishing, and verifying reference intervals in the clinical laboratory."
4. Bland, J.M., & Altman, D.G. (1986). "Statistical methods for assessing agreement between two methods of clinical measurement." *The Lancet*, 327(8476), 307-310.

## 🌟 Star History

If you find this project useful, please consider giving it a star ⭐!

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/QC_sigma_abnormality_detection&type=Date)](https://star-history.com/#yourusername/QC_sigma_abnormality_detection&Date)

---

**Made with ❤️ for Clinical Laboratory Quality Control**
