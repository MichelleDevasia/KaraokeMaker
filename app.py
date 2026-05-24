import streamlit as st
import os
import subprocess
import sys
import scraper
import metadata
import time

# --- Page Config & Theme ---
st.set_page_config(page_title="VibeSync AI Studio", layout="wide", initial_sidebar_state="collapsed")

# --- Custom Sophisticated CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500&display=swap');
    .stApp { background: linear-gradient(180deg, #010411, #0a1f44, #0d3b66); color: white; font-family: 'Poppins', sans-serif; }
    .glass-card { background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(15px); border-radius: 15px; padding: 30px; border: 1px solid rgba(135, 206, 235, 0.15); margin-bottom: 20px; transition: 0.3s; }
    .main-title { font-size: 64px; font-weight: 300; background: -webkit-linear-gradient(#add8e6, #87ceeb, #c3f2ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 0px; letter-spacing: -1.5px; }
    .stButton>button { background: linear-gradient(135deg, #add8e6, #87ceeb); color: #010411 !important; font-weight: 500 !important; border-radius: 50px !important; border: none !important; padding: 12px 28px !important; width: 100%; transition: 0.3s all ease; text-transform: uppercase; letter-spacing: 1px; font-size: 14px; }
</style>
""", unsafe_allow_html=True)

# --- Navigation State ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'

def go_to(page_name):
    st.session_state.page = page_name

# --- 1. HOME PAGE ---
if st.session_state.page == 'home':
    st.markdown("<h1 class='main-title'>VibeSync AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 20px;'>The Future of Interactive Music Engineering</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown("<div class='glass-card'><h3>🎹 Pitch Analysis</h3><p>Extracting musical scales using Chromagram technology.</p></div>", unsafe_allow_html=True)
    with col2: st.markdown("<div class='glass-card'><h3>🎤 AI Karaoke</h3><p>Using Spleeter neural networks to separate vocals.</p></div>", unsafe_allow_html=True)
    with col3: st.markdown("<div class='glass-card'><h3>👤 Artist Insights</h3><p>Mining Wikipedia and Genius metadata.</p></div>", unsafe_allow_html=True)
    
    if st.button("Enter the Studio", use_container_width=True): go_to('generator')

# --- 2. GENERATOR PANEL ---
elif st.session_state.page == 'generator':
    st.markdown("## 🛠 Music Extraction Engine")
    if st.button("← Back to Home"): go_to('home')
    if st.button("Go to Library 📚"): go_to('library')
    
    query = st.text_input("Enter Song Name or YouTube Link:", placeholder="e.g. Madhu Pakaroo...")
    
    if st.button("✨ Start AI Transformation", use_container_width=True):
        if query:
            with st.status("Analyzing and Processing...", expanded=True) as s:
                data = scraper.download_audio(query)
                if data["mp3"]:
                    # 1. AI Spleeter Separation (Run this FIRST so Whisper has a file to hear)
                    subprocess.run([sys.executable, "processor.py", data['mp3']])
                    
                    # 2. Fetch Metadata (With the new vocal path fallback)
                    v_path = f"karaoke_output/{data['title']}/vocals.wav"
                    meta = metadata.get_lyrics_and_metadata(data['title'], v_path)
                    
                    singer = meta['singer'] if meta else data['artist']
                    composer = meta['composer'] if meta else "Unknown Composer"
                    source = meta['source'] if meta else "Scraper Only"
                    
                    # 3. Save Info (Added source to the save file)
                    with open(f"library/{data['title']}.info", "w", encoding="utf-8") as f:
                        f.write(f"{singer}|{composer}|{source}")
                    
                    # 4. Save Lyrics
                    lyric_text = meta['lyrics'] if meta else "Lyrics not found."
                    with open(f"library/{data['title']}.txt", "w", encoding="utf-8") as f:
                        f.write(lyric_text)
                    
                    s.update(label="✅ Extraction Successful!", state="complete")
                    time.sleep(2)
                    go_to('library')

# --- 3. LIBRARY GALLERY ---
elif st.session_state.page == 'library':
    st.markdown("## 📚 Your AI Collection")
    if st.button("← Extraction Panel"): go_to('generator')
    songs = [f for f in os.listdir("library") if f.endswith(".mp3")]
    
    if not songs:
        st.warning("Your library is empty.")
    else:
        cols = st.columns(3)
        for idx, song_file in enumerate(songs):
            name = os.path.splitext(song_file)[0]
            with cols[idx % 3]:
                st.markdown(f"<div class='glass-card'><h4>{name}</h4></div>", unsafe_allow_html=True)
                if st.button(f"Open Studio: {name}", key=name):
                    st.session_state.active_song = song_file
                    go_to('studio')

# --- 4. THE PERFORMANCE STUDIO ---
elif st.session_state.page == 'studio':
    song_file = st.session_state.active_song
    name = os.path.splitext(song_file)[0]
    if st.button("← Back to Library"): go_to('library')
    
    singer, composer, source = "Unknown", "Unknown", "Genius"
    if os.path.exists(f"library/{name}.info"):
        with open(f"library/{name}.info", "r", encoding="utf-8") as f:
            parts = f.read().split("|")
            singer = parts[0]
            composer = parts[1]
            if len(parts) > 2: source = parts[2]
    
    st.markdown(f"<h1 style='text-align: center;'>{name}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'><b>Singer:</b> {singer} | <b>Composer:</b> {composer}</p>", unsafe_allow_html=True)
    
    t1, t2, t3 = st.tabs(["🎧 Players", "📜 Static Lyrics", "👤 Artist Bios"])
    
    with t1:
        col_a, col_b = st.columns(2)
        with col_a:
            st.write("Original Audio")
            st.audio(f"library/{song_file}")
        with col_b:
            k_path = f"karaoke_output/{name}/accompaniment.wav"
            if os.path.exists(k_path):
                st.write("Instrumental Track")
                st.audio(k_path)
    
    with t2:
        st.caption(f"Lyric Source: {source}") # Shows if Genius or AI transcribed it
        l_path = f"library/{name}.txt"
        if os.path.exists(l_path):
            with open(l_path, "r", encoding="utf-8") as f:
                content = f.read()
            st.text_area("", value=content, height=400)
            
    with t3:
        st.markdown("### Meet the Artists")
        st.markdown(f"**Singer ({singer}):** {metadata.get_artist_info(singer)}")
        st.divider()
        st.markdown(f"**Composer ({composer}):** {metadata.get_artist_info(composer)}")