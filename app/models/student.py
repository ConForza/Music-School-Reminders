class Student:

    def __init__(self, first_name, surname, email):
        self.first_name = first_name
        self.surname = surname
        self.email = email
        self.lessons = []

    def add_lesson(self, lesson):
        self.lessons.append(lesson)

    def unpaid_lessons(self):
        return [lesson for lesson in self.lessons if lesson.is_unpaid()]
