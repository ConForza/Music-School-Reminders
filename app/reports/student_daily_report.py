class StudentDailyReport:

    def __init__(self, student):
        self.student = student
        self.lesson_results = []

    def add_result(self, result):
        self.lesson_results.append(result)

    def applied_results(self):
        return [result for result in self.lesson_results if result.status == "applied"]

    def problem_results(self):
        return [result for result in self.lesson_results if result.status != "applied"]
