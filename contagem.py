import difflib
from products import produtos_oficiais

raw_list = [
    "18- Molho Grill Junior 1,05kg",
    "15 -Molho barbecue 1,05kg",     # 1
    "31 - Molho Chipotle 1,05kg",
    "7- Molho Barbecue 1,05kg",      # 2
    "   20 - Ketchup real 1,05kg  ",
    "31- Molho Chipotle 1,05kg",
    "12 Maionese Heinz 215g",
    "5 Mostarda Heinz Mel 220g",
    "3- Molho Tártaro 1,05kg",
    "16 Molho Alho e Ervas 215g",
    "22 Ketchup Heinz Curry 397g",
    "18- Molh Grill 1,05kg",
    "15 -Molo Barbcue 1,05kg",       # 3
    "31 - Molho Chpotl 1,05kg",
    "7- Molho Brbecue 1,05kg",
    "20 - Ketchp Real 1,05kg",
    "3- Molho Trtaro kisabor 1,05kg"
]


def normalize_product_name(typed_name, official_list, threshold=0.75):
    typed_clean = typed_name.strip()
    for official in official_list:
        if typed_clean.lower() == official.lower():
            return official
    best_match = None
    highest_similarity = 0.0
    for official in official_list:
        sim = difflib.SequenceMatcher(
            None,
            typed_clean.lower().replace(" ", ""),
            official.lower().replace(" ", "")
        ).ratio()
        if sim > highest_similarity:
            highest_similarity = sim
            best_match = official
    if highest_similarity >= threshold and best_match:
        print(
            f"🔍 Normalizado: '{typed_clean}' → '{best_match}' (similaridade: {highest_similarity:.2f})")
        return best_match
    else:
        return typed_clean


def get_user_choice():
    while True:
        choice = input(
            "Manter separado (m), remover (r) ou somar (s)? [m/r/s]: ").lower().strip()
        if choice in ("m", "r", "s"):
            return choice
        else:
            print("⚠️ Resposta inválida. Digite 'm', 'r' ou 's'.")


def process_raw_list(raw):
    estoque = []  # lista final de itens
    produtos = {}  # key: nome_normalizado.lower() → índice do item em estoque

    for idx, item_str in enumerate(raw, 1):
        print(f"\n--- 🧾 PROCESSANDO ITEM {idx}: '{item_str}' ---")
        item_str = item_str.strip()
        if not item_str:
            continue

        # Parse
        if "-" in item_str:
            parts = item_str.split("-", 1)
            quantity_str, product = parts[0], parts[1]
        else:
            parts = item_str.split(maxsplit=1)
            if len(parts) == 2:
                quantity_str, product = parts
            else:
                print(f"⚠️ Não conseguiu parsear: '{item_str}'")
                continue

        try:
            quantity = int(quantity_str.strip())
        except ValueError:
            print(f"⚠️ Quantidade inválida: '{item_str}'")
            continue

        product = product.strip()
        normalized = normalize_product_name(product, produtos_oficiais)
        if normalized != product:
            print(f"✅ Corrigido: '{product}' → '{normalized}'")

        key = normalized.lower()

        if key in produtos:
            # Pega o índice do item existente
            existing_idx = produtos[key]
            existing_item = estoque[existing_idx]

            print(f"\n🔁 DUPLICATA DETECTADA!")
            print(
                f"  ➤ Existente: {existing_item['quantidade']}x {existing_item['produto']}")
            print(f"  ➤ Novo:      {quantity}x {normalized}")

            choice = get_user_choice()

            if choice == "s":
                # SOMA: atualiza o item existente
                estoque[existing_idx]["quantidade"] += quantity
                print(
                    f"→ ✅ SOMADO! Total: {estoque[existing_idx]['quantidade']}x {normalized}")
                # ⚠️ NÃO ADICIONA NOVO ITEM
            elif choice == "r":
                print("→ 🗑️ REMOVIDO (ignorado).")
            else:  # "m"
                # ADICIONA COMO NOVO ITEM
                novo_item = {"quantidade": quantity, "produto": normalized}
                estoque.append(novo_item)
                print(f"→ ➕ ADICIONADO SEPARADO: {quantity}x {normalized}")
                # ⚠️ NÃO ATUALIZA produtos[key] — futuros itens ainda vão comparar com o grupo original
        else:
            # Primeira vez — adiciona normalmente
            novo_item = {"quantidade": quantity, "produto": normalized}
            estoque.append(novo_item)
            produtos[key] = len(estoque) - 1  # guarda o índice
            print(f"→ ➕ ADICIONADO: {quantity}x {normalized}")

    return estoque


estoque = process_raw_list(raw_list)

print("\n" + "="*60)
print("📦 ESTOQUE FINAL (CONSOLIDADO):")
print("="*60)
for i, item in enumerate(estoque, 1):
    print(f"{i:2}. {item['quantidade']:>3}x {item['produto']}")
