from django.db import models

class Student(models.Model):
    Roll_No = models.CharField(max_length=20, unique=True, primary_key=True)
    Name = models.CharField(max_length=100)
    Dept = models.CharField(max_length=100)
    Year = models.IntegerField()
    Semester = models.IntegerField()
    Joined_Year = models.IntegerField()
    Passed_Out_Year = models.IntegerField(null=True, blank=True)
    password = models.CharField(max_length=100, default='student123')

    def __str__(self):
        return f"{self.Roll_No} - {self.Name}"
    
    class Meta:
        db_table = 'Student'

class AcademicPerformance(models.Model):
    Roll_No = models.CharField(max_length=20)
    Dept = models.CharField(max_length=100)
    Semester = models.IntegerField()

    Thesis_Work = models.IntegerField(null=True, blank=True)
    Seminar = models.IntegerField(null=True, blank=True)
    Internship = models.IntegerField(null=True, blank=True)
    Project_Presentation = models.IntegerField(null=True, blank=True)

    SGPA = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    CGPA = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    Backlogs = models.IntegerField(default=0)

    AI_Applications = models.IntegerField(null=True, blank=True)
    Cloud_Computing = models.IntegerField(null=True, blank=True)
    Embedded_Systems = models.IntegerField(null=True, blank=True)
    Cybersecurity = models.IntegerField(null=True, blank=True)
    Deep_Learning = models.IntegerField(null=True, blank=True)
    IoT_Systems = models.IntegerField(null=True, blank=True)
    Big_DataAnalytics = models.IntegerField(null=True, blank=True)

    Optimization_Techniques = models.IntegerField(null=True, blank=True)
    Advanced_Algorithms = models.IntegerField(null=True, blank=True)
    Machine_Learning = models.IntegerField(null=True, blank=True)
    Data_Analytics = models.IntegerField(null=True, blank=True)
    Research_Methodology = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'Academic_Performance_final' 

    def __str__(self):
        return f"{self.Roll_No} - Sem {self.Semester}"


class AttendanceRecord(models.Model):
    id = models.AutoField(primary_key=True)
    Roll_No = models.CharField(max_length=20)
    Dept = models.CharField(max_length=100)
    Semester = models.IntegerField()
    Attendance_Percent = models.DecimalField(max_digits=5, decimal_places=2)
    Absent_Days = models.IntegerField()
    Medical_Leaves = models.IntegerField(default=0)
    Behaviour_Rating = models.DecimalField(max_digits=3, decimal_places=1)

    def __str__(self):
        return f"{self.Roll_No} - Sem {self.Semester}"
    
    class Meta:
        db_table = 'AttendanceRecord'

class FeeRecord(models.Model):
    id = models.AutoField(primary_key=True)
    Roll_No = models.CharField(max_length=20)
    Dept = models.CharField(max_length=100)
    Total_Fee = models.DecimalField(max_digits=10, decimal_places=2)
    Fee_Paid = models.DecimalField(max_digits=10, decimal_places=2)
    Fee_Due = models.DecimalField(max_digits=10, decimal_places=2)
    Fee_Status = models.CharField(max_length=50, choices=[
        ('Paid', 'Paid'),
        ('Pending', 'Pending'),
        ('Partial', 'Partial'),
    ])

    def __str__(self):
        return f"{self.Roll_No} - {self.Fee_Status}"
    
    class Meta:
        db_table = 'FeeRecord'

class ActivityRecord(models.Model):
    id = models.AutoField(primary_key=True)
    Roll_No = models.CharField(max_length=20)
    Dept = models.CharField(max_length=100)
    Library_Hours = models.IntegerField(default=0)
    Books_Borrowed = models.IntegerField(default=0)
    Mock_Test_Score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    Placement_Attendance = models.IntegerField(default=0)
    Internship_Status = models.CharField(max_length=50, choices=[
        ('Completed', 'Completed'),
        ('Ongoing', 'Ongoing'),
        ('Not Started', 'Not Started'),
    ], default='Not Started')
    Placement_Status = models.CharField(max_length=50, choices=[
        ('Placed', 'Placed'),
        ('Not Placed', 'Not Placed'),
        ('In Progress', 'In Progress'),
    ], default='Not Placed')
    Company_Name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.Roll_No} - Activities"
    
    class Meta:
        db_table = 'ActivityRecord'

class DisciplinaryRecord(models.Model):
    id = models.AutoField(primary_key=True)
    Roll_No = models.CharField(max_length=20)
    Action_Taken = models.BooleanField(default=False)
    Description = models.TextField(null=True, blank=True)
    Date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.Roll_No} - Disciplinary"
    
    class Meta:
        db_table = 'DisciplinaryRecord'