headers = [state.name.capitalize() for state in State] + ["Deaths"]
table_data = []

for i in range(numberOfRuns):
    print(f"Simulação {i + 1}")
    model = RandomWalkModel(gridSize)
    model.simulation(numberOfGenerations, verbose)

    report = model.report()
    row = report + [model.numberOfDeaths()]
    table_data.append(row)

    if saveImages:
        model.printImage(i)

# Imprimir tabela após todas as simulações
print("\nResumo Final das Simulações:\n")
print(tabulate(table_data, headers=headers, showindex="always", tablefmt="grid"))
 
print("Relatório final:")
for state, count in zip(State, report):
    print(f"{state.name}: {count}")
print("Mortes:", model.numberOfDeaths())