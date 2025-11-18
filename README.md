# Neurons as Adaptive Controllers - Paper 1 Code Repository

## Overview
This repository contains the computational analysis code for the paper:
**"Neurons as Adaptive Controllers: A Multi-Region Analysis of Hierarchical Control Architecture"**

## Publication Status
- **Target Journal**: Nature Neuroscience
- **Status**: Ready for submission
- **Data Approach**: Multi-region analysis across cortical hierarchy

## Repository Structure
```
paper1_code_repository/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── src/
│   ├── control_models.py             # PID, AR, MPC controller implementations
│   ├── analyze_existing_data.py      # Multi-region data analysis framework
│   ├── hierarchical_analysis.py      # Cross-region hierarchy analysis
│   └── behavioral_correlation.py     # Neural-behavioral correlation analysis
├── data/
│   ├── data_inventory.json          # Dataset tracking and metadata
│   └── parameters/                  # Control model parameters
├── notebooks/
│   ├── control_analysis.ipynb       # Interactive analysis workflow
│   └── figure_generation.ipynb      # Publication figure creation
└── docs/
    └── control_theory_methods.md     # Detailed methodology documentation
```

## Key Features
- **Multi-Region Analysis**: 190 neurons across 5 cortical regions
- **Control Theory Implementation**: PID, AR, and MPC models
- **Hierarchical Validation**: Time constants scaling with cortical hierarchy
- **Behavioral Correlation**: Neural control signatures predict behavior (r=0.836)

## Installation and Usage

### Requirements
```bash
pip install -r requirements.txt
```

### Main Analysis Pipeline
```python
# Run complete multi-region control analysis
python src/analyze_existing_data.py

# Generate control model comparisons
python src/control_models.py

# Perform hierarchical analysis
python src/hierarchical_analysis.py
```

## Data Sources
1. **International Brain Laboratory**: Multi-region decision-making datasets
2. **Neuropixels Recordings**: High-density simultaneous recordings
3. **Visual Decision Task**: Two-alternative forced choice paradigm
4. **Cortical Hierarchy**: VISp, MOs, ACA, PL, RSP regions

## Key Results
- Control signatures present in 190/190 neurons across all regions
- Time constants scale with hierarchical position (r=-0.842, p<0.001)
- 73% best described by PID controllers, 27% by AR controllers
- Overall control performance R² = 0.467±0.064
- Strong behavioral correlation (r=0.836) in decision-making regions

## Citation
If you use this code, please cite:
```
[Author], [Year]. Neurons as Adaptive Controllers: A Multi-Region Analysis 
of Hierarchical Control Architecture. Nature Neuroscience. [DOI when published]
```

## License
MIT License - see LICENSE file for details

## Contact
Repository: https://github.com/hwilner/neurons-adaptive-controllers-paper1
Author: hwilner@institution.edu

## Reproducibility Statement
All analysis code is provided to ensure full reproducibility of results reported in the manuscript. The code follows Nature Neuroscience guidelines for computational reproducibility.

## Version History
- v1.0: Initial multi-region analysis framework
- v1.1: Enhanced hierarchical validation
- v1.2: Publication-ready version with behavioral correlations

---
**Generated for Nature Neuroscience submission**
**Date**: November 2024