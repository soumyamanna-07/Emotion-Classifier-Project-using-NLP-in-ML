"""
Trains the emotion classifier and saves everything the Streamlit app needs.
Run once:   python train.py
"""

import string
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

DATA_FILE = "emotion predic for NLP.txt"

# NLTK's English stopword list, copied from your notebook output (198 words).
# Hardcoded so neither training nor the deployed app needs nltk.download().
STOP_WORDS = set("""
a about above after again against ain all am an and any are aren aren't as at
be because been before being below between both but by
can couldn couldn't d did didn didn't do does doesn doesn't doing don don't down during
each few for from further
had hadn hadn't has hasn hasn't have haven haven't having he he'd he'll he's her here hers
herself him himself his how
i i'd i'll i'm i've if in into is isn isn't it it'd it'll it's its itself just
ll m ma me mightn mightn't more most mustn mustn't my myself
needn needn't no nor not now o of off on once only or other our ours ourselves out over own
re s same shan shan't she she'd she'll she's should should've shouldn shouldn't so some such
t than that that'll the their theirs them themselves then there these they they'd they'll
they're they've this those through to too
under until up ve very was wasn wasn't we we'd we'll we're we've were weren weren't
what when where which while who whom why will with won won't wouldn wouldn't
y you you'd you'll you're you've your yours yourself yourselves
""".split())


def clean_text(text):
    """Same pipeline as the notebook: lower, punctuation, digits, non-ascii, stopwords."""
    text = text.lower()
    for punc in string.punctuation:
        text = text.replace(punc, "")
    text = "".join(ch for ch in text if not ch.isdigit())
    text = "".join(ch for ch in text if ch.isascii())
    return " ".join(w for w in text.split() if w not in STOP_WORDS)


print(f"Stopwords loaded: {len(STOP_WORDS)}")

print("Loading data...")
df = pd.read_csv(DATA_FILE, sep=";", header=None, names=["text", "emotion"])
print(f"  {len(df)} rows, {df['emotion'].nunique()} emotions")

emotion_num = {}
for i, emotion in enumerate(df["emotion"].unique()):
    emotion_num[emotion] = i
df["emotion"] = df["emotion"].map(emotion_num)
print(f"  labels: {emotion_num}")

print("Cleaning text...")
df["text"] = df["text"].apply(clean_text)

X_train, X_test, y_train, y_test = train_test_split(
    df["text"], df["emotion"], test_size=0.33, random_state=42
)
print(f"  train {X_train.shape[0]}, test {X_test.shape[0]}")

print("Vectorising with TF-IDF...")
tfidf_vectorizer = TfidfVectorizer()
X_train_tfidf = tfidf_vectorizer.fit_transform(X_train)
X_test_tfidf = tfidf_vectorizer.transform(X_test)

print("Training Logistic Regression...")
model = LogisticRegression(max_iter=1000)
model.fit(X_train_tfidf, y_train)

pred = model.predict(X_test_tfidf)
acc = accuracy_score(y_test, pred)
print(f"\nTest accuracy: {acc:.4f}   ({acc * 100:.2f}%)\n")
print(classification_report(y_test, pred, zero_division=0))

print("Saving files...")
joblib.dump(model, "emotion_model.pkl")
joblib.dump(tfidf_vectorizer, "tfidf_vectorizer.pkl")
joblib.dump(emotion_num, "emotion_labels.pkl")
joblib.dump(STOP_WORDS, "stopwords.pkl")
for f in ["emotion_model.pkl", "tfidf_vectorizer.pkl",
          "emotion_labels.pkl", "stopwords.pkl"]:
    print(f"  {f}")

print("\nDone. Now run:  python -m streamlit run app.py")