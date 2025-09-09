# type: ignore
# app.py
from products import produtos_oficiais
from contagem import estoque
from rapidfuzz import process, fuzz
import pyautogui
import pyperclip
import time
import tkinter as tk
from tkinter import messagebox
import unicodedata
import re

# =============================
# Ajustes/flags (faça tuning aqui)
# =============================
DEBUG = False
MIN_SCORE_TOKEN_SORT = 80    # token_sort_ratio mínimo para aceitar
MIN_SCORE_PARTIAL = 90       # partial_ratio mínimo para aceitar
MIN_SHARED_TOKENS = 1        # número mínimo de tokens em comum

# =============================
# Funções auxiliares
# =============================


def remove_accents(text: str) -> str:
    """Remove acentos para comparação sem alterar o nome original."""
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')


def tokenize_core(text: str):
    """
    Retorna tokens 'úteis' do texto: lower, sem acentos, sem pontuação,
    removendo números e unidades (g, kg, ml, l, etc).
    """
    t = remove_accents(text).lower()
    # substitui tudo que não for letra/número por espaço
    t = re.sub(r'[^a-z0-9\s]', ' ', t)
    parts = [p.strip() for p in t.split() if p.strip()]
    tokens = []
    for p in parts:
        # ignora tokens que são apenas números ou unidades
        if re.match(r'^\d+([.,]\d+)?$', p):
            continue
        if p in {"g", "kg", "ml", "l", "un", "pk", "mg", "oz"}:
            continue
        tokens.append(p)
    return tokens


def corrigir_nome(produto, lista_oficial):
    """
    Corrige o nome usando fuzzy matching com critérios adicionais para evitar
    substituições erradas (p.ex. 'Ketchup Heinz' -> 'Molho Real Zafran').
    """
    if not produto or not produto.strip():
        return ""

    produto_raw = produto.strip()
    produto_norm = remove_accents(produto_raw).lower()

    # normaliza lista oficial
    lista_norm = [remove_accents(p).lower() for p in lista_oficial]

    # 1) se já for exatamente um nome oficial (normalizado), retorna a oficial
    for i, norm in enumerate(lista_norm):
        if norm == produto_norm:
            if DEBUG:
                print(f"[corrigir_nome] exact match: {lista_oficial[i]}")
            return lista_oficial[i]

    # tokens "úteis" para checagem de palavras em comum
    produto_tokens = set(tokenize_core(produto_raw))

    # 2) pega top candidates pelo token_sort_ratio
    candidatos = process.extract(
        produto_norm, lista_norm, scorer=fuzz.token_sort_ratio, limit=8)

    best_candidate = None
    best_score_combined = -1

    for cand_norm, score_ts, idx in candidatos:
        candidato_oficial = lista_oficial[idx]
        candidato_tokens = set(tokenize_core(candidato_oficial))

        shared = produto_tokens & candidato_tokens
        shared_count = len(shared)

        # calcula partial ratio também (útil pra trechos)
        score_partial = fuzz.partial_ratio(produto_norm, cand_norm)

        if DEBUG:
            print(
                f"[corrigir_nome] candidate='{candidato_oficial}' ts={score_ts} partial={score_partial} shared={shared}")

        accept = False
        # criterio 1: token_sort alto + pelo menos um token em comum
        if score_ts >= MIN_SCORE_TOKEN_SORT and shared_count >= MIN_SHARED_TOKENS:
            accept = True
            score_combined = max(score_ts, score_partial)
        # criterio 2: partial ratio muito alto + pelo menos um token em comum
        elif score_partial >= MIN_SCORE_PARTIAL and shared_count >= MIN_SHARED_TOKENS:
            accept = True
            score_combined = max(score_ts, score_partial)
        else:
            accept = False
            score_combined = max(score_ts, score_partial)

        if accept and score_combined > best_score_combined:
            best_score_combined = score_combined
            best_candidate = candidato_oficial

    if best_candidate:
        if DEBUG:
            print(
                f"[corrigir_nome] accepted: {best_candidate} (score {best_score_combined})")
        return best_candidate

    # fallback: não arriscar — retorna o texto original do usuário
    if DEBUG:
        print(f"[corrigir_nome] fallback keep original: '{produto_raw}'")
    return produto_raw

