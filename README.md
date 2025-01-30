# AI Safety Through Consensus: Bridging Divides in Machines and Society

## Overview
This repository accompanies the project **AI Safety Through Consensus: Bridging Divides in Machines and Society**, which explores a hybrid methodology for AI alignment by combining adversarial debate mechanisms and consensus-building frameworks. The approach integrates insights from Irving et al.'s *AI Safety via Debate* and the structured 7-stage consensus process from Seeds for Change.

## Features
1. **Adversarial Debate Simulation**: Implements a debate-based framework to surface errors and test robustness.
2. **Consensus Framework Protocol**: A 7-stage structured process for building inclusive, win-win AI policies.
3. **Multi-Agent Collaboration**: Models diverse agent ideologies and interactions to reflect real-world stakeholder dynamics.
4. **Metrics and Analysis**: Includes tools for evaluating idea diversity, minority inclusion, and backtrack rates.

## Repository Structure
```
project_root/
├── README.md           # Project overview and instructions
├── requirements.txt    # Python dependencies
├── src/
│   ├── agents/         # AI agent configurations and roles
│   ├── consensus/      # Consensus protocol implementation
│   ├── debate/         # Adversarial debate framework
│   ├── metrics/        # Evaluation metrics and analysis scripts
│   └── utils/          # Shared utilities
├── data/
│   ├── input/          # Input datasets
│   └── output/         # Experiment results
├── tests/              # Unit and integration tests
└── media/              # Visual assets (e.g., diagrams, figures)
```

## Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/ai-safety-consensus.git
   cd ai-safety-consensus
   ```

2. **Set Up the Environment**:
   Create and activate a new Conda environment with Python 3.10:
   ```bash
   conda create -n consensus_env python=3.10 -y
   conda activate consensus_env
   ```

3. **Install Dependencies**:
   Install the required Python packages listed in `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
### Running the Experiment
1. Configure the agents and consensus protocol:
   - Modify YAML configuration files in `src/agents` and `src/consensus` as needed.

2. Start the experiment:
   ```bash
   python src/main.py
   ```

3. View the results:
   Generated outputs (e.g., policy variants, metrics) are saved in the `data/output/` directory.

### Example Outputs
- **Unique Solutions**: JSON array of policy variants with economic impact and feasibility scores.
- **Metrics**: Summary of diversity, inclusion, and backtrack rates.

## Metrics Evaluated
- **Idea Diversity**: Measures the range of unique solutions proposed.
- **Minority Inclusion**: Quantifies the representation of diverse perspectives.
- **Backtrack Rate**: Tracks inefficiencies in reaching consensus.

## References
- Irving, G., Christiano, P., & Amodei, D. (2018). [*AI Safety via Debate*](https://arxiv.org/abs/1805.00899v2). *arXiv:1805.00899.*
- Seeds for Change. [*Consensus Decision Making*](https://www.seedsforchange.org.uk).

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments
Special thanks to:
- The contributors of *AI Safety via Debate* for foundational insights.
- Seeds for Change for inspiring the consensus-building framework.

