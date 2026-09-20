import gradio as gr
import yfinance as yf   # Télécharge les données boursières (historique des prix et actualités) via Yahoo Finance
from transformers import pipeline
import plotly.graph_objects as go  # Génère le graphique financier interactif 
import torch

# =====================================================================
# INITIALISATION DE L'IA (FinBERT)
# =====================================================================
print("Chargement de l'IA (FinBERT)...")
try:
    # Utilisation du GPU si disponible pour accélérer l'inférence
    device_id = 0 if torch.cuda.is_available() else -1
    classifier = pipeline("text-classification", model="ProsusAI/finbert", device=device_id)
    print("FinBERT chargé avec succès.")
except Exception as e:
    print(f"❌Erreur de chargement du modèle : {e}")
    exit()

# =====================================================================
# FONCTION DE L'AGENT D'ANALYSE
# =====================================================================
def analyser_sentiment_action(ticker):
    ticker = ticker.strip().upper()
    if not ticker:
        return "⚠️ Veuillez entrer un ticker valide.", go.Figure()
    
    try:
        stock = yf.Ticker(ticker)
        
        # 1. GÉNÉRATION DU GRAPHIQUE INTERACTIF (1 Mois)
        hist = stock.history(period="1mo")
        fig = go.Figure()
        
        if not hist.empty:
            # Création d'un graphique en chandeliers japonais
            fig.add_trace(go.Candlestick(x=hist.index,
                            open=hist['Open'], high=hist['High'],
                            low=hist['Low'], close=hist['Close'],
                            name="Prix"))
            
            fig.update_layout(
                title=f"Historique des prix ({ticker}) - 30 Derniers Jours",
                xaxis_title="Date",
                yaxis_title="Prix",
                template="plotly_dark", # S'intègre bien avec le thème sombre
                margin=dict(l=20, r=20, t=50, b=20),
                xaxis_rangeslider_visible=False 
            )
        else:
            fig.update_layout(title="⚠️ Données de prix indisponibles pour ce ticker.")

        # 2. ANALYSE DES ACTUALITÉS
        raw_news = stock.news
        if not raw_news:
            return f"❌ Aucune actualité récente trouvée pour le ticker : {ticker}.", fig
        
        # Collecte et nettoyage des articles
        articles_valides = []
        for item in raw_news:
            if item is None or len(articles_valides) >= 5:
                continue
                
            titre, lien = None, "#"
            try:
                if isinstance(item, dict):
                    titre = item.get('title') or item.get('content', {}).get('title')
                    lien = item.get('link') or item.get('content', {}).get('clickThroughUrl', {}).get('url') or "#"
                else:
                    titre = getattr(item, 'title', None) or getattr(getattr(item, 'content', None), 'title', None)
                    lien = getattr(item, 'link', None) or getattr(getattr(item, 'content', None), 'url', None) or "#"
                    
                    if not titre and hasattr(item, '__dict__'):
                        d = item.__dict__
                        titre = d.get('title') or d.get('content', {}).get('title')
                        lien = d.get('link') or d.get('content', {}).get('clickThroughUrl', {}).get('url') or "#"
            except Exception as e_extract:
                print(f"Ignoré suite à une erreur d'extraction : {e_extract}")
                continue

            if titre:
                titre_propre = str(titre).strip()
                if len(titre_propre) >= 5:
                    articles_valides.append({"titre": titre_propre, "lien": lien})
        
        if not articles_valides:
            return f"❌ Impossible d'extraire des titres valides pour {ticker}.", fig

        # Inférence NLP en lot
        titres_a_analyser = [art["titre"] for art in articles_valides]
        predictions = classifier(titres_a_analyser)

        # Construction de l'affichage HTML
        total_score = 0
        compte_rendu_html = f"<h3> Dernières actualités analysées :</h3><ul style='list-style-type: none; padding-left: 0;'>"

        for article, pred in zip(articles_valides, predictions):
            label = str(pred['label']).lower()
            confiance = float(pred['score'])
            
            if "pos" in label:
                badge, poids, couleur_bordure = "🟢 HAUSSIER", confiance, "#28a745"
            elif "neg" in label:
                badge, poids, couleur_bordure = "🔴 BAISSIER", -confiance, "#dc3545"
            else:
                badge, poids, couleur_bordure = "🟡 NEUTRE", 0, "#ffc107"
                
            total_score += poids
            
            compte_rendu_html += f"""
            <li style='margin-bottom: 15px; padding: 10px; background-color: #f8f9fa; border-radius: 8px; border-left: 5px solid {couleur_bordure}; color: #333;'>
                <a href='{article["lien"]}' target='_blank' style='text-decoration: none; color: #0056b3; font-weight: bold;'>{article["titre"]}</a><br>
                <span style='font-size: 12px; font-weight: bold;'>Sentiment : {badge} | Confiance : {confiance:.1%}</span>
            </li>
            """
        
        compte_rendu_html += "</ul>"
        
        # Classes evaluation boursière
        sentiment_moyen = total_score / len(articles_valides)
        if sentiment_moyen > 0.20:
            statut_global, couleur_globale = " GLOBALEMENT OPTIMISTE", "#28a745"
        elif sentiment_moyen < -0.20:
            statut_global, couleur_globale = " GLOBALEMENT PESSIMISTE", "#dc3545"
        else:
            statut_global, couleur_globale = " NEUTRE / INDÉCIS", "#ffc107"
            
        signe = "+" if sentiment_moyen > 0 else ""
        conclusion_html = f"""
        <div style='padding: 20px; background-color: {couleur_globale}; color: white; border-radius: 10px; text-align: center; margin-bottom: 20px;'>
            <h2 style='margin: 0;'>Verdict de l'Agent : {statut_global}</h2>
            <p style='margin: 5px 0 0 0;'>Score d'intensité net : {signe}{sentiment_moyen:.1%}</p>
        </div>
        """
        
        return conclusion_html + compte_rendu_html, fig
        
    except Exception as e:
        return f"❌ Une erreur générale est survenue : {str(e)}", go.Figure()

# =====================================================================
#  INTERFACE GRADIO
# =====================================================================
#Liste d'actions populaires dans le déroulant pour faciliter la sélection par l'utilisateur
tickers_populaires = [
    ("TSLA (Tesla)", "TSLA"),
    ("AAPL (Apple)", "AAPL"),
    ("MSFT (Microsoft)", "MSFT"),
    ("NVDA (Nvidia)", "NVDA"),
    ("^GSPC (Indice S&P 500)", "^GSPC"),
    ("CW8.PA (ETF MSCI World)", "CW8.PA"),
    ("AI.PA (Air Liquide)", "AI.PA"),
    ("ENR.DE (Siemens Energy)", "ENR.DE"),
    ("MC.PA (LVMH)", "MC.PA")
]

with gr.Blocks() as demo:
    gr.Markdown("#  Agent d'Analyse Boursière Multimodal")
    
    with gr.Row():
        with gr.Column(scale=1):
            input_ticker = gr.Dropdown(
                choices=tickers_populaires, 
                label="Sélectionnez ou tapez un Code Ticker", 
                allow_custom_value=True, 
                value="TSLA"
            )
            btn_analyser = gr.Button(" Analyser l'Actif", variant="primary")
            
        with gr.Column(scale=2):
            output_plot = gr.Plot(label="Évolution du Marché (1 mois)")
            output_html = gr.HTML(label="Analyse de Sentiment NLP")
            
    btn_analyser.click(fn=analyser_sentiment_action, inputs=input_ticker, outputs=[output_html, output_plot])
    

if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft())