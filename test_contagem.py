from contagem import estoque

print("\n📦 Estoque final:")
for item in estoque:
    print(f"{item['quantidade']}x {item['produto']}")
