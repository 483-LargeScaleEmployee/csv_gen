import csv
import os
import random
from enum import Enum
from typing import Dict, List

from gen_sample_name import gen_sample_name


# the sprint is the 2 week period for the current schedule
class SprintDay(Enum):
    DAY_1 = "Monday"
    DAY_2 = "Tuesday"
    DAY_3 = "Wednesday"
    DAY_4 = "Thursday"
    DAY_5 = "Friday"
    DAY_6 = "Saturday"
    DAY_7 = "Sunday"
    DAY_8 = "Next Monday"
    DAY_9 = "Next Tuesday"
    DAY_10 = "Next Wednesday"
    DAY_11 = "Next Thursday"
    DAY_12 = "Next Friday"
    DAY_13 = "Next Saturday"
    DAY_14 = "Next Sunday"

    @classmethod
    def list(cls):
        return list(cls)


# three shifts correspond to 3 times 8 hour shifts = 24 hour coverage
# night is 12am-8am, morning is 8am-4pm, evening is 4pm-12am
# Night, Morning, Evening more readable in csv
class Shift(Enum):
    NIGHT = "Night"
    MORNING = "Morning"
    EVENING = "Evening"

    @classmethod
    def list(cls):
        return list(cls)


# for every day of the 2 week sprint, the employee will have a list of available shifts
# and also a single preferred shift
class EmployeeDay:
    def __init__(self, available_shifts: List[Shift], preferred_shift: Shift, request_day_off: bool):
        self.available_shifts = available_shifts
        self.preferred_shift = preferred_shift
        self.request_day_off = request_day_off


# there will be three employee types
class EmployeeType(Enum):
    NURSE = "Nurse"
    DOCTOR = "Doctor"
    ADMIN = "Admin"

    @classmethod
    def list(cls):
        return list(cls)


class Employee:
    def __init__(self, name: str, employeeType: EmployeeType, employee_days: Dict[SprintDay, EmployeeDay]):
        self.name = name
        self.employeeType = employeeType
        self.employee_days = employee_days


# constraints do not specify num of departments, I'll do 5
class DepartmentType(Enum):
    CARDIOLOGY = "Cardiology"
    PEDIATRICS = "Pediatrics"
    EMERGENCY = "Emergency"
    SURGERY = "Surgery"
    IMMUNOLOGY = "Immunology"

    @classmethod
    def list(cls):
        return list(cls)


class Department:
    def __init__(self, departmentType: DepartmentType, needs):
        self.departmentType = departmentType
        self.needs: Dict[SprintDay, Dict[Shift, Dict[EmployeeType, int]]] = needs


def gen_departments():
    departments = {}
    for departmentType in DepartmentType.list():

        needs = {}
        for sprintDay in SprintDay.list():
            needs[sprintDay] = {}
            for shift in Shift.list():
                needs[sprintDay][shift] = {}
                for employeeType in EmployeeType.list():
                    # for any given day at any given shift, there are a certain # of department needs
                    # randomly generate this number as being 0-3 for each type
                    needs[sprintDay][shift][employeeType] = random.randint(0, 3)

        departments[departmentType] = Department(departmentType, needs)
    return departments


# generate employees which will be able to solve this problem by just generating a large number of them
# in the future, this could be modified to ensure only a single solution, maybe no solution, etc.
def gen_employees():
    employees = []
    for _ in range(100):
        employee_days = {}
        for sprintDay in SprintDay.list():
            available_shifts = random.sample(Shift.list(), random.randint(1, 3))
            preferred_shift = random.choice(available_shifts)
            request_day_off = random.randint(1, 100) <= 25  # 25% chance of requesting day off on any given day
            employee_days[sprintDay] = EmployeeDay(available_shifts, preferred_shift, request_day_off)

        employees.append(Employee(gen_sample_name(), random.choice(EmployeeType.list()), employee_days))
    return employees


# first col is employee name, then employee type, then 14 sprint days
def write_employees(gen_number, employees):
    with open(f"target/{gen_number}/employees.csv", mode="w", newline="") as employee_file:
        employee_writer = csv.writer(employee_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        employee_writer.writerow(["Name", "Type"] + [sprintDay.value for sprintDay in SprintDay.list()])
        for employee in employees:
            row = [employee.name, employee.employeeType.value]  # Use .value to get the string
            for sprintDay in SprintDay.list():
                employeeDay = employee.employee_days[sprintDay]
                row.append(
                    f"{[ed.value for ed in employeeDay.available_shifts]} {employeeDay.preferred_shift.value} {employeeDay.request_day_off}"
                )
            employee_writer.writerow(row)


# each department will be written in a different file, with department_name.csv
def write_departments(gen_number, departments):
    for department in departments.values():
        with open(
            f"target/{gen_number}/{department.departmentType.value}.csv", mode="w", newline=""
        ) as department_file:
            department_writer = csv.writer(department_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
            department_writer.writerow(["Sprint Day", "Shift"] + [et.value for et in EmployeeType.list()])
            for sprintDay in SprintDay.list():
                for shift in Shift.list():
                    row = [sprintDay.value, shift.value]  # Use .value to get the string
                    for employeeType in EmployeeType.list():
                        row.append(department.needs[sprintDay][shift][employeeType])
                    department_writer.writerow(row)


def main():
    departments = gen_departments()
    employees = gen_employees()

    os.makedirs("target", exist_ok=True)

    # saving the gen_number for better collaboration and testing
    # cur gen number is the highest num in target + 1
    gen_number = 0
    for file in os.listdir("target"):
        if file.endswith(".csv"):
            gen_number = max(gen_number, int(file.split(".")[0]) + 1)

    os.makedirs(f"target/{gen_number}", exist_ok=False)

    write_employees(gen_number, employees)
    write_departments(gen_number, departments)


if __name__ == "__main__":
    main()
