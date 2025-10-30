# content_analyzer.py
# Author: Nicole Chong (8950465)
# Description: Uses Hugging Face models to analyze article text for sentiment and toxicity
# to support AI-based content moderation in EchoPress.

from transformers import pipeline

# Lazy-load models
_sentiment_analyzer = None
_toxicity_detector = None

def get_sentiment_analyzer():
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        _sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="distilbert/distilbert-base-uncased-finetuned-sst-2-english",
            device=-1  # CPU only
        )
    return _sentiment_analyzer

def get_toxicity_detector():
    global _toxicity_detector
    if _toxicity_detector is None:
        _toxicity_detector = pipeline(
            "text-classification",
            model="unitary/toxic-bert",
            device=-1  # CPU only
        )
    return _toxicity_detector


def analyze_content(article_text):
    text = article_text[:512]

    sentiment = get_sentiment_analyzer()(text)[0]
    toxicity = get_toxicity_detector()(text)[0]

    sentiment_label = sentiment['label']
    toxicity_label = toxicity['label']
    toxicity_score = toxicity['score']

    if toxicity_label == "toxic" and toxicity_score > 0.7:
        return {"status": "BLOCKED", "reason": "Toxic or inappropriate content detected."}
    elif sentiment_label == "NEGATIVE" and toxicity_score > 0.5:
        return {"status": "FLAGGED", "reason": "Negative tone; requires moderator review."}
    else:
        return {"status": "SAFE", "reason": "No issues detected."}
