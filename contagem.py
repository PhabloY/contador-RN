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
    Process a raw list of stock items into a standardized list of dictionaries.

    Each dictionary contains:
        - quantidade: integer representing quantity
        - produto: string representing product name

    Features:
        - Strips extra spaces
        - Separates quantity and product using the first "-"
        - Avoids duplicates based on quantity + product name (case-insensitive)
    """
    cleaned_stock = []
    seen = set()  # to avoid duplicates

    for item in raw:
        if "-" in item:
            quantity_str, product = item.split("-", 1)
            quantity = int(quantity_str.strip())
            product = product.strip()

            # Use a key to detect duplicates
            key = f"{quantity}-{product.lower()}"
            if key not in seen:
                cleaned_stock.append(
                    {"quantidade": quantity, "produto": product})
                seen.add(key)

    return cleaned_stock


# Final list ready to be imported into app.py
estoque = process_raw_list(raw_list)
