import enum
import random
import pandas as pd  # Importa a biblioteca pandas
from PIL import Image
from tabulate import tabulate

# Certifique-se de que as bibliotecas necessárias estão instaladas:
# pip install pandas openpyxl Pillow tabulate

# Enum class to represent the possible states of an individual in the simulation.
class State(enum.Enum):
    healthy = 0
    sick = 1
    asymptomatic = 2
    dead = 3
    immune = 4

class Individual:
    def __init__(self, state):
        self.state = state

class RandomWalkModel:
    def __init__(self, populationMatrixSize):
        self.population = []
        self.nextPopulation = []
        self.currentGeneration = 0

        # # default variant
        # self.transitionProbabilities = [
        #     [1.0, 0.0, 0.0, 0.0, 0.0],      # Healthy
        #     [0.2, 0.3, 0.11, 0.34, 0.05],    # Sick
        #     [0.3, 0.0, 0.6, 0.0, 0.1],       # Asymptomatic
        #     [0.0, 0.0, 0.0, 1.0, 0.0],      # Dead
        #     [0.7, 0.0, 0.0, 0.0, 0.3]       # Immune
        # ]
        
        # self.contagionFactor = 0.7 # Probability of getting sick after interaction with a sick individual 
        # self.socialDistanceEffect = 0.0 # Probability of avoiding contact because of social distancing


        self.transitionProbabilities = [
            [1.0, 0.0, 0.0, 0.0, 0.0],       # Healthy
            [0.4, 0.15, 0.23, 0.2, 0.12],    # Sick
            [0.2, 0.0, 0.5, 0.0, 0.3],       # Asymptomatic
            [0.0, 0.0, 0.0, 1.0, 0.0],       # Dead
            [0.7, 0.0, 0.0, 0.0, 0.3]        # Immune
        ]
        
        self.contagionFactor = 0.7 # Probability of getting sick after interaction with a sick individual 
        self.socialDistanceEffect = 0.5 # Probability of avoiding contact because of social distancing
        
        
        for i in range(populationMatrixSize):
            self.population.append([])
            self.nextPopulation.append([])
            for j in range(populationMatrixSize):
                self.population[i].append(Individual(State.healthy))
                self.nextPopulation[i].append(Individual(State.healthy))

        startIndex = populationMatrixSize // 2
        self.population[startIndex][startIndex].state = State.sick
        self.nextPopulation[startIndex][startIndex].state = State.sick

    def individualTransition(self, line, column):
        individual = self.population[line][column]
        if individual.state in [State.dead, State.healthy]:
            return
        if individual.state == State.sick:
            self.computeSocialInteractions(line, column)
        probabilities = self.transitionProbabilities[individual.state.value]
        number = random.random()
        cumulativeProbability = 0
        for index in range(len(probabilities)):
            cumulativeProbability += probabilities[index]
            if number <= cumulativeProbability:
                self.nextPopulation[line][column].state = State(index)
                break

    def computeSickContact(self, neighbour):
        if random.random() <= self.contagionFactor:
            neighbour.state = State.sick

    def computeSocialInteractions(self, line, column):
        for i in range(max(0, line - 1), min(line + 2, len(self.population))):
            for j in range(max(0, column - 1), min(column + 2, len(self.population[i]))):
                if i == line and j == column:
                    continue
                if self.socialDistanceEffect < random.random():
                    neighbour = self.nextPopulation[i][j]
                    if neighbour.state == State.healthy:
                        self.computeSickContact(neighbour)

    def nextGeneration(self):
        for i in range(len(self.population)):
            for j in range(len(self.population[i])):
                self.individualTransition(i, j)
        for i in range(len(self.population)):
            for j in range(len(self.population[i])):
                self.population[i][j].state = self.nextPopulation[i][j].state

    def report(self):
        cases = [0] * len(State)
        for row in self.population:
            for individual in row:
                cases[individual.state.value] += 1
        return cases

    def simulation(self, generations):
        for _ in range(generations):
            self.nextGeneration()

    def numberOfDeaths(self):
        return sum(1 for row in self.population for individual in row if individual.state == State.dead)

    def printImage(self, name):
        lines = len(self.population)
        columns = len(self.population[0])
        img = Image.new("RGB", (columns, lines))
        colors = {
            State.healthy: (0, 255, 0),
            State.sick: (255, 255, 0),
            State.dead: (255, 0, 0),
            State.immune: (0, 0, 255),
            State.asymptomatic: (255, 0, 255)
        }
        for i in range(lines):
            for j in range(columns):
                state = self.population[i][j].state
                img.putpixel((j, i), colors.get(state, (0,0,0))) # Default to black if state not in map
        
        # img.save(f"./images/simulation-{name}.png")
        # img.show()

# =======================
#         MAIN
# =======================

numberOfRuns = 1000
gridSize = 156
numberOfGenerations = 52
saveImages = False

# Cabeçalhos para a tabela e o arquivo Excel
console_headers = [state.name.capitalize() for state in State] + ["Deaths"]
excel_headers = ['Execução'] + console_headers

# Listas para armazenar os resultados
all_runs_data = []
sums = [0] * (len(State) + 1)

# Loop principal para executar as simulações e coletar dados
for i in range(numberOfRuns):
    print(f"Simulação {i + 1}/{numberOfRuns}")
    model = RandomWalkModel(gridSize)
    model.simulation(numberOfGenerations)

    report = model.report()
    deaths = model.numberOfDeaths()
    
    # Guarda os resultados desta execução para a tabela
    run_results = report + [deaths]
    all_runs_data.append([f"{i + 1}"] + run_results)

    # Acumula os totais para o cálculo da média
    for idx in range(len(report)):
        sums[idx] += report[idx]
    sums[-1] += deaths

    if saveImages:
        model.printImage(f"run_{i+1}")

# --- Geração do Relatório em Excel (.xlsx) ---

# Calcula as médias
averages = [round(value / numberOfRuns) for value in sums]
averages_row = ['Média Final'] + averages  # Cria a linha de resumo

# Cria um DataFrame com todos os dados
df = pd.DataFrame(all_runs_data, columns=excel_headers)

# Cria um DataFrame para a linha de média e o anexa ao final
df_avg = pd.DataFrame([averages_row], columns=excel_headers)
df_final = pd.concat([df, df_avg], ignore_index=True)

# Salva o DataFrame em um arquivo Excel
excel_output_filename = "relatorio_simulacoes_consolidado.xlsx"
df_final.to_excel(excel_output_filename, index=False, sheet_name='Resultados Consolidados')

# --- Saída Final no Console ---

print("\n" + "="*40)
print("MÉDIA FINAL DAS SIMULAÇÕES (CONSOLE):")
print("="*40)
# Mostra a tabela de médias no console
print(tabulate([averages], headers=console_headers, tablefmt="grid"))
print(f"\nRelatório consolidado em Excel '{excel_output_filename}' gerado com sucesso.")