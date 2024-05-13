import random
import pandas as pd

# Muneel Haider
# i21-0640
# AI Project

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
        self.courses = [Course("Operating Systems"), Course("Database Systems"), Course("Algorithms"),
                        Course("Data Structures"), Course("Software Engineering"),
                        Course("Operating Systems Lab", True), Course("Database Systems Lab", True)]
        self.professors = [Professor("Dr. Labiba"), Professor("Sir Aadil"),
                           Professor("Ma'am Sidra"), Professor("Sir Usman"), Professor("Dr. Mehreen")]
        self.sections = [Section(name) for name in ["A", "B", "C", "D", "E", "F"]]
        self.classrooms = [Classroom("D-101", 60), Classroom("D-102", 100)]
        self.timeslots = [Timeslot("8:30-9:50"), Timeslot("10:00-11:20"), Timeslot("11:30-12:50"),
                          Timeslot("1:00-2:20"), Timeslot("2:30-3:50"), Timeslot("4:00-5:20")]
        self.days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        self.populationSize = 50
        self.generations = 100
        self.labsAllotted = {section.name: set() for section in self.sections}

    def encode(self, chromosome):
        encoded = ''
        for day, allocations in chromosome.items():
            for allocation in allocations:
                encoded += f"{self.courses.index(allocation[0]):08b}"
                encoded += f"{self.sections.index(allocation[1]):08b}"
                encoded += f"{self.timeslots.index(allocation[2]):08b}"
                encoded += f"{self.classrooms.index(allocation[3]):08b}"
                encoded += f"{self.professors.index(allocation[4]):08b}"
        return encoded

    def decode(self, encoded):
        step = 40  # Each allocation represented by 40 bits
        chromosome = {day: [] for day in self.days}
        for i in range(0, len(encoded), step):
            course_idx = int(encoded[i:i+8], 2)
            section_idx = int(encoded[i+8:i+16], 2)
            timeslot_idx = int(encoded[i+16:i+24], 2)
            classroom_idx = int(encoded[i+24:i+32], 2)
            professor_idx = int(encoded[i+32:i+40], 2)

            course = self.courses[course_idx]
            section = self.sections[section_idx]
            timeslot = self.timeslots[timeslot_idx]
            classroom = self.classrooms[classroom_idx]
            professor = self.professors[professor_idx]

            # Random assignment; adapt if needed
            day = random.choice(self.days)
            chromosome[day].append((course, section, timeslot, classroom, professor))
        return chromosome


    def checkConstraints(self, proposed, existing):
        for alreadyAllotted in existing:
            if proposed[2] == alreadyAllotted[2]:  # Check timeslot conflicts
                if proposed[4] == alreadyAllotted[4] or proposed[3] == alreadyAllotted[3]:  # Check professor or room conflicts
                    return False
        return True
    

    def initializePopulation(self):
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
                    for i in range(len(availableTimeslots) - 1 if course.isLab else len(availableTimeslots)):
                        timeslot = availableTimeslots[i]
                        nextTimeslot = availableTimeslots[i + 1] if course.isLab and i < len(availableTimeslots) - 1 else None
                        if course.isLab and nextTimeslot and self.checkConstraints((course, section, timeslot, room, professor), chromosome[day]) and self.checkConstraints((course, section, nextTimeslot, room, professor), chromosome[day]):
                            if course.name not in self.labsAllotted[section.name]:
                                chromosome[day].append((course, section, timeslot, room, professor))
                                chromosome[day].append((course, section, nextTimeslot, room, professor))
                                coursesCount[section.name] += 1
                                self.labsAllotted[section.name].add(course.name)
                                break
                        elif not course.isLab and self.checkConstraints((course, section, timeslot, room, professor), chromosome[day]):
                            chromosome[day].append((course, section, timeslot, room, professor))
                            coursesCount[section.name] += 1
        return chromosome



    def calculateFitness(self, chromosome):
        fitness = 0
        for day, allocations in chromosome.items():
            for allocation in allocations:
                # Check each allocation against all others on the same day
                conflicts = sum(1 for other in allocations if not self.checkConstraints(allocation, [other]) and other != allocation)
                fitness += conflicts
        return -fitness  # Return negative of the conflict count to signify that lower is better


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
        population = [self.encode(self.initializePopulation()) for _ in range(self.populationSize)]
        
        for generation in range(self.generations):
            decoded_population = [self.decode(individual) for individual in population]
            sortedPopulation = sorted(decoded_population, key=self.calculateFitness, reverse=True)
            population = [self.encode(individual) for individual in sortedPopulation[:2]]


            while len(population) < self.populationSize:
                parents = random.sample(population, 2)
                child = self.crossover(self.decode(parents[0]), self.decode(parents[1]))
                mutated_child = self.mutate(self.decode(self.encode(child)))
                population.append(self.encode(mutated_child))

            
        best_timetable = self.decode(population[0])
        return best_timetable



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
