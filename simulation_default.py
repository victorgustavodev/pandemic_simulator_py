import enum
import random
from PIL import Image
from tabulate import tabulate # Certifique-se de que a biblioteca está instalada (pip install tabulate)
from fpdf import FPDF # Certifique-se de que a biblioteca está instalada (pip install fpdf2)

#This code is a simulation of a disease spread using a random walk model.
#This code used to be in a file called "simulation_default.py" and is now being refactored to include PDF generation and other improvements.
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

        # default variant
        # self.transitionProbabilities = [
        #     [1.0, 0.0, 0.0, 0.0, 0.0],      # Healthy
        #     [0.2, 0.3, 0.11, 0.34, 0.05],   # Sick
        #     [0.3, 0.0, 0.6, 0.0, 0.1],      # Asymptomatic
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

    def simulation(self, generations, verbose):
        for _ in range(generations):
            self.nextGeneration()

    def numberOfDeaths(self):
        return sum(1 for row in self.population for individual in row if individual.state == State.dead)

# =======================
#      PDF GENERATOR
# =======================
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'Relatório Consolidado das Simulações', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

    def create_table(self, table_data, headers, summary_row=None):
        self.set_font('Arial', 'B', 9)
        # Distribui a largura da coluna de forma uniforme
        effective_width = self.w - self.l_margin - self.r_margin
        col_width = effective_width / len(headers)

        # Imprime os cabeçalhos da tabela
        for header in headers:
            self.cell(col_width, 8, header, 1, 0, 'C')
        self.ln()

        # Imprime as linhas de dados da tabela
        self.set_font('Arial', '', 9)
        for row in table_data:
            for item in row:
                self.cell(col_width, 8, str(item), 1, 0, 'C')
            self.ln()

        # Imprime a linha de resumo (média) com destaque
        if summary_row:
            self.set_font('Arial', 'B', 9) # Usa negrito para a linha de resumo
            for item in summary_row:
                self.cell(col_width, 8, str(item), 1, 0, 'C')
            self.ln()

# =======================
#         MAIN
# =======================

numberOfRuns = 1000
gridSize = 156
numberOfGenerations = 52
saveImages = False
verbose = False

# Cabeçalhos para as tabelas
console_headers = [state.name.capitalize() for state in State] + ["Deaths"]
pdf_table_headers = ['Execução'] + console_headers

# Listas para armazenar os resultados
all_runs_data_for_pdf = []
sums = [0] * (len(State) + 1)

# Loop principal para executar as simulações e coletar dados
for i in range(numberOfRuns):
    print(f"Simulação {i + 1}")
    model = RandomWalkModel(gridSize)
    model.simulation(numberOfGenerations, verbose)

    report = model.report()
    deaths = model.numberOfDeaths()
    
    # Guarda os resultados desta execução para o PDF
    run_results = report + [deaths]
    all_runs_data_for_pdf.append([f"{i + 1}"] + run_results)

    # Acumula os totais para o cálculo da média
    for idx in range(len(report)):
        sums[idx] += report[idx]
    sums[-1] += deaths

    if saveImages:
        # A função printImage ainda pode ser usada se necessário
        model.printImage(f"run_{i+1}")

# --- Geração do Relatório em PDF Após todas as simulações ---

# Calcula as médias
averages = [round(value / numberOfRuns) for value in sums]
averages_row = ['Média Final'] + averages # Cria a linha de resumo para o PDF

# Inicializa o objeto PDF e adiciona uma página
pdf = PDF()
pdf.add_page()

# Adiciona a tabela única e consolidada ao PDF
pdf.create_table(
    table_data=all_runs_data_for_pdf,
    headers=pdf_table_headers,
    summary_row=averages_row
)

# Salva o arquivo PDF final
pdf_output_filename = "relatorio_simulacoes_consolidado.pdf"
pdf.output(pdf_output_filename, "/results/" + pdf_output_filename)

# --- Saída Final no Console ---

print("\n" + "="*40)
print("MÉDIA FINAL DAS SIMULAÇÕES (CONSOLE):")
print("="*40)
print(tabulate([averages], headers=console_headers, tablefmt="grid"))
print(f"\nRelatório consolidado em PDF '{pdf_output_filename}' gerado com sucesso.")