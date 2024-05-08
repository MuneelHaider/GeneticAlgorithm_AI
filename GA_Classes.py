import random

# Class Definitions
class Course:
    def __init__(self, course_id, name, type, length, professor_ids):
        self.course_id = course_id
        self.name = name
        self.type = type  # 'theory' or 'lab'
        self.length = length
        self.professor_ids = professor_ids

class Professor:
    def __init__(self, professor_id, name, max_courses):
        self.professor_id = professor_id
        self.name = name
        self.max_courses = max_courses

class Room:
    def __init__(self, room_id, type, capacity):
        self.room_id = room_id
        self.type = type  # 'classroom' or 'lab'
        self.capacity = capacity

class Section:
    def __init__(self, section_id, student_strength):
        self.section_id = section_id
        self.student_strength = student_strength

# Genetic Algorithm Functions
def create_valid_gene(courses, rooms, professors, sections, timetable):
    valid = False
    while not valid:
        course = random.choice(courses)
        professor = random.choice([prof for prof in professors if prof.professor_id in course.professor_ids])
        section = random.choice(sections)

        # Check if the course is a lab and assign appropriate room
        if course.type == 'lab':
            suitable_rooms = [rm for rm in rooms if rm.capacity >= section.student_strength and rm.type == 'lab']
        else:
            suitable_rooms = [rm for rm in rooms if rm.capacity >= section.student_strength and rm.type == 'classroom']
        
        if not suitable_rooms:
            continue  # Skip if no suitable room is found

        room = random.choice(suitable_rooms)
        day_of_week = random.randint(1, 5)
        
        if course.type == 'theory':
            possible_slots = list(range(1, 9))
            random.shuffle(possible_slots)
            time_slots = sorted(possible_slots[:2])
        else:
            time_slots = [random.choice([1, 4])]
        
        valid = True
        for ts in time_slots:
            conflicts = [(professor.professor_id, day_of_week, ts), (room.room_id, day_of_week, ts), (section.section_id, day_of_week, ts)]
            if any(conflict in timetable for conflict in conflicts):
                valid = False
                break

    return [(course.course_id, section.section_id, room.room_id, professor.professor_id, day_of_week, ts) for ts in time_slots]



def initialize_population(pop_size, courses, sections, rooms, professors):
    population = []
    for _ in range(pop_size):
        timetable = set()
        while len(timetable) < len(courses) * 2:
            genes = create_valid_gene(courses, rooms, professors, sections, timetable)
            timetable.update(genes)
        population.append(list(timetable))
    return population

def evaluate_timetable(timetable, course_map):
    conflicts = 0
    professor_times = {}
    room_times = {}
    section_times = {}
    for gene in timetable:
        course_id, section_id, room_id, professor_id, day, time_slot = gene
        course = course_map[course_id]
        if (professor_id, day, time_slot) in professor_times:
            conflicts += 10
        if (room_id, day, time_slot) in room_times:
            conflicts += 10
        if (section_id, day, time_slot) in section_times:
            conflicts += 10
        if course.type == 'theory' and time_slot > 4:
            conflicts += 1
        elif course.type == 'lab' and time_slot <= 4:
            conflicts += 1
        professor_times[(professor_id, day, time_slot)] = True
        room_times[(room_id, day, time_slot)] = True
        section_times[(section_id, day, time_slot)] = True
    return -conflicts

def tournament_selection(population, scores, k=3):
    tournament = random.sample(list(zip(population, scores)), k)
    return min(tournament, key=lambda x: x[1])[0]

def single_point_crossover(parent1, parent2, crossover_rate=0.8):
    if random.random() < crossover_rate:
        crossover_point = random.randint(1, len(parent1) - 1)
        child1 = parent1[:crossover_point] + parent2[crossover_point:]
        child2 = parent2[:crossover_point] + parent1[crossover_point:]
        return child1, child2
    return parent1[:], parent2[:]

def mutate(individual, courses, rooms, professors, mutation_rate=0.02):
    for index in range(len(individual)):
        if random.random() < mutation_rate:
            gene = individual[index]
            course_id, section_id, room_id, professor_id, day, time_slot = gene
            course = next(course for course in courses if course.course_id == course_id)
            professor = next(prof for prof in professors if prof.professor_id == professor_id)
            room = next(rm for rm in rooms if rm.room_id == room_id)
            new_time_slot = random.choice(range(1, 9))
            new_gene = (course_id, section_id, room_id, professor_id, day, new_time_slot)
            if not check_hard_constraints(new_gene, individual, professors, rooms):
                individual[index] = new_gene

def check_hard_constraints(gene, timetable, professors, rooms):
    course_id, section_id, room_id, professor_id, day, time_slot = gene
    for g in timetable:
        if g != gene and (g[3] == professor_id and g[4] == day and g[5] == time_slot):
            return False
    return True


