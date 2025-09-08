from products import produtos_oficiais
from pathlib import Path
import sys
import tkinter as tk
from rapidfuzz import process, fuzz
import unicodedata

# Adicionando raiz do projeto ao path
root_path = Path(__file__).parent.parent.resolve()
sys.path.append(str(root_path))

# -----------------------------
# Função de normalização para comparar sem acento
# -----------------------------


def remove_accents(text):
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')

# -----------------------------
# Autocomplete com teclado + fuzzy parcial
# -----------------------------


class AutocompleteEntry(tk.Entry):
    def __init__(self, produtos, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.produtos = produtos
        self.var = self["textvariable"] = tk.StringVar()
        self.var.trace_add("write", self.changed)
        self.listbox_up = False
        self.listbox = None
        self.bind("<Down>", self.move_down)
        self.bind("<Up>", self.move_up)
        self.bind("<Return>", self.selection_from_keyboard)

    def changed(self, *args):
        typed = self.var.get()
        if typed == '':
            self.hide_listbox()
        else:
            typed_norm = remove_accents(typed).lower()
            produtos_norm = [remove_accents(p).lower() for p in self.produtos]

            # fuzzy partial_ratio para sugerir com poucas letras
            matches = process.extract(
                typed_norm, produtos_norm, scorer=fuzz.partial_ratio, limit=5)
            matches = [self.produtos[idx]
                       for _, score, idx in matches if score >= 40]

            if matches:
                if not self.listbox_up:
                    self.listbox = tk.Listbox(width=self["width"])
                    self.listbox.bind("<<ListboxSelect>>", self.selection)
                    self.listbox.place(
                        x=self.winfo_x(), y=self.winfo_y() + self.winfo_height())
                    self.listbox_up = True
                self.listbox.delete(0, tk.END)
                for m in matches:
                    self.listbox.insert(tk.END, m)
            else:
                self.hide_listbox()

    def selection(self, event):
        if self.listbox_up:
            index = self.listbox.curselection()
            if index:
                value = self.listbox.get(index)
                self.var.set(value)
            self.hide_listbox()

    def selection_from_keyboard(self, event):
        if self.listbox_up:
            try:
                index = self.listbox.curselection()
                if not index:
                    index = 0
                else:
                    index = index[0]
                value = self.listbox.get(index)
                self.var.set(value)
            except:
                pass
            self.hide_listbox()
        return "break"

    def move_down(self, event):
        if self.listbox_up:
            cur = self.listbox.curselection()
            if not cur:
                self.listbox.selection_set(0)
            else:
                next_index = min(cur[0]+1, self.listbox.size()-1)
                self.listbox.selection_clear(0, tk.END)
                self.listbox.selection_set(next_index)
            self.listbox.activate(next_index)
        return "break"

    def move_up(self, event):
        if self.listbox_up:
            cur = self.listbox.curselection()
            if not cur:
                self.listbox.selection_set(0)
            else:
                prev_index = max(cur[0]-1, 0)
                self.listbox.selection_clear(0, tk.END)
                self.listbox.selection_set(prev_index)
            self.listbox.activate(prev_index)
        return "break"

    def hide_listbox(self):
        if self.listbox_up:
            self.listbox.destroy()
            self.listbox_up = False
            self.listbox = None


# -----------------------------
# Interface Tkinter
# -----------------------------
root = tk.Tk()
root.title("Teste Autocomplete Fuzzy Parcial")
root.geometry("500x400")

# Campo de produto com autocomplete
tk.Label(root, text="Produto:").pack()
entry_produto = AutocompleteEntry(
    produtos_oficiais, root, font=("Helvetica", 12), width=50)
entry_produto.pack(pady=5)

# Campo de quantidade
tk.Label(root, text="Quantidade:").pack()
entry_quantidade = tk.Entry(root, font=("Helvetica", 12))
entry_quantidade.pack(pady=5)

# Lista de itens digitados (exibição)
frame_lista = tk.Frame(root)
frame_lista.pack(pady=10, fill="x")
label_itens = tk.Label(frame_lista, text="",
                       justify="left", font=("Helvetica", 10))
label_itens.pack()

# Lista que guarda os últimos 5 itens
itens_digitados = []

# Função para atualizar a lista visual


def atualizar_lista_visual():
    texto = ""
    for item in itens_digitados:
        texto += f"• {item['produto']} x {item['quantidade']}\n"
    label_itens.config(text=texto)

# Função para enviar item


def enviar_item(event=None):
    produto = entry_produto.get().strip()
    quantidade = entry_quantidade.get().strip()
    if produto and quantidade:
        # Adiciona item na lista
        itens_digitados.append({"produto": produto, "quantidade": quantidade})
        # Mantém só os últimos 5
        if len(itens_digitados) > 5:
            itens_digitados.pop(0)
        atualizar_lista_visual()
        # Limpa campos para próximo input
        entry_produto.delete(0, tk.END)
        entry_quantidade.delete(0, tk.END)
        entry_produto.focus()


# Bind Enter na quantidade
entry_quantidade.bind("<Return>", enviar_item)

# Botão só para teste também
btn_enviar = tk.Button(root, text="Enviar Item", command=enviar_item)
btn_enviar.pack(pady=10)

root.mainloop()
