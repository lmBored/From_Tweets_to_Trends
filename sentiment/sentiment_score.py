from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np
from scipy.special import softmax
import re
# import time

tokenizer = AutoTokenizer.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment-latest")
model = AutoModelForSequenceClassification.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment-latest")

def transform_text(text):
    text = re.sub(r'([A-Za-z])\1{2,}', r'\1', text) # replace repeated texts, normalization
    text = re.sub(r'[^A-Za-z ]', '', text) # remove special characters
    text = re.sub(r'@\S+', '@user', text) # replace user mentions
    return text

def roberta(text):
    # start_time = time.time()
    ptext = transform_text(text)
    input = tokenizer(ptext, return_tensors='pt')
    with torch.no_grad():
        output = model(**input)
    score = torch.nn.functional.softmax(output.logits, dim=-1)
    
    # labels = ["negative", "neutral", "positive"]
    # sentiment_mapping = {"negative": -1, "neutral": 0, "positive": 1}
    # sentiment_probabilities = [(labels[i], prob.item()) for i, prob in enumerate(score[0])]
    sentiment_score = score[0][2].item() - score[0][0].item()
    # sentiment_score = sum(sentiment_mapping[label] * prob.item() for label, prob in zip(labels, score[0]))
    
    # Log-odds
    # odds_pos = score[0][2].item() / (1 - score[0][2].item() + 1e-6)
    # odds_neg = score[0][0].item() / (1 - score[0][0].item() + 1e-6)
    # log_odds_score = np.log(odds_pos) - np.log(odds_neg)
    # normalized_score = 1 / (1 + np.exp(-log_odds_score))
    # print(f"Roberta time taken: {time.time() - start_time}")
    
    return sentiment_score