def print_timetable(timetable, course_map):
    days_of_week = {1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday'}
    time_slots = {1: '08:00-09:20', 2: '09:30-10:50', 3: '11:00-12:20', 4: '12:30-13:50',
                  5: '14:00-15:20', 6: '15:30-16:50', 7: '17:00-18:20', 8: '18:30-19:50'}
    formatted_timetable = {day: {time: [] for time in time_slots.values()} for day in days_of_week.values()}
    for entry in timetable:
        course_id, section_id, room_id, professor_id, day, time_slot = entry
        course = course_map[course_id]
        day_name = days_of_week[day]
        slot_time = time_slots[time_slot]
        description = f"{course.name} (Section {section_id}, Room {room_id}, Prof {professor_id})"
        formatted_timetable[day_name][slot_time].append(description)
    for day in days_of_week.values():
        print(f"\n{day}")
        for time, courses in formatted_timetable[day].items():
            if courses:
                print(f"  {time}: {', '.join(courses)}")
            else:
                print(f"  {time}: No Class")


def genetic_algorithm(population_size, courses, sections, rooms, professors, course_map, num_generations=100, mutation_rate=0.02):
    population = initialize_population(population_size, courses, sections, rooms, professors)
    best_score = float('inf')
    best_solution = None
    for generation in range(num_generations):
        scores = [evaluate_timetable(timetable, course_map) for timetable in population]
        for i in range(len(scores)):
            if scores[i] < best_score:
                best_score = scores[i]
                best_solution = population[i]
        new_population = [best_solution]  # Elitism
        while len(new_population) < population_size:
            parent1 = tournament_selection(population, scores)
            parent2 = tournament_selection(population, scores)
            child1, child2 = single_point_crossover(parent1, parent2)
            mutate(child1, courses, rooms, professors, mutation_rate)
            mutate(child2, courses, rooms, professors, mutation_rate)
            new_population.extend([child1, child2])
        population = new_population[:population_size]
    return best_solution, best_score






# Generate Professors with Pakistani names
professor_names = ['Ayesha', 'Faisal', 'Hassan', 'Sana', 'Kamran', 'Nadia', 'Usman', 'Asma', 'Bilal', 'Zara', 'Irfan', 'Saima', 'Junaid', 'Hina', 'Ali']
professors = [Professor(f'P{i}', f'{name}', max_courses=random.randint(1, 4)) for i, name in enumerate(professor_names, 1)]

# Generate Rooms (10 classrooms, 5 labs)
rooms = [Room(f'R{i}', 'classroom', capacity=random.randint(20, 40)) for i in range(1, 11)]
rooms.extend([Room(f'L{i}', 'lab', capacity=random.randint(15, 25)) for i in range(1, 6)])

# Generate Sections
sections = [Section(f'S{i}', student_strength=random.randint(10, 35)) for i in range(1, 7)]

# List of computer science courses with corresponding labs
course_names = [
    'Algorithms', 'Data Structures', 'Operating Systems', 'Network Security', 'Artificial Intelligence',
    'Machine Learning', 'Database Systems'
]

# Generate Theory and Corresponding Lab Courses
courses = []
lab_count = 0
for i, name in enumerate(course_names, 1):
    professor_ids_theory = random.sample([prof.professor_id for prof in professors], random.randint(1, 3))
    courses.append(Course(f'C{i*2-1}', f'{name}', 'theory', length=90, professor_ids=professor_ids_theory))
    professor_ids_lab = random.sample(professor_ids_theory, random.randint(1, len(professor_ids_theory)))
    courses.append(Course(f'C{i*2}', f'{name} Lab', 'lab', length=180, professor_ids=professor_ids_lab))

# Additional courses
additional_courses = [
    'Software Engineering', 'Web Development', 'Human-Computer Interaction',
    'Computer Graphics', 'Quantum Computing', 'Cryptography', 'Cloud Computing'
]

for i, name in enumerate(additional_courses, start=len(course_names)+1):
    professor_ids = random.sample([prof.professor_id for prof in professors], random.randint(1, 3))
    courses.append(Course(f'C{i+7}', name, 'theory', length=90, professor_ids=professor_ids))

# Create a course map for easy lookup in the fitness function
course_map = {course.course_id: course for course in courses}

# Define Genetic Algorithm Functions here (create_valid_gene, initialize_population, etc.)

# Genetic Algorithm Execution
population_size = 10
num_generations = 50

best_solution, best_score = genetic_algorithm(
    population_size, courses, sections, rooms, professors, course_map, num_generations
)

# Print the best solution in a formatted timetable
print("Best Score:", best_score)
print_timetable(best_solution, course_map)