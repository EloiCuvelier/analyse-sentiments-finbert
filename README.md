#  Multimodal Stock Market Analysis Agent

##  Background
As I was preparing to make my first stock market investments, I designed this tool to evaluate how Artificial Intelligence (NLP) could help me quickly identify short-term market trends by automatically analyzing financial news.

##  The Project
An interactive web application combining:
* **FinBERT:** Sentiment analysis (NLP) with batch inference (GPU/CUDA optimized) to classify news (Bullish/Bearish/Neutral).
* **Yahoo Finance API:** Real-time extraction of news feeds and historical price data.
* **Plotly & Gradio:** A smooth user interface generating dynamic and interactive Japanese candlestick stock charts.
  <img width="1662" height="637" alt="image" src="https://github.com/user-attachments/assets/96e243d5-abbb-4ef9-97a2-3655abf8461f" />
  <img width="1042" height="557" alt="image" src="https://github.com/user-attachments/assets/275b4962-83f8-4e37-a2e0-a81b56b65d54" />



##  Quick Start
```bash
git clone https://github.com/EloiCuvelier/analyse-sentiments-finbert.git
cd analyse-sentiments-finbert
pip install -r requirements.txt
python robot_bourse.py
```

*Disclaimer: This experimental tool strictly reflects short-term media sentiment and does not replace fundamental financial analysis for long-term investments.*
