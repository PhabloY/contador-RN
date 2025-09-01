# type: ignore
# app.py
from products import produtos_oficiais
from contagem import estoque
from rapidfuzz import process, fuzz
import pyautogui
import time
import tkinter as tk
from tkinter import messagebox

# Função para corrigir nomes usando fuzzy matching


def corrigir_nome(produto, lista_oficial):
    resultado, score, _ = process.extractOne(
        produto, lista_oficial, scorer=fuzz.ratio)
    if score >= 80:  # ajustar se quiser mais rigor
        return resultado
    else:
        return produto  # mantém original se não houver correspondência boa

# Função de digitação automática


def digitar_estoque():
    time.sleep(5)  # tempo para posicionar o cursor no sistema
    for item in estoque:
        quantidade = str(item["quantidade"])
        nome = corrigir_nome(item["produto"], produtos_oficiais)
        pyautogui.typewrite(f"{quantidade} {nome}")
        pyautogui.press("enter")
    messagebox.showinfo("Sucesso", "Digitação automática concluída!")


# Criando interface simples
root = tk.Tk()
root.title("Automação de Contagem")

# Texto de preview
preview_text = "\n".join(
    [f"{item['quantidade']} - {corrigir_nome(item['produto'], produtos_oficiais)}" for item in estoque])
label_preview = tk.Label(
    root, text="Preview da contagem:\n\n" + preview_text, justify="left")
label_preview.pack(padx=10, pady=10)

# Botão para iniciar digitação
botao_iniciar = tk.Button(root, text="Iniciar Digitação",
                          command=digitar_estoque, bg="green", fg="white")
botao_iniciar.pack(padx=10, pady=10)

root.mainloop()
