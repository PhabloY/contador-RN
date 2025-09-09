
# Raw list examples (pasted from WhatsApp)
raw_list = [
    "18- Molho Grill 1,05kg",
    "15 -Molho barbecue 1,05kg",
    "31 - Molho Chipotle 1,05kg",
    "7- Molho Barbecue 1,05kg",
    "   20 - Ketchup real 1,05kg  ",
    "31- Molho Chipotle 1,05kg",  # duplicate example
    "12 Maionese Heinz 215g",     # without hyphen
    "5 Mostarda Heinz Mel 220g",  # without hyphen
    "3- Molho Tártaro 1,05kg",
    "16 Molho Alho e Ervas 215g",
    "22 Ketchup Heinz Curry 397g"
    "18- Molh Grill 1,05kg",        # erro no nome
    "15 -Molo Barbcue 1,05kg",     # erro no nome
    "31 - Molho Chpotl 1,05kg",    # erro no nome
    "7- Molho Brbecue 1,05kg",     # correto
    "20 - Ketchp Real 1,05kg",      # erro no nome
    "3- Molho Trtaro 1,05kg"        # erro no nome
]


def process_raw_list(raw):
    """
    Processes a raw list of stock items and handles duplicates interactively.

    Options for duplicates:
        (m) keep separate
        (r) remove duplicate
        (s) sum quantities
    Returns a list of dictionaries with keys:
        - quantidade: int
        - produto: str
    """

    estoque = []
    produtos = {}  # track duplicates by lowercase product name

    for item in raw:
        item = item.strip()
        if not item:
            continue

        # Try split by hyphen first
        if "-" in item:
            quantity_str, product = item.split("-", 1)
        else:  # assume first number is quantity
            parts = item.split(maxsplit=1)
            if len(parts) == 2:
                quantity_str, product = parts
            else:
                print(f"⚠️ Could not parse item: '{item}'")
                continue

        try:
            quantity = int(quantity_str.strip())
        except ValueError:
            print(f"⚠️ Could not convert quantity for item: '{item}'")
            continue

        product = product.strip()
        key = product.lower()

        if key in produtos:
            print(f"\n⚠️ Duplicate found: '{product}'")
            print(
                f"Existing stock: {produtos[key]['quantidade']}x {produtos[key]['produto']}")
            print(f"New item found: {quantity}x {product}")

            choice = input(
                "Keep separate (m), remove duplicate (r), or sum quantities (s)? [m/r/s]: "
            ).lower().strip()

            if choice == "m":
                estoque.append({"quantidade": quantity, "produto": product})
            elif choice == "r":
                print("→ Ignored.")
            elif choice == "s":
                produtos[key]["quantidade"] += quantity
                print(
                    f"→ Quantities summed! Now {produtos[key]['quantidade']}x {product}")
            else:
                print("→ Invalid option, keeping separate by default.")
                estoque.append({"quantidade": quantity, "produto": product})
        else:
            novo_item = {"quantidade": quantity, "produto": product}
            estoque.append(novo_item)
            produtos[key] = novo_item

    return estoque


# Final processed list ready to import in app.py
estoque = process_raw_list(raw_list)

# Optional debug print
print("\n📦 Final stock:")
for item in estoque:
    print(f"{item['quantidade']}x {item['produto']}")
