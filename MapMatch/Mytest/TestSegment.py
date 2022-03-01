class Employee:
    def __init__(self, name, salary):
        self.__name = name
        self.__salary = salary

    @property
    def salary(self):
        return self.__salary

    @salary.setter
    def salary(self, salary):
        self.__salary = salary

    def __str__(self):
        return "__str__emploee"

    def __repr__(self):
        return '__repr__'


emp1 = Employee('lisi', 1000)
print(emp1)
# print(emp1.salary)
# emp1.salary = 2000
# print(emp1.salary)





























