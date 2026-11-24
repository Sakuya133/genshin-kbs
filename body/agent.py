import json
import ollama
from rapidfuzz import process
from brain.reasoner import get_build, list_characters

MODEL = "qwen3:8b"
SYSTEM = (
    "Kamu asisten analisis build Genshin Impact. "
    "SEMUA fakta harus berasal dari hasil tool. "
    "Jika tool mengembalikan error atau data kosong, katakan data belum tersedia. "
    "Dilarang menyebut angka, set artefak, atau domain yang tidak ada di hasil tool. "
    "Jawab singkat dalam bahasa Indonesia."
)

def tool_get_build(char: str) -> dict:
    m = process.extractOne(char, list_characters(), score_cutoff=70)
    if not m:
        return {"error": "unknown_character", "name": char, "available": list_characters()}
    return get_build(m[0])

TOOLS = [{
    "type": "function",
    "function": {
        "name": "get_build",
        "description": "Ambil role, set artefak, dan domain rekomendasi satu karakter dari knowledge base.",
        "parameters": {
            "type": "object",
            "properties": {"char": {"type": "string", "description": "nama karakter"}},
            "required": ["char"],
        },
    },
}]
FUNCS = {"get_build": tool_get_build}

def run(q: str, history=None):
    # history: list pesan {role, content} (teks user/assistant), dibatasi pemanggil
    msgs = [{"role": "system", "content": SYSTEM}]
    if history:
        msgs += [{"role": m["role"], "content": m["content"]} for m in history]
    msgs.append({"role": "user", "content": q})
    trace = []
    for _ in range(5):  # batas langkah, cegah loop tak berujung
        r = ollama.chat(model=MODEL, messages=msgs, tools=TOOLS, think=False)
        msgs.append(r.message)
        if not r.message.tool_calls:
            return r.message.content, trace
        for tc in r.message.tool_calls:
            fn = FUNCS.get(tc.function.name)
            args = dict(tc.function.arguments)
            out = fn(**args) if fn else {"error": "unknown_tool"}
            trace.append({"tool": tc.function.name, "args": args, "result": out})
            msgs.append({"role": "tool", "tool_name": tc.function.name,
                         "content": json.dumps(out, ensure_ascii=False)})
    return "Maaf, gagal menjawab (terlalu banyak langkah).", trace

def ask(q: str) -> str:
    return run(q)[0]

if __name__ == "__main__":
    while True:
        q = input("> ").strip()
        if not q:
            break
        print(ask(q))
