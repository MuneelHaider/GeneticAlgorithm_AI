import random
import csv

# THIS CODE DOES NOT RUN, JUST FOR GENERAL IDEA

class Course:
    def __init__(self, course_id, name, is_lab, professor_ids):
        self.course_id = course_id
        self.name = name
        self.is_lab = is_lab
        self.professor_ids = professor_ids

class Professor:
    def __init__(self, professor_id, name):
        self.professor_id = professor_id
        self.name = name
        self.courses_taught = []

class Room:
    def __init__(self, room_id, capacity):
        self.room_id = room_id
        self.capacity = capacity

class Section:
    def __init__(self, section_id, student_strength, max_courses=5):
        self.section_id = section_id
        self.student_strength = student_strength
        self.max_courses = max_courses
        self.courses = []

def initialize_population(pop_size, courses, sections, rooms, professors):
    population = []
    for _ in range(pop_size):
        chromosome = []
        for course in courses:
            for section in sections:
                if len(section.courses) >= section.max_courses:
                    continue
                suitable_rooms = [room for room in rooms if room.capacity >= section.student_strength]
                suitable_professors = [prof for prof in professors if len(prof.courses_taught) < 3 and course.course_id not in prof.courses_taught]

                if not suitable_rooms or not suitable_professors:
                    continue

                for _ in range(2 if not course.is_lab else 1):
                    room = random.choice(suitable_rooms)
                    professor = random.choice(suitable_professors)
                    available_days = list(set(range(1, 6)) - set([g['day'] for g in chromosome if g['section_id'] == section.section_id]))

                    if not available_days:
                        continue

                    day = random.choice(available_days)
                    if course.is_lab:
                        start_slot = random.choice([1, 3, 5])
                        time_slots = [start_slot, start_slot + 1]
                    else:
                        time_slots = random.sample(range(1, 9), 2)

                    for time_slot in time_slots:
                        gene = {
                            'course_id': course.course_id,
                            'section_id': section.section_id,
                            'room_id': room.room_id,
                            'professor_id': professor.professor_id,
                            'day': day,
                            'time_slot': time_slot
                        }
                        chromosome.append(gene)
                        professor.courses_taught.append(course.course_id)
                        section.courses.append(course.course_id)

        if chromosome:
            population.append(chromosome)

    return population

def evaluate_timetable(timetable):
    conflicts = 0
    professor_times = {}
    room_times = {}
    section_times = {}

    for gene in timetable:
        course_id, section_id, room_id, professor_id, day, time_slot = gene

        if (professor_id, day, time_slot) in professor_times:
            conflicts += 10
        if (room_id, day, time_slot) in room_times:
            conflicts += 10
        if (section_id, day, time_slot) in section_times:
            conflicts += 10

        professor_times[(professor_id, day, time_slot)] = True
        room_times[(room_id, day, time_slot)] = True
        section_times[(section_id, day, time_slot)] = True

    return -conflicts

def tournament_selection(population, scores, k=3):
    selected_index = random.randint(0, len(population) - 1)
    for _ in range(k - 1):
        index = random.randint(0, len(population) - 1)
        if scores[index] < scores[selected_index]:
            selected_index = index
    return population[selected_index]

def crossover(parent1, parent2, crossover_rate=0.8):
    min_length = min(len(parent1), len(parent2))
    if random.random() < crossover_rate and min_length > 1:
        point = random.randint(1, min_length - 1)
        child1 = parent1[:point] + parent2[point:]
        child2 = parent2[:point] + parent1[point:]
        return child1, child2
    return parent1.copy(), parent2.copy()

def mutate(chromosome, mutation_rate=0.02):
    for gene in chromosome:
        if random.random() < mutation_rate:
            gene['day'] = random.choice(range(1, 6))
            gene['time_slot'] = random.choice(range(1, 9))

