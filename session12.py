from collections import namedtuple
from datetime import datetime
from dateutil import parser
from typing import Type

def type_checked_line(Line:namedtuple, line:list, line_num:int):
    """
    Type-checks and converts the values in a line according to the annotations of a namedtuple.

    Args:
        Line (Type[namedtuple]): The namedtuple class defining the structure and types of the line.
        line (list): The list of values to be type-checked and converted.
        line_num (int): The line number in the file (used for error reporting).

    Returns:
        namedtuple or None: Returns an instance of the Line namedtuple if successful, 
                            or None if there's an error.

    Example:
        Line = namedtuple("Line", ["name", "age", "date"])
        Line.__annotations__ = {"name": str, "age": int, "date": datetime}
        line_data = ["John Doe", "30", "2023-05-15"]
        result = type_checked_line(Line, line_data, 1)
        if result:
            print(f"Name: {result.name}, Age: {result.age}, Date: {result.date}")
    """

    for i, (field, value) in enumerate(zip(Line._fields, line)):
        try:
            if Line.__annotations__[field] == datetime:
                line[i] = parser.parse(value).date()
            else:
                line[i] = Line.__annotations__[field](value)
        except TypeError as e:
            print(f"Type error: {e} at line {line_num+1} for field {field}")
    try:
        return Line(*line)
    except TypeError as e:
        print(f"Error: {e} at line {line_num+1}")
        print(line)
        print(Line._fields)
        return None
    
def lazy_file_reader(file_path:str):
    """
    Lazily reads a file and yields type-checked namedtuple instances for each line.

    This function opens the specified file, reads it line by line, and yields
    type-checked namedtuple instances created from each line's data. It uses
    the type_checked_line function to perform type checking and conversion.

    Args:
        file_path (str): The path to the file to be read.

    Yields:
        namedtuple: A type-checked namedtuple instance for each line in the file.

    Example:
        file_path = "parking_violations.csv"
        for record in lazy_file_reader(file_path):
            if record:
                print(f"Summons Number: {record.Summons_Number}, "
                      f"Plate ID: {record.Plate_ID}, "
                      f"Issue Date: {record.Issue_Date}")
    """
    with open(file_path, 'r', encoding='latin-1') as file:
        headers = next(file)
        Line = namedtuple("Line", [field.replace(" ", "_") for field in headers.strip().split(",")])
        Line.__annotations__ = {
            'Summons_Number': int,
            'Plate_ID': str,
            'Registration_State': str,
            'Plate_Type': str,
            'Issue_Date': datetime,
            'Violation_Code': int,
            'Vehicle_Body_Type': str,
            'Vehicle_Make': str,
            'Violation_Description': str
        }
        
        for line_num, line in enumerate(file):
            yield type_checked_line(Line, line.strip().split(","), line_num)

class LazyIterable:
    """
    A lazy iterable class that reads a file and yields type-checked namedtuple instances.

    This class provides an iterator interface to read a file lazily, processing each line
    according to the annotations of a namedtuple. It uses the lazy_file_reader function
    to perform the actual file reading and type checking.

    Attributes: 
        file_path (str): The path to the file to be read.

    Methods:
        __iter__(): Returns an iterator over the lines in the file.

    Example:
        file_path = "parking_violations.csv"
        li = LazyIterable(file_path)
        for record in li:
            if record:
                print(f"Summons Number: {record.Summons_Number}, "
                      f"Plate ID: {record.Plate_ID}, "
                      f"Issue Date: {record.Issue_Date}")
    """
    def __init__(self, file_path:str):
        self.file_path = file_path

    def __iter__(self):
        return lazy_file_reader(self.file_path)
    

def count_violations(li:LazyIterable):
    """
    Counts the number of violations for each vehicle make in the file.

    This function takes a LazyIterable object, reads the file lazily, and counts
    the number of violations for each vehicle make. It uses the LazyIterable class
    to iterate over the file and process each line.

    Args:
        li (LazyIterable): An instance of the LazyIterable class initialized with the file path.

    Returns:
        dict: A dictionary with vehicle makes as keys and the number of violations as values.

    Example:
        file_path = "parking_violations.csv"
        li = LazyIterable(file_path)    
        violations = count_violations(li)
        print(violations)
    """
    violations = dict()
    for line_num, l in enumerate(li):
        try:
            if l.Vehicle_Make not in violations:
                violations[l.Vehicle_Make] = 0
            violations[l.Vehicle_Make] += 1
        except Exception as e:
            print(f"Exception: {e} for line: {line_num} ")
    return violations

