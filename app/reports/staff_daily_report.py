from app.reports.student_daily_report import StudentDailyReport

class StaffDailyReport:
    def __init__(self, staff):
        self.staff = staff
        self.students = {}

    def add_result(self, student, result):
        if student.email not in self.students:
            self.students[student.email] = StudentDailyReport(student)

        self.students[student.email].add_result(result)

    def has_results(self):
        return len(self.students) > 0