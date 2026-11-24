import streamlit as st
from body.agent import run, MODEL
from brain.reasoner import get_build, list_characters

AVATAR = {"assistant": "🌊", "user": "🧑‍🎓"}
CONTOH = [
    "Furina cocok pakai artefak apa dan farm di mana?",
    "Xingqiu cocok pakai artefak apa?",
    "Furina lv 80 stat HP-nya berapa?",
]

st.set_page_config(page_title="Genshin KBS", page_icon="🌊", layout="centered")

def fmt(v):
    # nilai kosong -> "belum ada data"
    if isinstance(v, list):
        return ", ".join(v) if v else "belum ada data"
    return v if v else "belum ada data"

# --- state ---
if "messages" not in st.session_state:
    st.session_state.messages = []  # {role, content, trace}

# --- sidebar: knowledge base ---
with st.sidebar:
    st.header("Knowledge Base")
    chars = list_characters()
    st.caption(f"{len(chars)} karakter: " + ", ".join(chars))

    pilih = st.selectbox("Lihat build karakter", chars)
    if pilih:
        b = get_build(pilih)
        st.markdown(f"**{pilih}**")
        st.write(f"- Elemen: {fmt(b.get('element'))}")
        st.write(f"- Senjata: {fmt(b.get('weapon'))}")
        st.write(f"- Role: {fmt(b.get('roles'))}")
        st.write(f"- Scaling: {fmt(b.get('scales_with'))}")
        st.write(f"- Set artefak: {fmt(b.get('sets'))}")
        st.write(f"- Domain: {fmt(b.get('domains'))}")

    st.divider()
    show_trace = st.toggle("Tampilkan jejak reasoning", value=True)
    st.caption(f"Model: {MODEL}")
    if st.button("Bersihkan chat"):
        st.session_state.messages = []
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

# --- riwayat chat ---
for m in st.session_state.messages:
    with st.chat_message(m["role"], avatar=AVATAR[m["role"]]):
        st.markdown(m["content"])
        if m["role"] == "assistant" and show_trace:
            render_trace(m.get("trace", []))

# --- tombol contoh pertanyaan ---
prompt = None
if not st.session_state.messages:
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
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=AVATAR["user"]):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=AVATAR["assistant"]):
        try:
            # kirim 6 pesan terakhir (teks user/assistant saja) sebagai konteks
            history = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages[:-1]
            ][-6:]
            with st.spinner("Berpikir…"):
                answer, trace = run(prompt, history=history)
            st.markdown(answer)
            if show_trace:
                render_trace(trace)
            st.session_state.messages.append(
                {"role": "assistant", "content": answer, "trace": trace}
            )
        except Exception as e:
            st.error(
                "Ollama belum jalan atau tidak bisa dihubungi. "
                "Cek dengan `ollama ps`.\n\n"
                f"Detail: {e}"
            )
