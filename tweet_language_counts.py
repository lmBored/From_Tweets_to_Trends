tweet_counts = {
    'ja': 86808,
    'en': 4730503,
    'de': 112543,
    'es': 418188,
    'fr': 280887,
    'in': 37142,
    'nl': 206641,
    'it': 67304,
    'und': 193254,
    'th': 58491,
    'pt': 49617,
    'ru': 19184,
    'hi': 4964,
    'cs': 3750,
    'ko': 68227,
    'et': 4035,
    'no': 6143,
    'da': 4564,
    'ca': 22707,
    'sv': 4104,
    'ro': 4788,
    'fa': 4906,
    'pl': 25348,
    'tr': 26614,
    'hu': 2894,
    'el': 9412,
    'fi': 3199,
    'ht': 4743,
    'uk': 4801,
    'tl': 6666,
    'ur': 2120,
    'ar': 23465,
    'zh': 1870,
    'lt': 1121,
    'cy': 1920,
    'iw': 890,
    'lv': 1758,
    'sl': 2617,
    'eu': 692,
    'is': 477,
    'ml': 175,
    'bg': 462,
    'vi': 242,
    'sr': 114,
    'ta': 183,
    'ps': 3,
    'ka': 61,
    'mr': 40,
    'ne': 126,
    'hy': 152,
    'pa': 9,
    'kn': 70,
    'te': 68,
    'gu': 15,
    'bn': 17,
    'or': 2,
    'am': 18,
    'my': 9,
    'dv': 8,
    'si': 5,
    'sd': 3,
    'ckb': 6,
    'lo': 1
}

total_tweets = sum(tweet_counts.values())

percentages = {lang: (count / total_tweets) * 100 for lang, count in tweet_counts.items()}

sorted_percentages = sorted(percentages.items(), key=lambda x: x[1], reverse=True)

for lang, percentage in sorted_percentages:
    print(f"{lang}: {percentage:.2f}%")

print({k: v for k, v in sorted_percentages.items() if v > 1})
