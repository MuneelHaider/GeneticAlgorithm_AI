import random
import csv

# Muneel Haider
# i21-0640
# AI Project

class Course:

    def __init__(self, courseID, name, isLab, professorIDs):
        self.courseID = courseID
        self.name = name 
        self.isLab = isLab
        self.professorIDs = professorIDs

class Professor:
    def __init__(self, professorID, name):
        self.professorID = professorID
        self.name = name
        self.coursesTeaching = []

class Room:
    def __init__(self, roomID, capacity):
        self.roomID = roomID
        self.capacity = capacity

class Section:
    def __init__(self, sectionID, strength, maxCourses=5):
        self.sectionID = sectionID
        self.strength = strength
        self.maxCourses = maxCourses  
        self.courses = []  


def initializePopulation(populationSize, courses, sections, rooms, professors):
    population = []

    for _ in range(populationSize):

        chromosome = []
        sortedCourses = sorted(courses, key=lambda x: x.isLab, reverse=True)
        
        for course in sortedCourses:
            for section in sections:
        
                if len(section.courses) >= section.maxCourses:
                    continue
        
                availableRooms = [room for room in rooms if room.capacity >= section.strength]
                availableProfessors = [prof for prof in professors if course.courseID not in prof.coursesTeaching and len(prof.coursesTeaching) < 3]

                if not availableRooms or not availableProfessors:
                    continue

                freeDays = list(set(range(1, 6)) - set([g['day'] for g in chromosome if g['sectionID'] == section.sectionID]))
        
                if not freeDays:
                    continue

                room = random.choice(availableRooms)
                professor = random.choice(availableProfessors)
                day = random.choice(freeDays)

                if course.isLab:
        
                    labSlots = [1, 3, 5]
                    
                    for startSlot in labSlots:
                        
                        if all(not any(g for g in chromosome if g['day'] == day and g['timeSlot'] == slot) for slot in [startSlot, startSlot + 1]):
                            genes = []

                            for offset in range(2):
                                gene = {
                                    'courseID': course.courseID,
                                    'sectionID': section.sectionID,
                                    'roomID': room.roomID,
                                    'professorID': professor.professorID,
                                    'day': day,
                                    'timeSlot': startSlot + offset
                                }
                                genes.append(gene)
                            
                            chromosome.extend(genes)
                            professor.coursesTeaching.append(course.courseID)
                            section.courses.append(course.courseID)
                            break
                else:
                    timeSlot = random.sample(range(1, 7), 2)

                    for timeSlot in timeSlot:
                        gene = {
                            'courseID': course.courseID,
                            'sectionID': section.sectionID,
                            'roomID': room.roomID,
                            'professorID': professor.professorID,
                            'day': day,
                            'timeSlot': timeSlot
                        }
                        chromosome.append(gene)
                        professor.coursesTeaching.append(course.courseID)
                        section.courses.append(course.courseID)

        if chromosome:
            population.append(chromosome)

    return population


# Fitness Function
def timetableFitness(timetable):
    conflicts = 0
    professorTimings = {}
    roomTimings = {}
    sectionTimings = {}

    for gene in timetable:
        courseID, sectionID, roomID, professorID, day, timeSlot = gene

        # Hard constraints
        if (professorID, day, timeSlot) in professorTimings:
            conflicts += 10

        if (roomID, day, timeSlot) in roomTimings:
            conflicts += 10

        if (sectionID, day, timeSlot) in sectionTimings:
            conflicts += 10

        professorTimings[(professorID, day, timeSlot)] = True
        roomTimings[(roomID, day, timeSlot)] = True
        sectionTimings[(sectionID, day, timeSlot)] = True

    return -conflicts

def tournamentSelection(population, scores, k=3):
    selected_index = random.randint(0, len(population) - 1)

    for _ in range(k - 1):
        index = random.randint(0, len(population) - 1)

        if scores[index] < scores[selected_index]:
            selected_index = index

    return population[selected_index]

