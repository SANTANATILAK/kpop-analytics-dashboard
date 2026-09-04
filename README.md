K-Pop Momentum Analytics & Prediction Dashboard

An interactive analytics system that tracks and predicts "momentum" for K-Pop acts using chart performance data, built to surface patterns that raw chart rankings miss.

Problem

Chart position alone doesn't tell you whether an act is gaining or losing momentum, or how well a comeback is holding audience attention over time. This project engineers custom metrics to quantify that.

Approach
Collected and cleaned 10,000+ chart records
Engineered 5 domain-specific metrics, including:
Momentum Spike Score — detects sudden surges in chart activity
Post-Comeback Retention Rate — measures how well an act holds its audience after a release spike
Applied statistical feature engineering and time-series pattern detection to model momentum trends
Built and deployed an interactive dashboard for exploring the results
Tech Stack

Python, Pandas, NumPy, Streamlit, Plotly

Results
Processed 10K+ records into a clean, queryable analytics pipeline
Deployed dashboard with 8+ interactive visualizations
Metrics validated against known comeback events to check for consistency
What I'd Improve Next
Add automated model validation/accuracy monitoring on a rolling basis
Extend metrics to compare momentum across different markets/regions
