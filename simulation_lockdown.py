import enum
import random
from PIL import Image

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
       
        # lockdown variant
        
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

    def printReport(self, report):
        for cases in report:
            print(cases, '\t', end=' ')
        print()

    def logHeaders(self, verbose):
        if verbose:
            for state in State:
                print(state.name, '\t', end=' ')
            print()

    def logReport(self, verbose):
        if verbose:
            report = self.report()
            self.printReport(report)

    def simulation(self, generations, verbose):
        self.logHeaders(verbose)
        self.logReport(verbose)

        for _ in range(generations):
            self.nextGeneration()
            self.logReport(verbose)

    def numberOfDeaths(self):
        return sum(1 for row in self.population for individual in row if individual.state == State.dead)

    def printImage(self, name):
        lines = len(self.population)
        columns = len(self.population[0])
        img = Image.new("RGB", (columns, lines))

        for i in range(lines):
            for j in range(columns):
                state = self.population[i][j].state
                if state == State.healthy:
                    img.putpixel((j, i), (0, 255, 0))
                elif state == State.sick:
                    img.putpixel((j, i), (255, 255, 0))
                elif state == State.dead:
                    img.putpixel((j, i), (255, 0, 0))
                elif state == State.immune:
                    img.putpixel((j, i), (0, 0, 255))
                elif state == State.asymptomatic:
                    img.putpixel((j, i), (255, 0, 255))

        img.save(f"./images/simulation-{name}.png")
        img.show()

# =======================
#         MAIN
# =======================

numberOfRuns = 1              # Número de vezes em que a simulação é executada
gridSize = 156                 # Tamanho da matriz (156x156) ~= 24.500 pessoas
numberOfGenerations = 51      # Quantidade de semanas (51 por que o zero conta) 52 * 7 = 365 dias (1 ano) 
saveImages = True             # Salvar imagens? True ou False
verbose = True               # Mostrar detalhes no console? True ou False

# 🟢 Verde: saudável
# 🟡 Amarelo: doente
# 🔴 Vermelho: morto
# 🔵 Azul: imune
# 🟣 Roxo: assintomático

for i in range(numberOfRuns):
    print(f"Simulação {i + 1}")
    model = RandomWalkModel(gridSize)
    model.simulation(numberOfGenerations, verbose)
    print("Mortes:", model.numberOfDeaths())
    if saveImages:
        model.printImage(i)
