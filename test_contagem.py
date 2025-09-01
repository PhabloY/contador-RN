from contagem import estoque

for item in estoque:
    print(f"Quantidade:{item['quantidade']}, product: {item['produto']}")
