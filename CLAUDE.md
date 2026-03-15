# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

- **Run the application**: `streamlit run app.py`
- **Install dependencies**: `uv pip install -e .`
- **Project uses UV package manager** - prefer `uv` commands over `pip`

## Architecture Overview

This is a Streamlit web application for visualizing git repository statistics. The application consists of:

### Core Components

- **`app.py`**: Main Streamlit application with session state management, repository input form, and tabbed visualization interface
- **`gstats/analyzer.py`**: `RepositoryAnalyzer` class that uses GitPython to extract commit data and statistics
- **`gstats/author_normalizer.py`**: Handles author grouping using email as primary key, with name similarity as fallback
- **`gstats/visualizations/`**: Modular visualization classes accessed through the `GitVisualizer` facade

### Key Architecture Patterns

- **Session State Management**: Repository path, analysis results, and settings are stored in Streamlit session state to persist across interactions
- **Email-Based Author Grouping**: Authors are grouped by email first (same email = same person), with name similarity as fallback for different emails
- **Modular Visualizations**: Each chart type is implemented as a separate class with a static `create()` method
- **Lazy Analysis**: Repository analysis only occurs when user submits the form or changes settings

### Data Flow

1. User enters repository path → `RepositoryAnalyzer` loads git repo
2. `get_raw_commit_data()` extracts commits with author names and emails, builds `email_to_names` mapping
3. `apply_author_normalization()` groups authors by email (primary) and name similarity (fallback)
4. `GitVisualizer` methods create Plotly charts from the normalized DataFrame
5. Results cached in session state for performance

### Settings and Configuration

- **Author similarity threshold**: Controls how aggressively similar author names are merged (0.0-1.0)
- **Max lines per commit**: Filters out large commits that might skew visualizations
- Repository analysis automatically re-runs when settings change