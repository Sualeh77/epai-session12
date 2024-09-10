import pytest
from collections import namedtuple
from datetime import datetime
from session12 import type_checked_line, lazy_file_reader, LazyIterable, count_violations
import tempfile
import os

@pytest.fixture
def test_file():
    test_data = [
        "Summons_Number,Plate_ID,Registration_State,Plate_Type,Issue_Date,Violation_Code,Vehicle_Body_Type,Vehicle_Make,Violation_Description\n",
        "1234567,ABC123,NY,PAS,2023-05-15,21,SUBN,FORD,No Parking\n",
        "7654321,XYZ789,NJ,COM,2023-05-16,14,PICK,TOYOTA,Double Parking\n"
    ]
    temp_file = tempfile.NamedTemporaryFile(mode='w+', delete=False)
    temp_file.writelines(test_data)
    temp_file.close()
    yield temp_file.name
    os.unlink(temp_file.name)

def test_type_checked_line():
    Line = namedtuple("Line", ["Summons_Number", "Plate_ID", "Issue_Date"])
    Line.__annotations__ = {"Summons_Number": int, "Plate_ID": str, "Issue_Date": datetime}
    line_data = ["1234567", "ABC123", "2023-05-15"]
    result = type_checked_line(Line, line_data, 0)
    assert result is not None
    assert result.Summons_Number == 1234567
    assert result.Plate_ID == "ABC123"
    assert result.Issue_Date == datetime(2023, 5, 15).date()

def test_lazy_file_reader(test_file):
    reader = lazy_file_reader(test_file)
    lines = list(reader)
    assert len(lines) == 2
    assert lines[0].Summons_Number == 1234567
    assert lines[1].Vehicle_Make == "TOYOTA"

def test_lazy_iterable(test_file):
    li = LazyIterable(test_file)
    lines = list(li)
    assert len(lines) == 2
    assert lines[0].Plate_ID == "ABC123"
    assert lines[1].Registration_State == "NJ"

def test_count_violations(test_file):
    li = LazyIterable(test_file)
    violations = count_violations(li)
    assert violations == {"FORD": 1, "TOYOTA": 1}