# =============================
# Função de digitação automática
# =============================


def digitar_estoque():
    try:
        delay_item = float(entry_delay_item.get())
        delay_enter = float(entry_delay_enter.get())
    except ValueError:
        messagebox.showerror(
            "Erro", "Insira valores válidos de tempo em segundos.")
        return

    messagebox.showinfo(
        "Atenção",
        "Posicione o cursor no campo de produto do sistema.\n"
        "A digitação automática começará em 5 segundos."
    )
    time.sleep(5)

    for item in estoque:
        quantidade = item.get("quantidade", 0)
        produto_nome = item.get("produto", "").strip()
        if not produto_nome or quantidade <= 0:
            continue

        nome_corrigido = corrigir_nome(produto_nome, produtos_oficiais)

        # ===== Passo 1: digitar produto =====
        pyperclip.copy(nome_corrigido)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(delay_enter)

        # ===== Passo 2: selecionar sugestão do autocomplete =====
        pyautogui.press("down")  # seta para selecionar sugestão
        pyautogui.press("enter")
        time.sleep(delay_enter)

        # ===== Passo 3: ir para campo de quantidade =====
        pyautogui.press("tab")
        time.sleep(delay_enter)

        # ===== Passo 4: digitar quantidade =====
        pyperclip.copy(str(quantidade))
        pyautogui.hotkey("ctrl", "v")
        time.sleep(delay_enter)

        # ===== Passo 5: confirmar enter =====
        pyautogui.press("enter")
        time.sleep(delay_item)

    messagebox.showinfo("Sucesso", "Digitação automática concluída!")


# =============================
# Interface Gráfica
# =============================
root = tk.Tk()
root.title("📦 Automação de Contagem")
root.geometry("550x650")
root.resizable(False, False)

# Centralizar a janela
root.update_idletasks()
x = (root.winfo_screenwidth() - 550) // 2
y = (root.winfo_screenheight() - 650) // 2
root.geometry(f"+{x}+{y}")

# Frame principal com canvas e scrollbar
frame_main = tk.Frame(root)
frame_main.pack(padx=20, pady=20, fill="both", expand=True)

canvas = tk.Canvas(frame_main)
scrollbar = tk.Scrollbar(frame_main, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas)

scrollable_frame.bind("<Configure>", lambda e: canvas.configure(
    scrollregion=canvas.bbox("all")))

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Preview do estoque
preview_text = "\n".join(
    [f"• {item['quantidade']} — {corrigir_nome(item['produto'], produtos_oficiais)}"
     for item in estoque]
)

label_preview = tk.Label(
    scrollable_frame,
    text="📋 Preview da contagem:\n\n" + preview_text,
    justify="left",
    font=("Helvetica", 10),
    fg="gray10",
    bg="white",
    relief="solid",
    borderwidth=1,
    padx=10,
    pady=10,
    wraplength=500
)
label_preview.pack(pady=10, fill="x")

# Inputs para configurar delays
frame_delays = tk.Frame(scrollable_frame)
frame_delays.pack(pady=10, fill="x")

tk.Label(frame_delays, text="⏱ Tempo entre Enter (segundos):").grid(
    row=0, column=0, sticky="w")
entry_delay_enter = tk.Entry(frame_delays)
entry_delay_enter.insert(0, "0.2")
entry_delay_enter.grid(row=0, column=1)

tk.Label(frame_delays, text="⏱ Tempo entre itens (segundos):").grid(
    row=1, column=0, sticky="w")
entry_delay_item = tk.Entry(frame_delays)
entry_delay_item.insert(0, "0.5")
entry_delay_item.grid(row=1, column=1)

# Botão de digitação
botao_iniciar = tk.Button(
    scrollable_frame,
    text="✅ Iniciar Digitação",
    command=digitar_estoque,
    bg="#28a745",
    fg="white",
    font=("Helvetica", 12, "bold"),
    relief="flat",
    padx=20,
    pady=10
)
botao_iniciar.pack(pady=20)

botao_iniciar.bind("<Enter>", lambda e: botao_iniciar.config(bg="#218838"))
botao_iniciar.bind("<Leave>", lambda e: botao_iniciar.config(bg="#28a745"))

root.mainloop()
