import math
import string

import joblib
import streamlit as st

st.set_page_config(page_title="MoodLens", page_icon="\U0001F3AD", layout="wide",
                   initial_sidebar_state="collapsed")

PALETTE = {
    "joy":      ("#F2B53B", "Joy",      "\U0001F604"),
    "sadness":  ("#4C7FD1", "Sadness",  "\U0001F622"),
    "fear":     ("#8B6FD4", "Fear",     "\U0001F628"),
    "anger":    ("#D9534F", "Anger",    "\U0001F620"),
    "love":     ("#E0609B", "Love",     "\U0001F970"),
    "surprise": ("#2FB8A8", "Surprise", "\U0001F632"),
}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Plus+Jakarta+Sans:wght@400;500;600&display=swap');

.stApp {
    background:
      radial-gradient(900px 600px at 82% -8%, #2A1F42 0%, transparent 62%),
      radial-gradient(700px 500px at 8% 104%, #1E2440 0%, transparent 58%),
      #15111E;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2.4rem; padding-bottom: 2rem; max-width: 1080px; }

html, body, [class*="css"], .stMarkdown, p, div, span, label {
    font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
    color: #E8E3F2;
}

.masthead { display:flex; align-items:baseline; gap:.9rem; margin-bottom:.35rem; }
.masthead .mark {
    font-family:'Instrument Serif', Georgia, serif; font-size:2.9rem; line-height:1;
    color:#F6F2FF; letter-spacing:-.5px;
}
.masthead .sub { font-size:.95rem; color:#9A8FB5; }
.rule { height:1px; background:linear-gradient(90deg,#3A3150,transparent); margin:1.4rem 0 1.9rem; }

.panel {
    background:linear-gradient(170deg,#211B30 0%,#1A1526 100%);
    border:1px solid #302846; border-radius:16px; padding:1.4rem 1.5rem;
    box-shadow:0 18px 50px -24px #000000AA;
}

.dial { position:relative; display:flex; justify-content:center; align-items:center; }
.dial .glow {
    position:absolute; width:250px; height:250px; border-radius:50%;
    filter:blur(42px); opacity:.42; pointer-events:none;
}
.dial .face {
    position:absolute; font-size:3.3rem; line-height:1;
    filter:drop-shadow(0 6px 14px #00000066);
}

.stTextArea textarea {
    background:#15111E !important; border:1px solid #332B48 !important;
    border-radius:10px !important; color:#EDE8F7 !important;
    font-family:'Plus Jakarta Sans', sans-serif !important; font-size:.98rem !important;
    line-height:1.65 !important;
}
.stTextArea textarea:focus { border-color:#6E5CA8 !important; box-shadow:0 0 0 3px #6E5CA833 !important; }
.stTextArea textarea::placeholder { color:#6B5F85 !important; }

div.stButton > button {
    border-radius:9px; font-family:'Plus Jakarta Sans', sans-serif;
    transition:background .15s ease, border-color .15s ease;
}
div.stButton > button[kind="primary"] {
    background:#6E5CA8; color:#FFFFFF; border:1px solid #8574C4;
    font-weight:600; font-size:.95rem; padding:.62rem 0;
}
div.stButton > button[kind="primary"]:hover { background:#8574C4; border-color:#9D8DD6; color:#FFFFFF; }
div.stButton > button[kind="secondary"] {
    background:transparent; border:1px solid #332B48; color:#B9AFCF;
    font-weight:400; font-size:.84rem; padding:.52rem .8rem; text-align:left;
}
div.stButton > button[kind="secondary"]:hover { background:#241E33; border-color:#4A3F6B; color:#E8E3F2; }
div.stButton > button:focus-visible { outline:2px solid #C3B5F0; outline-offset:2px; }

.seed { font-size:.86rem; color:#9A8FB5; line-height:1.9; }

.readout { text-align:center; margin-top:.2rem; }
.readout .word {
    font-family:'Instrument Serif', Georgia, serif; font-size:2.5rem; line-height:1.1;
    margin:0;
}
.readout .pct { font-size:.92rem; color:#9A8FB5; margin:.3rem 0 0; }

.legend { margin-top:1.5rem; }
.legend-row { display:flex; align-items:center; gap:.6rem; padding:.34rem 0; font-size:.88rem; }
.legend-row .swatch { width:9px; height:9px; border-radius:2px; flex:none; }
.legend-row .face { font-size:.98rem; line-height:1; flex:none; }
.legend-row .name { flex:1; color:#CFC7E0; }
.legend-row .val { color:#9A8FB5; font-variant-numeric:tabular-nums; }
.legend-row.lead .name, .legend-row.lead .val { color:#F6F2FF; font-weight:600; }

.resting { text-align:center; color:#6B5F85; font-size:.9rem; line-height:1.7; padding:.4rem 1rem 0; }

.colophon {
    margin-top:2.6rem; padding-top:1.3rem; border-top:1px solid #2A2340;
    font-size:.82rem; color:#6B5F85; line-height:1.8;
}
.colophon strong { color:#9A8FB5; font-weight:600; }

@media (prefers-reduced-motion: no-preference) {
  .ring-anim { animation: sweep .6s cubic-bezier(.22,.8,.3,1) both; }
  @keyframes sweep { from { opacity:0; transform:rotate(-16deg) scale(.94); }
                     to   { opacity:1; transform:none; } }

  .dial .face { animation: breathe 3.4s ease-in-out infinite; }
  @keyframes breathe { 0%,100% { transform:translateY(0) scale(1); }
                       50%     { transform:translateY(-5px) scale(1.06); } }

  .dial .glow { animation: pulse 4.2s ease-in-out infinite; }
  @keyframes pulse { 0%,100% { opacity:.3; transform:scale(.94); }
                     50%     { opacity:.5; transform:scale(1.04); } }

  .legend-row { animation: rise .42s ease-out both; }
  .legend-row:nth-child(1){animation-delay:.30s} .legend-row:nth-child(2){animation-delay:.36s}
  .legend-row:nth-child(3){animation-delay:.42s} .legend-row:nth-child(4){animation-delay:.48s}
  .legend-row:nth-child(5){animation-delay:.54s} .legend-row:nth-child(6){animation-delay:.60s}
  @keyframes rise { from { opacity:0; transform:translateY(7px); } to { opacity:1; transform:none; } }

  .readout .word { animation: rise .5s ease-out .18s both; }
}
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_all():
    return (joblib.load("emotion_model.pkl"),
            joblib.load("tfidf_vectorizer.pkl"),
            joblib.load("emotion_labels.pkl"),
            joblib.load("stopwords.pkl"))


model, vectorizer, emotion_num, stop_words = load_all()
num_to_emotion = {v: k for k, v in emotion_num.items()}


def clean_text(text):
    text = text.lower()
    for punc in string.punctuation:
        text = text.replace(punc, "")
    text = "".join(ch for ch in text if not ch.isdigit())
    text = "".join(ch for ch in text if ch.isascii())
    return " ".join(w for w in text.split() if w not in stop_words)


def ring(ranked, resting=False):
    """Donut where each arc length is one emotion's probability."""
    R, W, BOX = 86, 20, 232
    C = 2 * math.pi * R
    cx = cy = BOX / 2
    parts = [f'<svg viewBox="0 0 {BOX} {BOX}" width="{BOX}" height="{BOX}" '
             f'role="img" aria-label="Emotion distribution">'
             f'<g transform="rotate(-90 {cx} {cy})">']

    if resting:
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" '
                     f'stroke="#2A2340" stroke-width="{W}"/>')
    else:
        offset = 0.0
        for name, pct in ranked:
            colour = PALETTE[name][0]
            seg = C * pct / 100
            draw = max(seg - (1.6 if seg > 5 else 0), 0.7)
            parts.append(
                f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{colour}" '
                f'stroke-width="{W}" stroke-dasharray="{draw:.2f} {C - draw:.2f}" '
                f'stroke-dashoffset="{-offset:.2f}" stroke-linecap="butt"/>')
            offset += seg

    parts.append("</g></svg>")
    return "".join(parts)


st.markdown("""
<div class="masthead">
  <span class="mark">MoodLens</span>
  <span class="sub">reads the feeling in a sentence</span>
</div>
<div class="rule"></div>
""", unsafe_allow_html=True)

SEEDS = [
    "i left with my bouquet of red and yellow tulips",
    "i feel rather rotten and low today",
    "i feel terrified of the dark corridor",
    "i just keep feeling like someone is being unkind",
    "i feel loved and cherished every day",
    "i feel stunned by the result",
]

if "seed" not in st.session_state:
    st.session_state.seed = ""

compose, reading = st.columns([1.05, 1], gap="large")

with compose:
    text = st.text_area("Your sentence", height=168, value=st.session_state.seed,
                        placeholder="Write a sentence the way you would say it out loud.",
                        label_visibility="collapsed")
    run = st.button("Read the feeling", type="primary", use_container_width=True)

    st.markdown('<p class="seed" style="margin:1.3rem 0 .5rem;">Or start from one of these</p>',
                unsafe_allow_html=True)
    for i, seed in enumerate(SEEDS):
        if st.button(seed, key=f"seed{i}", use_container_width=True):
            st.session_state.seed = seed
            st.rerun()

with reading:
    cleaned = clean_text(text) if text else ""
    show = run and text.strip() and cleaned

    if show:
        vec = vectorizer.transform([cleaned])
        probs = model.predict_proba(vec)[0]
        ranked = sorted(((num_to_emotion[i], float(p) * 100)
                         for i, p in enumerate(probs)),
                        key=lambda x: x[1], reverse=True)
        top_name, top_pct = ranked[0]
        top_colour, top_label, top_face = PALETTE[top_name]

        legend = "".join(
            f'<div class="legend-row{" lead" if n == top_name else ""}">'
            f'<span class="swatch" style="background:{PALETTE[n][0]};"></span>'
            f'<span class="face">{PALETTE[n][2]}</span>'
            f'<span class="name">{PALETTE[n][1]}</span>'
            f'<span class="val">{p:.1f}%</span></div>'
            for n, p in ranked)

        st.markdown(f"""
        <div class="panel">
          <div class="dial ring-anim">
            <div class="glow" style="background:{top_colour};"></div>
            {ring(ranked)}
            <div class="face">{top_face}</div>
          </div>
          <div class="readout">
            <p class="word" style="color:{top_colour};">{top_label}</p>
            <p class="pct">{top_pct:.0f}% of the model's belief</p>
          </div>
          <div class="legend">{legend}</div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("What the model actually read"):
            st.markdown("Your sentence after lowercasing and stripping punctuation, "
                        "digits, non-ASCII characters and stopwords:")
            st.code(cleaned, language=None)

    else:
        if run and not text.strip():
            message = "Write a sentence first, then read the feeling."
        elif run and not cleaned:
            message = ("Every word in that sentence is a stopword, so nothing "
                       "survived cleaning. Try something longer.")
        else:
            message = ("Six emotions sit on this ring. Write a sentence and each one "
                       "takes the share the model gives it.")
        st.markdown(f"""
        <div class="panel">
          <div class="dial">
            {ring([], resting=True)}
            <div class="face" style="opacity:.28;">\U0001F642</div>
          </div>
          <div class="resting">{message}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("""
<div class="colophon">
  <strong>Soumya Manna</strong> &nbsp;·&nbsp; TF-IDF features into logistic regression,
  trained on 2,000 labelled sentences across six emotions.<br>
  It gets 62% of held-out sentences right, and it is weakest on surprise and love,
  which the training set barely contains. A learning project, not a product.
</div>
""", unsafe_allow_html=True)