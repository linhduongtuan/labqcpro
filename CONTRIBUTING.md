# Contributing to QC Sigma Abnormality Detection

First off, thank you for considering contributing to this project! 🎉

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

**Bug Report Template:**
```markdown
**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Run command '...'
2. With parameters '...'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots/Output**
If applicable, add screenshots or console output.

**Environment:**
 - OS: [e.g., macOS 13.0, Windows 11, Ubuntu 22.04]
 - Python version: [e.g., 3.9.7]
 - Package versions: [run `pip list`]

**Additional context**
Add any other context about the problem.
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. Create an issue and provide:

- **Clear title** describing the enhancement
- **Detailed description** of the proposed functionality
- **Use case** explaining why this would be useful
- **Example code** showing how it might work
- **Alternatives considered** if any

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following our coding standards
3. **Add tests** for new functionality
4. **Update documentation** as needed
5. **Ensure tests pass** before submitting
6. **Submit a pull request**

## Development Setup

### Prerequisites
- Python 3.9 or higher
- Git
- Virtual environment tool (venv, conda, or uv)

### Setup Instructions

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/QC_sigma_abnormality_detection.git
cd QC_sigma_abnormality_detection

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest black flake8 mypy

# Run tests
pytest tests/
```

## Coding Standards

### Python Style Guide

We follow **PEP 8** with some modifications:

- **Line length**: 100 characters (not 79)
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Single quotes for strings, double quotes for docstrings
- **Imports**: Grouped and sorted (stdlib, third-party, local)

### Code Formatting

Use **Black** for automatic formatting:
```bash
black lab_qc_analysis.py
```

### Linting

Use **flake8** for code quality:
```bash
flake8 --max-line-length=100 --ignore=E203,W503 *.py
```

### Type Hints

Add type hints to all new functions:
```python
def calculate_sigma(tea: float, bias: float, cv: float) -> float:
    """
    Calculate Six Sigma metric.
    
    Parameters
    ----------
    tea : float
        Total Allowable Error (%)
    bias : float
        Systematic bias (%)
    cv : float
        Coefficient of Variation (%)
    
    Returns
    -------
    float
        Sigma value
    """
    return (tea - abs(bias)) / cv
```

### Documentation

#### Docstrings

Use **NumPy style** docstrings:

```python
def apply_westgard_rules(qc_data: pd.DataFrame, analyte: str) -> pd.DataFrame:
    """
    Apply Westgard multi-rule quality control.
    
    Implements the following rules:
    - 1-2s: Warning (one control exceeds ±2 SD)
    - 1-3s: Random error (one control exceeds ±3 SD)
    - 2-2s: Systematic error (two consecutive exceed ±2 SD same side)
    - R-4s: Random error (range exceeds 4 SD)
    - 4-1s: Systematic shift (four consecutive exceed ±1 SD same side)
    - 10-x: Systematic shift (ten consecutive on same side of mean)
    
    Parameters
    ----------
    qc_data : pd.DataFrame
        QC measurements with columns ['run', 'datetime', 'value']
    analyte : str
        Analyte name ('creatinine' or 'urea')
    
    Returns
    -------
    pd.DataFrame
        Violations with columns ['run', 'rule', 'description', 'action']
    
    Examples
    --------
    >>> qc = LabQCAnalysis()
    >>> data = qc.generate_qc_data('creatinine', n_days=30)
    >>> violations = qc.apply_westgard_rules(data, 'creatinine')
    >>> print(violations)
    """
    pass
```

#### Comments

- Use comments for complex logic only
- Avoid obvious comments
- Explain *why*, not *what*

**Good:**
```python
# Apply robust scaling to handle outliers
z_scores = 0.6745 * (values - median) / mad
```

**Bad:**
```python
# Calculate z scores
z_scores = (values - mean) / std
```

### Testing

#### Unit Tests

Write tests for all new functions using **pytest**:

```python
# test_qc_analysis.py
import pytest
import numpy as np
from lab_qc_analysis import LabQCAnalysis

def test_sigma_calculation():
    """Test Six Sigma calculation with known values."""
    qc = LabQCAnalysis(seed=42)
    
    # Known case: TEa=15%, Bias=1%, CV=5% → Sigma=2.8
    sigma = qc.calculate_sigma(tea=15.0, bias=1.0, cv=5.0)
    assert abs(sigma - 2.8) < 0.01

def test_westgard_1_3s_rule():
    """Test 1-3s rule detects outliers."""
    qc = LabQCAnalysis(seed=42)
    
    # Create data with clear 3-sigma violation
    data = pd.DataFrame({
        'run': [1, 2, 3],
        'value': [1.0, 1.0, 1.0 + 3.5*0.05]  # 3.5 SD above mean
    })
    
    violations = qc.apply_westgard_rules(data, 'creatinine')
    assert '1-3s' in violations['rule'].values

@pytest.fixture
def sample_qc_data():
    """Fixture providing sample QC data."""
    qc = LabQCAnalysis(seed=42)
    return qc.generate_qc_data('creatinine', n_days=30)
```

Run tests:
```bash
pytest tests/ -v
pytest tests/ --cov=lab_qc_analysis  # with coverage
```

