import random
import pandas as pd

#   Muneel Haider
#   i210640
#   AI - Project

class Course:
    def __init__(self, name, isLab=False):
        self.name = name
        self.isLab = isLab

class Professor:
    def __init__(self, name):
        self.name = name

class Section:
    def __init__(self, name):
        self.name = name

class Classroom:
    def __init__(self, code, capacity):
        self.code = code
        self.capacity = capacity

class Timeslot:
    def __init__(self, startTime):
        self.startTime = startTime

class TimetableSystem:
    def __init__(self):
        
        self.courses = [
            Course("Operating Systems"), Course("Database Systems"), Course("Algorithms"), Course("Data Structures"), Course("Software Engineering"), Course("Operating Systems Lab", True), Course("Database Systems Lab", True)
        ]
        self.professors = [
            Professor("Dr. Labiba"), Professor("Sir Aadil"), Professor("Ma'am Sidra"), Professor("Sir Usman"), Professor("Dr. Mehreen")
        ]
        self.sections = [Section(name) for name in ["A", "B", "C", "D", "E", "F"]]
        self.classrooms = [Classroom("D-101", 60), Classroom("D-102", 100)]
        
        self.timeslots = [
            Timeslot("8:30-9:50"), Timeslot("10:00-11:20"), Timeslot("11:30-12:50"), Timeslot("1:00-2:20"), Timeslot("2:30-3:50"), Timeslot("4:00-5:20")
        ]
        
        self.days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        self.populationSize = 50
        self.generations = 100
        
        self.labsAllotted = {section.name: [] for section in self.sections}
        
        chromosome = {day: [] for day in self.days}


    def checkConstraints(self, indexAllotted, already):
        
        for alreadyAllotted in already:
        
            if indexAllotted[2] == alreadyAllotted[2]:  
                if indexAllotted[4] == alreadyAllotted[4]:  
                    return False
        
                if indexAllotted[3] == alreadyAllotted[3]:
                    return False
        return True



    def initializePopulation(self):
        
        self.labsAllotted = {section.name: set() for section in self.sections}  

        chromosome = {day: [] for day in self.days}
        maxCoursesPerDay = 3  

        for day in chromosome:
            coursesCount = {section.name: 0 for section in self.sections}  

            for section in self.sections:

                randomCourses = random.sample(self.courses, len(self.courses))  

                for course in randomCourses:

                    if coursesCount[section.name] >= maxCoursesPerDay:
                        continue  

                    availableRooms = [room for room in self.classrooms if room.capacity >= (120 if course.isLab else 60)]
                    
                    if not availableRooms:
                        availableRooms = self.classrooms  

                    availableTimeslots = self.timeslots[:-1] if course.isLab else self.timeslots 
                    room = random.choice(availableRooms)
                    professor = random.choice(self.professors)

                    if course.isLab:
                        if course.name in self.labsAllotted[section.name]:
                            continue  

                        for i in range(len(availableTimeslots) - 1):  

                            timeslot = availableTimeslots[i]
                            nextTimeslot = availableTimeslots[i + 1]

                            if self.checkConstraints((course, section, timeslot, room, professor), chromosome[day]) and \
                            self.checkConstraints((course, section, nextTimeslot, room, professor), chromosome[day]):
                            
                                chromosome[day].append((course, section, timeslot, room, professor))
                                chromosome[day].append((course, section, nextTimeslot, room, professor))
                                coursesCount[section.name] += 1  
                                self.labsAllotted[section.name].add(course.name)  
                                break
                    else:
                        timeslot = random.choice(availableTimeslots)

                        if self.checkConstraints((course, section, timeslot, room, professor), chromosome[day]):
                            chromosome[day].append((course, section, timeslot, room, professor))
                            coursesCount[section.name] += 1
        return chromosome



    def calculateFitness(self, chromosome):
        
        fitness = 0
        
        for day, allocations in chromosome.items():
            for allocation in allocations:
        
                if self.checkConstraints(allocation, allocations):
                    fitness += 1
        return fitness

    def mutate(self, chromosome):
        
        day = random.choice(self.days)
        
        if chromosome[day]:  
            indexAllocation = random.randint(0, len(chromosome[day]) - 1)
            allocation = chromosome[day][indexAllocation]
            newTimeslot = random.choice(self.timeslots)

            newAllocation = (allocation[0], allocation[1], newTimeslot, allocation[3], allocation[4])

            if self.checkConstraints(newAllocation, chromosome[day]):
                chromosome[day][indexAllocation] = newAllocation
 
        return chromosome


    def crossover(self, parent1, parent2):
 
        preChild = random.randint(0, len(self.days))
        child = {day: (parent1 if i < preChild else parent2)[day] for i, day in enumerate(self.days)}
 
        return child

    def geneticAlgorithm(self):
        population = [self.initializePopulation() for _ in range(self.populationSize)]
 
        for generation in range(self.generations):
            sortedPopulation = sorted(population, key=self.calculateFitness, reverse=True)
            population = sortedPopulation[:2]  
 
            while len(population) < self.populationSize:
 
                parent1, parent2 = random.sample(sortedPopulation, 2)
                child = self.crossover(parent1, parent2)
                child = self.mutate(child)
                population.append(child)
 
            print(f"Generation {generation}: Best Fitness = {self.calculateFitness(sortedPopulation[0])}")
 
        return sortedPopulation[0]

    def saveCSV(self, bestTimetable):
 
        for day, allocations in bestTimetable.items():
            df = pd.DataFrame('-', index=[room.code for room in self.classrooms], columns=[ts.startTime for ts in self.timeslots])
 
            for allocation in allocations:
                course, section, timeslot, room, professor = allocation
                df.at[room.code, timeslot.startTime] = f"{course.name} - {section.name} ({professor.name})"
 
            df.to_csv(f"{day}_timetable.csv")
            print(f"Timetable for {day} saved to '{day}_timetable.csv'.")

timetable = TimetableSystem()
bestTimetable = timetable.geneticAlgorithm()
timetable.saveCSV(bestTimetable)
