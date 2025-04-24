# Git Stats Visualizer

A simple tool to visualize git repository statistics using Streamlit.

## Features

- Basic repository statistics (total commits, unique authors, first commit date)
- Commit timeline visualization
- Author contribution analysis
- Interactive plots using Plotly

## Installation

1. Clone this repository
2. Install UV (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
3. Install the required dependencies:
   ```bash
   uv pip install -e .
   ```

## Usage

1. Run the application:
   ```bash
   streamlit run app.py
   ```
2. Enter the path to your git repository in the sidebar
3. Click "Analyze Repository" to view the statistics

## Requirements

- Python 3.8+
- UV package manager
- GitPython
- Streamlit
- Pandas
- Plotly
- Python-dateutil

## License

MIT
