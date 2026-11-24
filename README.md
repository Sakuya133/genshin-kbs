# Genshin KBS

Knowledge-Based System: ontologi OWL (Owlready2 + HermiT) sebagai otak, LLM lokal
Qwen3 8B via Ollama sebagai antarmuka bahasa. LLM hanya menerjemahkan bahasa —
semua fakta berasal dari ontologi lewat tool-calling.

## Menjalankan UI

Prasyarat:
- Ollama berjalan di `localhost` (cek `ollama ps`).
- Model sudah tersedia: `ollama pull qwen3:8b`.
- Dependency terpasang di venv: `pip install -r requirements.txt`.

Jalankan UI chat Streamlit:

```bash
env -u PYTHONPATH streamlit run app.py
```

Catatan: `env -u PYTHONPATH` dipakai agar PYTHONPATH dari ROS 2 tidak mencemari
environment Streamlit.

Di UI: sidebar menampilkan knowledge base (daftar karakter + build per karakter),
chat menjawab pertanyaan build, dan tiap jawaban punya expander "Jejak reasoning"
berisi tool call beserta hasilnya.

## Test

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q
```