def genetic_algorithm(population_size, num_generations, courses, sections, rooms, professors):
    population = initialize_population(population_size, courses, sections, rooms, professors)
    scores = [evaluate_timetable(chromosome) for chromosome in population]
    best_index = scores.index(max(scores))
    best = population[best_index]

    for generation in range(num_generations):
        new_population = []
        while len(new_population) < len(population):
            parent1 = tournament_selection(population, scores)
            parent2 = tournament_selection(population, scores)
            if len(parent1) > 1 and len(parent2) > 1:
                child1, child2 = crossover(parent1, parent2)
                mutate(child1)
                mutate(child2)
                new_population.extend([child1, child2])
            else:
                new_population.extend([parent1.copy(), parent2.copy()])
        population = new_population
        scores = [evaluate_timetable(chromosome) for chromosome in population]
        current_best_index = scores.index(max(scores))
        if scores[current_best_index] > scores[best_index]:
            best_index = current_best_index
            best = population[best_index]

    return best

def write_day_timetable_to_csv(schedule, day, file_path):
    with open(f"{day.lower()}.csv", mode='w', newline='') as file:
        writer = csv.writer(file)
        headers = ['Time Slot', day]
        writer.writerow(headers)
        for time_slot, entries in schedule.items():
            row = [time_slot] + [', '.join(entries[day]) if entries[day] else "No Class"]
            writer.writerow(row)

def process_and_output_timetable(timetable, course_map, professor_map):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    time_slots = {
        1: '08:30-09:50', 2: '10:00-11:20', 3: '11:30-12:50', 4: '13:00-14:20',
        5: '14:30-15:50', 6: '16:00-17:20', 7: '17:30-18:50', 8: '19:00-20:20'
    }
    schedule = {time: {day: [] for day in days} for time in time_slots.values()}

    for gene in timetable:
        day_index = days[gene['day'] - 1]
        time_slot_label = time_slots[gene['time_slot']]
        course = course_map[gene['course_id']]
        professor = professor_map[gene['professor_id']]
        section_id = gene['section_id']
        description = f"{course.name} - Sec {section_id}, Room {gene['room_id']}, Prof {professor.name}"
        schedule[time_slot_label][day_index].append(description)

    for day in days:
        write_day_timetable_to_csv(schedule, day, f"{day.lower()}.csv")

    for time_slot, day_info in schedule.items():
        print(f"{time_slot:<15}", end="")
        for day in days:
            descriptions = ', '.join(day_info[day]) if day_info[day] else "No Class"
            print(f"| {descriptions}", end="")
        print()

professor_names = [
    'Ayesha', 'Faisal', 'Hassan', 'Sana', 'Kamran', 'Nadia', 'Usman', 'Asma', 'Bilal', 'Zara',
    'Irfan', 'Saima', 'Junaid', 'Hina', 'Ali'
]

course_names = [
    'Algorithms', 'Data Structures', 'Operating Systems', 'Network Security', 'Artificial Intelligence',
    'Machine Learning', 'Database Systems', 'Software Engineering', 'Web Development', 'Human-Computer Interaction',
    'Computer Graphics', 'Quantum Computing', 'Cryptography', 'Cloud Computing', 'Big Data Analytics',
    'Computer Vision', 'Bioinformatics', 'Game Development', 'Internet of Things', 'Compiler Construction'
]

professors = [Professor(f'P{i+1}', name) for i, name in enumerate(professor_names)]

lab_indices = random.sample(range(20), 7)
courses = []
for i, name in enumerate(course_names):
    is_lab = i in lab_indices
    professor_ids = random.sample([prof.professor_id for prof in professors], random.randint(1, 3))
    courses.append(Course(f'C{i+1}', name, is_lab, professor_ids))

sections = [Section(f'S{i+1}', random.randint(10, 35)) for i in range(10)]
rooms = [Room(f'R{i+1}', 60 if i < 8 else 120) for i in range(12)]
course_map = {course.course_id: course for course in courses}
professor_map = {prof.professor_id: prof for prof in professors}

best_solution = genetic_algorithm(10, 50, courses, sections, rooms, professors)
process_and_output_timetable(best_solution, course_map, professor_map)
