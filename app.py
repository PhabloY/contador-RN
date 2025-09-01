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
    time.sleep(5)  # tempo para posicionar o cursor no sistema
    for item in estoque:
        quantidade = item.get("quantidade", 0)
        produto_nome = item.get("produto", "").strip()
        if not produto_nome:
            continue

        nome_corrigido = corrigir_nome(produto_nome, produtos_oficiais)
        texto_para_digitar = f"{quantidade} {nome_corrigido}"

        print(f"Digitando: {texto_para_digitar}")  # DEBUG

        # Usa clipboard para suportar acentos
        pyperclip.copy(texto_para_digitar)
        pyautogui.hotkey("ctrl", "v")
        pyautogui.press("enter")

    messagebox.showinfo("Sucesso", "Digitação automática concluída!")


# =============================
# Interface Gráfica
# =============================
root = tk.Tk()
root.title("📦 Automação de Contagem")
root.geometry("500x600")
root.resizable(False, False)

# Centralizar a janela
root.update_idletasks()
x = (root.winfo_screenwidth() - 500) // 2
y = (root.winfo_screenheight() - 600) // 2
root.geometry(f"+{x}+{y}")

# Ícone opcional
try:
    root.iconbitmap("icon.ico")
except tk.TclError:
    pass

# Frame principal com canvas e scrollbar
frame_main = tk.Frame(root)
frame_main.pack(padx=20, pady=20, fill="both", expand=True)

canvas = tk.Canvas(frame_main)
scrollbar = tk.Scrollbar(frame_main, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

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
    wraplength=450
)
label_preview.pack(pady=10, fill="x")

# Botão de digitação
botao_iniciar = tk.Button(
    root,
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
