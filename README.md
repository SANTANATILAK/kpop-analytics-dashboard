# K-Pop Momentum Analytics Dashboard

A Streamlit-based intelligence dashboard explicitly designed for measuring fandom-driven momentum, chart re-entries, and comeback durability within South Korea's music ecosystem.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip

### 1. Installation

Clone this repository and install the dependencies:

```bash
git clone <your-repo-url>
cd kpop-analytics-dashboard
pip install -r requirements.txt
```

### 2. Generate Synthetic Chart Data

The dashboard relies on standard daily chart movement data. For demonstration purposes, we run a mock data generator that accurately simulates the "sawtooth" chart behaviors found in K-Pop:

```bash
python src/generate_mock_data.py
```
*(This will output a `playlist_history.csv` file into the `/data` folder)*

### 3. Launching the Dashboard

Run the Streamlit app locally:

```bash
streamlit run app.py
```

## 📊 Modules and Architecture

- **`app.py`:** The Streamlit dashboard frontend and interactive Plotly visualizations.
- **`src/data_processing.py`:** The calculation engine parsing raw daily chart numbers into Momentum Spike Scores and Post-Comeback Retention Days.
- **`src/generate_mock_data.py`:** Simulated K-Pop streaming data representing single vs. album release cycles.
- **`docs/`:** Strategic executive summaries and research methodology intended for Atlantic's A&R data teams.
