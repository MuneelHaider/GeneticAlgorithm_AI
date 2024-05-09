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
def create_valid_gene(courses, rooms, professors, sections, timetable, current_day_slots):
    valid = False
    while not valid:
        course = random.choice(courses)
        professor = random.choice([prof for prof in professors if prof.professor_id in course.professor_ids])
        section = random.choice(sections)
        suitable_rooms = [rm for rm in rooms if rm.capacity >= section.student_strength and (course.type == 'lab' if rm.type == 'lab' else True)]

        if not suitable_rooms:
            continue  # Ensures there is a suitable room, else skip to next iteration

        room = random.choice(suitable_rooms)
        # Generate available days excluding adjacent days to any already scheduled
        already_scheduled_days = set(current_day_slots.get((course.course_id, section.section_id), []))
        available_days = set(range(1, 6)) - already_scheduled_days
        # Exclude adjacent days if already scheduled
        for day in already_scheduled_days:
            if day > 1:
                available_days.discard(day - 1)
            if day < 5:
                available_days.discard(day + 1)

        if not available_days:
            continue  # All valid days are taken for this course and section, skip to next iteration

        day_of_week = random.choice(list(available_days))

        # Define time slots ensuring labs are consecutive and theory are spread
        if course.type == 'theory':
            time_slots = sorted(random.sample(range(1, 9), 2))  # Ensures two non-adjacent slots for theory
        else:
            start_time = random.choice([1, 3, 5, 7])  # Consecutive slots for labs
            time_slots = [start_time, start_time + 1]

        valid = True
        for ts in time_slots:
            conflicts = [(professor.professor_id, day_of_week, ts), (room.room_id, day_of_week, ts), (section.section_id, day_of_week, ts)]
            if any(conflict in timetable for conflict in conflicts):
                valid = False
                break

        if valid:
            current_day_slots.setdefault((course.course_id, section.section_id), []).append(day_of_week)

    return [(course.course_id, section.section_id, room.room_id, professor.professor_id, day_of_week, ts) for ts in time_slots]



def initialize_population(pop_size, courses, sections, rooms, professors):
    population = []
    for _ in range(pop_size):
        timetable = set()
        current_day_slots = {}
        while len(timetable) < len(courses) * 2:
            genes = create_valid_gene(courses, rooms, professors, sections, timetable, current_day_slots)
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

def mutate(individual, courses, rooms, professors, mutation_rate=0.02, current_day_slots=None):
    for index in range(len(individual)):
        if random.random() < mutation_rate:
            gene = individual[index]
            course_id, section_id, room_id, professor_id, day, time_slot = gene
            new_day = day  # Potential day change logic can be introduced here
            new_time_slot = random.choice(range(1, 9))
            
            new_gene = (course_id, section_id, room_id, professor_id, new_day, new_time_slot)
            
            if not check_hard_constraints(new_gene, individual, professors, rooms):
                individual[index] = new_gene
                # Update day slots tracking if day changed:
                if new_day != day:
                    if current_day_slots:
                        current_day_slots[(course_id, section_id)].remove(day)
                        current_day_slots[(course_id, section_id)].append(new_day)



def check_hard_constraints(gene, timetable, professors, rooms):
    course_id, section_id, room_id, professor_id, day, time_slot = gene
    for g in timetable:
        if g != gene and (g[3] == professor_id and g[4] == day and g[5] == time_slot):
            return False
    return True

def print_timetable(timetable, course_map):
    days_of_week = {1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday'}
    time_slots = {1: '08:30-09:50', 2: '10:00-11:20', 3: '11:30-12:50', 4: '13:00-14:20',
                  5: '14:30-15:50', 6: '16:00-17:20', 7: '17:30-18:50', 8: '19:00-20:20'}
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

# Main Execution
professor_names = ['Ayesha', 'Faisal', 'Hassan', 'Sana', 'Kamran', 'Nadia', 'Usman', 'Asma', 'Bilal', 'Zara', 'Irfan', 'Saima', 'Junaid', 'Hina', 'Ali']
professors = [Professor(f'P{i}', f'{name}', max_courses=random.randint(1, 4)) for i, name in enumerate(professor_names, 1)]

rooms = [Room(f'R{i}', 'classroom', capacity=random.randint(20, 40)) for i in range(1, 11)]
rooms.extend([Room(f'L{i}', 'lab', capacity=random.randint(15, 25)) for i in range(1, 6)])

sections = [Section(f'S{i}', student_strength=random.randint(10, 35)) for i in range(1, 7)]

course_names = [
    'Algorithms', 'Data Structures', 'Operating Systems', 'Network Security', 'Artificial Intelligence',
    'Machine Learning', 'Database Systems', 'Software Engineering', 'Web Development', 'Human-Computer Interaction',
    'Computer Graphics', 'Quantum Computing', 'Cryptography', 'Cloud Computing', 'Big Data Analytics',
    'Computer Vision', 'Bioinformatics', 'Game Development', 'Internet of Things', 'Compiler Construction'
]

courses = []
for i, name in enumerate(course_names, 1):
    course_type = 'lab' if i % 5 == 0 else 'theory'
    professor_ids = random.sample([prof.professor_id for prof in professors], random.randint(1, 3))
    courses.append(Course(f'C{i}', name, course_type, length=90 if course_type == 'theory' else 180, professor_ids=professor_ids))

course_map = {course.course_id: course for course in courses}

population_size = 10
num_generations = 50

best_solution, best_score = genetic_algorithm(
    population_size, courses, sections, rooms, professors, course_map, num_generations
)

print("Best Score:", best_score)
print_timetable(best_solution, course_map)
