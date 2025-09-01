# Raw list example (e.g., pasted from WhatsApp)
raw_list = [
    "18- Molho Grill 1,05kg",
    "15 -Molho barbecue 1,05kg",
    "31 - Molho Chipotle 1,05kg",
    "7- Molho Barbecue 1,05kg",
    "   20 - Ketchup real 1,05kg  ",
    "31- Molho Chipotle 1,05kg"  # duplicate example
]


def process_raw_list(raw):
    """
    Processa a lista bruta de itens e lida com duplicatas interativamente.
    Opções para duplicatas:
        (m) manter separado
        (r) remover duplicata
        (s) somar quantidades
    """
    estoque = []
    # dict para rastrear duplicatas pelo nome do produto (lowercase)
    produtos = {}

    for item in raw:
        if "-" not in item:
            continue

        quantity_str, product = item.split("-", 1)
        quantity = int(quantity_str.strip())
        product = product.strip()
        key = product.lower()

        if key in produtos:
            print(f"\n⚠️ Duplicata encontrada: '{product}'")
            print(
                f"Já existe no estoque: {produtos[key]['quantidade']}x {produtos[key]['produto']}")
            print(f"Novo item encontrado: {quantity}x {product}")

            choice = input(
                "Deseja (m) manter separado, (r) remover duplicata, ou (s) somar quantidades? [m/r/s]: ").lower().strip()

            if choice == "m":
                estoque.append({"quantidade": quantity, "produto": product})
            elif choice == "r":
                print("→ Ignorado.")
            elif choice == "s":
                produtos[key]["quantidade"] += quantity
                print(
                    f"→ Quantidade somada! Agora {produtos[key]['quantidade']}x {product}")
            else:
                print("→ Opção inválida, mantendo separado por padrão.")
                estoque.append({"quantidade": quantity, "produto": product})
        else:
            novo_item = {"quantidade": quantity, "produto": product}
            estoque.append(novo_item)
            produtos[key] = novo_item

    return estoque


# Final list pronta
estoque = process_raw_list(raw_list)

print("\n📦 Estoque final:")
for item in estoque:
    print(f"{item['quantidade']}x {item['produto']}")
