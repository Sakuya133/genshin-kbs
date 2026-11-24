import threading
import streamlit as st
from body.agent import run, MODEL

AVATAR = {"assistant": "🌊", "user": "🧑‍🎓"}
CONTOH = [
    "Furina cocok pakai artefak apa dan farm di mana?",
    "Xingqiu cocok pakai artefak apa?",
    "Furina lv 80 stat HP-nya berapa?",
]
MAX_CHATS = 10  # maksimal jumlah chat (pertanyaan) yang disimpan — berlaku global semua guest

st.set_page_config(page_title="Genshin KBS", page_icon="🌊", layout="centered")

@st.cache_resource
def get_store():
    # state bersama lintas semua sesi/guest (satu proses Streamlit); semua guest dihitung sama
    return {"messages": [], "lock": threading.Lock()}

store = get_store()
messages = store["messages"]  # list {role, content, trace}

def jumlah_chat():
    return sum(1 for m in messages if m["role"] == "user")

def tambah_pesan(role, content, trace=None):
    with store["lock"]:
        messages.append({"role": role, "content": content, "trace": trace or []})
        # buang chat terlama bila melebihi batas (1 chat = 1 pertanyaan + jawabannya)
        while jumlah_chat() > MAX_CHATS:
            del messages[0]  # pertanyaan terlama
            while messages and messages[0]["role"] == "assistant":
                del messages[0]  # jawaban yang mengikutinya

# --- sidebar: riwayat (global) ---
with st.sidebar:
    st.header("Riwayat")
    st.caption(f"{jumlah_chat()}/{MAX_CHATS} chat · dibagikan ke semua guest")
    riwayat = [m["content"] for m in messages if m["role"] == "user"]
    if not riwayat:
        st.caption("Belum ada percakapan.")
    else:
        for i, teks in enumerate(riwayat, 1):
            ringkas = teks if len(teks) <= 60 else teks[:57] + "…"
            st.write(f"{i}. {ringkas}")

    st.divider()
    show_trace = st.toggle("Tampilkan jejak reasoning", value=True)
    st.caption(f"Model: {MODEL}")
    if st.button("Bersihkan chat"):
        with store["lock"]:
            messages.clear()
        st.rerun()

# --- header ---
st.title("🌊 Genshin Build Assistant")
st.caption(
    "LLM hanya antarmuka bahasa — semua pengetahuan berasal dari ontologi (knowledge base)."
)

def render_trace(trace):
    with st.expander("Jejak reasoning"):
        if not trace:
            st.caption("Tidak ada tool yang dipanggil.")
        for t in trace:
            st.code(f"{t['tool']}({t['args']})", language="python")
            st.json(t["result"])

# --- tampilkan riwayat chat ---
for m in messages:
    with st.chat_message(m["role"], avatar=AVATAR[m["role"]]):
        st.markdown(m["content"])
        if m["role"] == "assistant" and show_trace:
            render_trace(m.get("trace", []))

# --- tombol contoh pertanyaan ---
prompt = None
if not messages:
    st.write("Coba contoh pertanyaan:")
    cols = st.columns(len(CONTOH))
    for c, q in zip(cols, CONTOH):
        if c.button(q):
            prompt = q

# --- input chat ---
typed = st.chat_input("Tanya soal build karakter…")
if typed:
    prompt = typed

if prompt:
    # konteks LLM: 6 pesan terakhir SEBELUM pertanyaan ini
    history = [{"role": m["role"], "content": m["content"]} for m in messages][-6:]
    tambah_pesan("user", prompt)
    with st.chat_message("user", avatar=AVATAR["user"]):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=AVATAR["assistant"]):
        try:
            with st.spinner("Berpikir…"):
                answer, trace = run(prompt, history=history)
            st.markdown(answer)
            if show_trace:
                render_trace(trace)
            tambah_pesan("assistant", answer, trace)
        except Exception as e:
            st.error(
                "Ollama belum jalan atau tidak bisa dihubungi. "
                "Cek dengan `ollama ps`.\n\n"
                f"Detail: {e}"
            )
