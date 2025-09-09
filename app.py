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

# =============================
# Funções auxiliares
# =============================


def remove_accents(text: str) -> str:
    """Remove acentos para comparação sem alterar o nome original."""
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')


def corrigir_nome(produto, lista_oficial):
    """Corrige o nome usando fuzzy matching, mantendo acentos do nome oficial."""
    if not produto.strip():
        return ""
    produto_norm = remove_accents(produto).lower()
    lista_norm = [remove_accents(p).lower() for p in lista_oficial]

    resultado = process.extractOne(produto_norm, lista_norm, scorer=fuzz.ratio)
    if resultado:
        idx = resultado[2]  # índice do nome oficial
        score = resultado[1]
        if score >= 60:  # ajustável
            return lista_oficial[idx]
    return produto.strip()

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
