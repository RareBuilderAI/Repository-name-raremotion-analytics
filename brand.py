"""Shared Raremotion Labs presentation; analytics and auth stay in their modules."""

import streamlit as st


def apply_brand():
    st.markdown('''
<style>
.stApp { background: #070b16; color: #f5f7fb; }
[data-testid="stHeader"] { background: #070b16; }
[data-testid="stMainBlockContainer"] { max-width: 1240px; padding-top: 5rem; }
.rm-nav { display:flex; justify-content:space-between; align-items:center;
  gap:1rem; padding:0 0 2.5rem; border-bottom:1px solid #202a3c; margin-bottom:3rem; }
.rm-brand { color:#f5f7fb; font-size:1rem; font-weight:750; letter-spacing:.02em; }
.rm-brand span { color:#19b5e8; }
.rm-nav a { color:#a7b0c3; text-decoration:none; font-size:.9rem; }
.rm-nav a:hover { color:#19b5e8; }
.rm-eyebrow { color:#19b5e8; font-size:.75rem; letter-spacing:.18em; font-weight:700; margin-bottom:1rem; }
.rm-hero h1 { font-size:clamp(2.5rem, 5.5vw, 5rem); line-height:1.06;
  letter-spacing:-.055em; font-weight:800; margin:0; padding:0; color:#f5f7fb; }
.rm-hero h1 span { color:#a7b0c3; }
.rm-hero p { max-width:650px; font-size:1.1rem; line-height:1.65; color:#a7b0c3; margin:1.5rem 0 2rem; }
h2 { letter-spacing:-.035em; margin-top:1.5rem; }
h3 { letter-spacing:-.02em; }
[data-testid="stMetric"] { background:#101827; border:1px solid #253047; border-radius:14px; padding:1.1rem; }
[data-testid="stMetricLabel"] { color:#a7b0c3; }
[data-testid="stMetricValue"] { color:#f5f7fb; }
[data-testid="stFileUploaderDropzone"] { background:#101827; border:1px dashed #354760; border-radius:14px; }
[data-testid="stExpander"] { background:#0d1422; border-radius:12px; }
[data-testid="stButton"] button { border-radius:9px; min-height:2.8rem; font-weight:650; }
[data-testid="stButton"] button[kind="primary"] { background:#19b5e8; color:#06111a; border:1px solid #19b5e8; }
[data-testid="stButton"] button[kind="primary"]:hover { background:#64d5f5; border-color:#64d5f5; }
[data-testid="stButton"] button:focus-visible, a:focus-visible { outline:3px solid #8ce3fa; outline-offset:3px; }
[data-testid="stTabs"] { margin-top:1rem; }
@media (max-width:640px) {
  [data-testid="stMainBlockContainer"] { padding:4.5rem 1rem; }
  .rm-nav { margin-bottom:2rem; padding-bottom:1.5rem; }
  .rm-hero p { font-size:1rem; }
}
</style>
<nav class="rm-nav" aria-label="Raremotion">
  <div class="rm-brand"><span>◉</span> Raremotion Labs</div>
  <a href="https://raremotion-labs.vercel.app/index.html" target="_blank" rel="noopener noreferrer">Visit the Lab ↗</a>
</nav>
''', unsafe_allow_html=True)


def show_intro(*, login=False):
    if login:
        title = 'Your data.<br><span>A clearer picture.</span>'
        description = 'Understand your business with Raremotion Analytics. Sign in to explore your data, uncover patterns, and ask better questions.'
    else:
        title = 'Business data.<br><span>Useful intelligence.</span>'
        description = 'Turn your CSV into a clear view of performance, practical insights, and answers about your business.'
    # All markup is static application copy, never uploaded or account content.
    st.markdown(f'''<section class="rm-hero">
<div class="rm-eyebrow">RAREMOTION ANALYTICS</div>
<h1>{title}</h1><p>{description}</p></section>''', unsafe_allow_html=True)