def crossover(parent1, parent2, crossoverRate=0.8):
    minimumLength = min(len(parent1), len(parent2))

    if random.random() < crossoverRate and minimumLength > 1:
        point = random.randint(1, minimumLength - 1)
        child1 = parent1[:point] + parent2[point:]
        child2 = parent2[:point] + parent1[point:]
        return child1, child2

    return parent1.copy(), parent2.copy()


# Mutation Function
def mutation(chromosome, mutationRate=0.02):

    for gene in chromosome:

        if random.random() < mutationRate:
            gene['day'] = random.choice(range(1, 6))
            gene['timeSlot'] = random.choice(range(1, 9))

def GAlgorithm(populationSize, generations, courses, sections, rooms, professors):

    population = initializePopulation(populationSize, courses, sections, rooms, professors)
    scores = [timetableFitness(chromosome) for chromosome in population]
    bestScoreIndex = scores.index(max(scores))
    best = population[bestScoreIndex]

    for generation in range(generations):
  
        newPopulation = []
  
        while len(newPopulation) < len(population):
  
            parent1 = tournamentSelection(population, scores)
            parent2 = tournamentSelection(population, scores)
  
            if len(parent1) > 1 and len(parent2) > 1: 
                child1, child2 = crossover(parent1, parent2)
                mutation(child1)
                mutation(child2)
                newPopulation.extend([child1, child2])

            else:
                newPopulation.extend([parent1.copy(), parent2.copy()])

        population = newPopulation
        scores = [timetableFitness(chromosome) for chromosome in population]
        currentScoreIndex = scores.index(max(scores))

        if scores[currentScoreIndex] > scores[bestScoreIndex]:

            bestScoreIndex = currentScoreIndex
            best = population[bestScoreIndex]

    print(f"Generation {generations - 1}: Best Score = {scores[bestScoreIndex]}")

    return best

def outputCSV(timetable, courseDict, professorDict):

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    timeSlot = {
        1: '08:30-09:50', 2: '10:00-11:20', 3: '11:30-12:50', 4: '13:00-14:20',
        5: '14:30-15:50', 6: '16:00-17:20'
    }
    
    for dayIndex, dayName in enumerate(days, start=1):

        with open(f'{dayName.lower()}.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Time Slot', 'Class Details'])
        
            for timeSlotIndex in range(1, 7):

                timeSlott = timeSlot[timeSlotIndex]
                entries = [
                    f"{courseDict[g['courseID']].name} - Section {g['sectionID']}, Room {g['roomID']}, Prof {professorDict[g['professorID']].name}"
                    for g in timetable
                    if g['day'] == dayIndex and g['timeSlot'] == timeSlotIndex
                ]
                writer.writerow([timeSlott, "  --|--   ".join(entries) if entries else "No Class"])


def program():
    
    professorNames = [
        'Ayesha', 'Faisal', 'Hassan', 'Sana', 'Kamran', 'Nadia', 'Usman'
    ]

    courseNames = [
        'Algorithms', 'Data Structures', 'Operating Systems', 'Network Security', 
        'Artificial Intelligence', 'Machine Learning'
    ]

    labCourseNames = [
        'Computer Vision Lab', 'Game Development Lab', 
        'Internet of Things Lab'
    ]

    professors = [Professor(f'P{i+1}', name) for i, name in enumerate(professorNames)]

    courses = [Course(f'C{i+1}', name, False, random.sample([prof.professorID for prof in professors], random.randint(1, 3))) for i, name in enumerate(courseNames)]
    labCourses = [Course(f'L{i+1}', name, True, random.sample([prof.professorID for prof in professors], random.randint(1, 3))) for i, name in enumerate(labCourseNames)]

    sections = [Section(f'S{i+1}', random.randint(10, 35)) for i in range(4)]
    rooms = [Room(f'R{i+1}', 60 if i < 8 else 120) for i in range(12)]  
    
    courseDict = {course.courseID: course for course in courses + labCourses}
    professorDict = {prof.professorID: prof for prof in professors}

    best_solution = GAlgorithm(10, 50, courses + labCourses, sections, rooms, professors)
    outputCSV(best_solution, courseDict, professorDict)


if __name__ == '__main__':
    program()