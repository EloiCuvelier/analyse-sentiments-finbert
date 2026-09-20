#  Multimodal Stock Market Analysis Agent

##  Background
As I was preparing to make my first stock market investments, I designed this tool to evaluate how Artificial Intelligence (NLP) could help me quickly identify short-term market trends by automatically analyzing financial news.

##  The Project
An interactive web application combining:
* **FinBERT:** Sentiment analysis (NLP) with batch inference (GPU/CUDA optimized) to classify news (Bullish/Bearish/Neutral).
* **Yahoo Finance API:** Real-time extraction of news feeds and historical price data.
* **Plotly & Gradio:** A smooth user interface generating dynamic and interactive Japanese candlestick stock charts.

##  Quick Start
```bash
git clone https://github.com/EloiCuvelier/analyse-sentiments-finbert.git
cd analyse-sentiments-finbert
pip install -r requirements.txt
python robot_bourse.py
```

*Disclaimer: This experimental tool strictly reflects short-term media sentiment and does not replace fundamental financial analysis for long-term investments.*