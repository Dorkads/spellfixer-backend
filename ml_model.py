import os, json
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import tokenizer_from_json

BASE = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE, "../spellfixer-ml/model/model.keras")
TOK_PATH   = os.path.join(BASE, "../spellfixer-ml/model/tokenizer/tokenizer.json")
CORR_PATH  = os.path.join(BASE, "corrections.json")
MAX_LEN    = 25

# загрузка один раз при импорте
with open(TOK_PATH, 'r', encoding='utf-8') as f:
    tokenizer = tokenizer_from_json(f.read())
with open(CORR_PATH, 'r', encoding='utf-8') as f:
    corrections = json.load(f)
model = load_model(MODEL_PATH)

def check_word(word: str):
    seq    = tokenizer.texts_to_sequences([word])
    padded = pad_sequences(seq, maxlen=MAX_LEN, padding='post', truncating='post')
    pred   = float(model.predict(padded)[0][0])
    if pred >= 0.5:
        corr = corrections.get(word, "")
        return {"correct": False, "correction": corr}
    return {"correct": True}