#### Integration Tests

Test complete workflows:
```python
def test_full_analysis_pipeline():
    """Test complete QC analysis from data to report."""
    qc = LabQCAnalysis(seed=42)
    
    # Generate data
    data = qc.generate_qc_data('creatinine', n_days=30)
    assert len(data) == 90
    
    # Analyze
    fig, stats = qc.plot_levey_jennings(data, 'creatinine')
    assert 'mean' in stats
    assert 'sigma' in stats
    
    # Check violations
    violations = qc.apply_westgard_rules(data, 'creatinine')
    assert isinstance(violations, pd.DataFrame)
```

## Commit Messages

Follow **Conventional Commits** specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, missing semicolons, etc.
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

**Examples:**
```
feat(westgard): add 2-3s rule implementation

Implement the 2-3s Westgard rule for detecting moderate
systematic errors. This rule triggers when 2 out of 3
consecutive controls exceed ±2 SD.

Closes #42
```

```
fix(sigma): correct bias calculation in sigma metrics

Fixed incorrect absolute value handling in bias calculation
that caused negative sigma values in some edge cases.

Fixes #58
```

## Pull Request Process

### Before Submitting

1. **Update documentation**
   - README.md if adding features
   - Docstrings for new functions
   - TECHNICAL_REPORT.md for algorithms

2. **Add tests**
   - Unit tests for new functions
   - Integration tests for workflows
   - Aim for >80% code coverage

3. **Run quality checks**
   ```bash
   black *.py
   flake8 --max-line-length=100 *.py
   mypy --ignore-missing-imports *.py
   pytest tests/ -v
   ```

4. **Update CHANGELOG.md**
   ```markdown
   ## [Unreleased]
   ### Added
   - New 2-3s Westgard rule implementation (#42)
   
   ### Fixed
   - Sigma calculation bias handling (#58)
   ```

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed
- [ ] All tests pass locally

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added and pass
- [ ] CHANGELOG.md updated

## Screenshots (if applicable)
Add screenshots for UI changes

## Related Issues
Closes #(issue number)
```

### Review Process

1. Maintainers will review your PR
2. Address feedback and update PR
3. Once approved, maintainer will merge
4. Your contribution will be in the next release! 🎉

## Project Structure

```
QC_sigma_abnormality_detection/
├── src/                          # Source code (future organization)
│   ├── core/                     # Core QC logic
│   ├── detectors/                # Detection algorithms
│   ├── visualization/            # Plotting functions
│   └── utils/                    # Utilities
├── tests/                        # Test files
│   ├── test_qc_analysis.py
│   ├── test_westgard_rules.py
│   └── test_sigma_metrics.py
├── docs/                         # Documentation
├── examples/                     # Example scripts
├── data/                         # Sample data
└── results/                      # Output directory
```

## Adding New Features

### New Westgard Rule

1. Add to `apply_westgard_rules` method
2. Include in documentation
3. Add unit test
4. Update rule summary

Example:
```python
def check_2_3s_rule(self, z_scores):
    """Check 2 out of 3 consecutive controls exceed ±2 SD."""
    violations = []
    for i in range(len(z_scores) - 2):
        window = z_scores[i:i+3]
        positive = sum(z > 2.0 for z in window)
        negative = sum(z < -2.0 for z in window)
        
        if positive >= 2 or negative >= 2:
            violations.append({
                'run': i + 2,
                'rule': '2-3s',
                'description': '2 out of 3 controls exceed ±2 SD',
                'action': 'WARNING - Investigate'
            })
    return violations
```

### New Statistical Test

1. Create function in `LabQCAnalysis` class
2. Add mathematical documentation
3. Include example usage
4. Add to demo script

Example:
```python
def kruskal_wallis_test(self, groups: List[np.ndarray]) -> dict:
    """
    Perform Kruskal-Wallis H-test (non-parametric ANOVA).
    
    Parameters
    ----------
    groups : List[np.ndarray]
        List of sample groups
    
    Returns
    -------
    dict
        Test statistics and p-value
    """
    from scipy.stats import kruskal
    
    h_stat, p_value = kruskal(*groups)
    
    return {
        'h_statistic': h_stat,
        'p_value': p_value,
        'significant': p_value < 0.05,
        'test_name': 'Kruskal-Wallis H'
    }
```

## Questions?

- **Open an issue**: For bugs or feature requests
- **Start a discussion**: For questions or ideas
- **Email**: For private inquiries

## Code of Conduct

### Our Pledge

We are committed to making participation in our project a harassment-free experience for everyone.

### Our Standards

**Positive behavior:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community

**Unacceptable behavior:**
- Trolling, insulting/derogatory comments, personal attacks
- Public or private harassment
- Publishing others' private information
- Other conduct reasonably considered inappropriate

### Enforcement

Project maintainers have the right to remove, edit, or reject comments, commits, code, issues, and other contributions not aligned with this Code of Conduct.

## Recognition

Contributors will be recognized in:
- README.md Contributors section
- CHANGELOG.md release notes
- GitHub Contributors page

Thank you for contributing! 🙏

---

**Happy Coding!** 💻🔬
