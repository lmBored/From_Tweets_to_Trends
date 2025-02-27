from transformers import AutoModelForSequenceClassification
from transformers import TFAutoModelForSequenceClassification
from transformers import AutoTokenizer, AutoConfig
import torch
import numpy as np
from scipy.special import softmax
import re
import time

from transformers import logging as transformers_logging
transformers_logging.set_verbosity_error()

MODEL = f"cardiffnlp/twitter-roberta-base-sentiment-latest"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
config = AutoConfig.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL)

device = torch.device('cuda' if torch.cuda.is_available() else 'mps' if torch.backends.mps.is_available() else 'cpu')
model.to(device)

def transform_text(text):
    text = text.lower()  # Normalize case
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)  # Remove URLs
    text = re.sub(r'([A-Za-z])\1{2,}', r'\1\1', text)  # Replace repeated characters
    text = re.sub(r'@\S+', '@user', text)  # Replace user mentions
    text = re.sub(r'#', '', text)  # Optional: Remove the hashtag symbol, keep the word
    text = re.sub(r'[^a-z0-9 ]+', '', text)  # Remove special characters
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra spaces
    return text

def roberta(text, tokenizer, model, configr):
    ptext = transform_text(text)
    
    input = tokenizer(ptext, return_tensors='pt')
    input = input.to(device)
    
    with torch.no_grad():
        output = model(**input)
        
    scores = output[0][0].cpu().detach().numpy()
    scores = softmax(scores)
    
    sentiment_score = scores[2].item() - scores[0].item()
    max_score = np.argmax(scores)
    label = configr.id2label[max_score]
    
    return label, sentiment_score

def roberta1(text, tokenizer, model, configr):
    # start_time = time.time()
    ptext = transform_text(text)
    input = tokenizer(ptext, return_tensors='pt')
    # with torch.no_grad():
    output = model(**input)
    # scores = torch.nn.functional.softmax(output.logits, dim=-1)
    scores = output[0][0].detach().numpy()
    scores = softmax(scores)
    
    # labels = ["negative", "neutral", "positive"]
    # sentiment_mapping = {"negative": -1, "neutral": 0, "positive": 1}
    # sentiment_probabilities = [(labels[i], prob.item()) for i, prob in enumerate(scores[0])]
    sentiment_score = scores[2].item() - scores[0].item()
    # sentiment_score = scores[0][2].item() - scores[0][0].item()
    # sentiment_score = sum(sentiment_mapping[label] * prob.item() for label, prob in zip(labels, score[0]))
    
    max_score = np.argmax(scores)
    label = configr.id2label[max_score]
    
    ranking = np.argsort(scores)
    ranking = ranking[::-1]
    # for i in range(scores.shape[0]):
    #     l = configr.id2label[ranking[i]]
    #     s = scores[ranking[i]]
    #     print(f"{i+1}) {l} {np.round(float(s), 4)}")
    
    # Log-odds
    # odds_pos = score[0][2].item() / (1 - score[0][2].item() + 1e-6)
    # odds_neg = score[0][0].item() / (1 - score[0][0].item() + 1e-6)
    # log_odds_score = np.log(odds_pos) - np.log(odds_neg)
    # normalized_score = 1 / (1 + np.exp(-log_odds_score))
    # print(f"Roberta time taken: {time.time() - start_time}")
    
    return label, sentiment_score
    