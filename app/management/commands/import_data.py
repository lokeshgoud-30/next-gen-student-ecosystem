# data_manager/management/commands/import_data.py
import pandas as pd
import os
from django.core.management.base import BaseCommand
from app.models import Student, AcademicPerformance, AttendanceRecord, FeeRecord, ActivityRecord

class Command(BaseCommand):
    help = 'Import data from Excel files in data folder'

    def handle(self, *args, **options):
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        data_folder = os.path.join(project_root, '..', 'data')
        
        files = {
            'student': 'Student_Information.xlsx',
            'academic': 'Academic_Performance.xlsx', 
            'attendance': 'Attendance_Discipline.xlsx',
            'fees': 'Fees_Finance.xlsx',
            'library': 'Libraries_Placement.xlsx'
        }
        
        for data_type, file_name in files.items():
            file_path = os.path.join(data_folder, file_name)
            
            if os.path.exists(file_path):
                self.stdout.write(f"Importing {data_type} from {file_name}")
                
                try:
                    df = pd.read_excel(file_path)
                    
                    if data_type == 'student':
                        self.import_students(df)
                    elif data_type == 'academic':
                        self.import_academic(df)
                    elif data_type == 'attendance':
                        self.import_attendance(df)
                    elif data_type == 'fees':
                        self.import_fees(df)
                    elif data_type == 'library':
                        self.import_library(df)
                        
                    self.stdout.write(self.style.SUCCESS(f"Successfully imported {data_type} data"))
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error importing {data_type}: {str(e)}"))
            else:
                self.stdout.write(self.style.WARNING(f"File not found: {file_path}"))

    def safe_int_convert(self, value, default=0):
        """Safely convert value to integer, handling text like 'Not Attended'"""
        if pd.isna(value) or value in ['', ' ', None, 'NaN', 'NULL', 'None']:
            return default
        
        # Handle text values that should not be converted to numbers
        if isinstance(value, str):
            value_lower = value.lower().strip()
            if value_lower in ['not attended', 'na', 'n/a', 'pending', 'tbd', 'absent']:
                return default
        
        try:
            # Try direct conversion
            return int(float(value))
        except (ValueError, TypeError):
            try:
                # Try string cleaning
                cleaned = ''.join(char for char in str(value) if char.isdigit())
                if cleaned:
                    return int(cleaned)
                return default
            except:
                return default

    def safe_float_convert(self, value, default=0.0):
        """Safely convert value to float"""
        if pd.isna(value) or value in ['', ' ', None, 'NaN', 'NULL', 'None']:
            return default
        
        if isinstance(value, str):
            value_lower = value.lower().strip()
            if value_lower in ['not attended', 'na', 'n/a', 'pending', 'tbd']:
                return default
        
        try:
            # Remove percentage symbols if present
            value_str = str(value).replace('%', '').replace(',', '').strip()
            return float(value_str)
        except (ValueError, TypeError):
            return default

    def clean_placement_attendance(self, value):
        """Clean placement attendance values like 'Not Attended'"""
        if pd.isna(value) or value in ['', ' ', None]:
            return 0
        
        if isinstance(value, str):
            value_lower = value.lower().strip()
            if value_lower in ['attended', 'present']:
                return 1
            elif value_lower in ['not attended', 'notattended', 'absent', 'na', 'n/a']:
                return 0
            else:
                # Try to convert if it's a number string
                try:
                    return int(value)
                except:
                    return 0
        
        # If it's already a number
        try:
            return int(value)
        except:
            return 0

    def clean_text_field(self, value, default=''):
        """Clean text fields handling NaN and None"""
        if pd.isna(value) or value in ['', ' ', None, 'NaN', 'NULL', 'None', 'none']:
            return default
        return str(value).strip()

    def import_students(self, df):
        for index, row in df.iterrows():
            # Handle all fields safely
            passed_out_year = self.safe_int_convert(row.get('Passed_Out_Year'))
            year = self.safe_int_convert(row.get('Year'), 1)
            semester = self.safe_int_convert(row.get('Semester'), 1)
            joined_year = self.safe_int_convert(row.get('Joined_Year'))
            
            Student.objects.update_or_create(
                Roll_No=self.clean_text_field(row['Roll_No']),
                defaults={
                    'Name': self.clean_text_field(row.get('Name'), 'Unknown'),
                    'Dept': self.clean_text_field(row.get('Dept'), 'CSE'),
                    'Year': year,
                    'Semester': semester,
                    'Joined_Year': joined_year,
                    'Passed_Out_Year': passed_out_year if passed_out_year != 0 else None
                }
            )

    def import_academic(self, df):
        for index, row in df.iterrows():
            # Handle numeric fields safely
            thesis_work = self.safe_float_convert(row.get('Thesis_Work'))
            seminar = self.safe_float_convert(row.get('Seminar'))
            internship = self.safe_float_convert(row.get('Internship'))
            project_presentation = self.safe_float_convert(row.get('Project_Presentation'))
            sgpa = self.safe_float_convert(row.get('SGPA'))
            cgpa = self.safe_float_convert(row.get('CGPA'))
            backlogs = self.safe_int_convert(row.get('Backlogs'))
            semester = self.safe_int_convert(row.get('Semester'), 1)
            
            # Handle subject fields (assuming they are marks/percentages)
            ai_applications = self.safe_float_convert(row.get('AI_Applications'))
            cloud_computing = self.safe_float_convert(row.get('Cloud_Computing'))
            embedded_systems = self.safe_float_convert(row.get('Embedded_Systems'))
            cybersecurity = self.safe_float_convert(row.get('Cybersecurity'))
            deep_learning = self.safe_float_convert(row.get('Deep_Learning'))
            iot_systems = self.safe_float_convert(row.get('IoT_Systems'))
            big_dataanalytics = self.safe_float_convert(row.get('Big_DataAnalytics'))
            optimization_techniques = self.safe_float_convert(row.get('Optimization_Techniques'))
            advanced_algorithms = self.safe_float_convert(row.get('Advanced_Algorithms'))
            machine_learning = self.safe_float_convert(row.get('Machine_Learning'))
            data_analytics = self.safe_float_convert(row.get('Data_Analytics'))
            research_methodology = self.safe_float_convert(row.get('Research_Methodology'))
            
            AcademicPerformance.objects.update_or_create(
                Roll_No=self.clean_text_field(row['Roll_No']),
                Semester=semester,
                defaults={
                    'Dept': self.clean_text_field(row.get('Dept'), 'CSE'),
                    'Thesis_Work': thesis_work,
                    'Seminar': seminar,
                    'Internship': internship,
                    'Project_Presentation': project_presentation,
                    'SGPA': sgpa,
                    'CGPA': cgpa,
                    'Backlogs': backlogs,
                    'AI_Applications': ai_applications,
                    'Cloud_Computing': cloud_computing,
                    'Embedded_Systems': embedded_systems,
                    'Cybersecurity': cybersecurity,
                    'Deep_Learning': deep_learning,
                    'IoT_Systems': iot_systems,
                    'Big_DataAnalytics': big_dataanalytics,
                    'Optimization_Techniques': optimization_techniques,
                    'Advanced_Algorithms': advanced_algorithms,
                    'Machine_Learning': machine_learning,
                    'Data_Analytics': data_analytics,
                    'Research_Methodology': research_methodology
                }
            )

    def import_attendance(self, df):
        for index, row in df.iterrows():
            # Handle percentage field (remove % symbol if present)
            attendance_percent = self.safe_float_convert(row.get('Attendance_%'))
            absent_days = self.safe_int_convert(row.get('Absent_Days'))
            medical_leaves = self.safe_int_convert(row.get('Medical_Leaves'))
            behaviour_rating = self.safe_int_convert(row.get('Behaviour_Rating'), 3)
            semester = self.safe_int_convert(row.get('Semester'), 1)
            
            AttendanceRecord.objects.update_or_create(
                Roll_No=self.clean_text_field(row['Roll_No']),
                Semester=semester,
                defaults={
                    'Dept': self.clean_text_field(row.get('Dept'), 'CSE'),
                    'Attendance_Percent': attendance_percent,
                    'Absent_Days': absent_days,
                    'Medical_Leaves': medical_leaves,
                    'Behaviour_Rating': behaviour_rating
                }
            )

    def import_fees(self, df):
        for index, row in df.iterrows():
            total_fee = self.safe_float_convert(row.get('Total_Fee'))
            fee_paid = self.safe_float_convert(row.get('Fee_Paid'))
            fee_due = self.safe_float_convert(row.get('Fee_Due'))
            fee_status = self.clean_text_field(row.get('Fee_Status'), 'Pending')
            
            FeeRecord.objects.update_or_create(
                Roll_No=self.clean_text_field(row['Roll_No']),
                defaults={
                    'Dept': self.clean_text_field(row.get('Dept'), 'CSE'),
                    'Total_Fee': total_fee,
                    'Fee_Paid': fee_paid,
                    'Fee_Due': fee_due,
                    'Fee_Status': fee_status
                }
            )

    def import_library(self, df):
        for index, row in df.iterrows():
            # Handle library hours, books borrowed, mock test score safely
            library_hours = self.safe_int_convert(row.get('Library_Hours'))
            books_borrowed = self.safe_int_convert(row.get('Books_Borrowed'))
            mock_test_score = self.safe_int_convert(row.get('Mock_Test_Score'))
            
            # Handle placement attendance specially to convert 'Not Attended' to 0
            placement_attendance = self.clean_placement_attendance(row.get('Placement_Attendance'))
            
            internship_status = self.clean_text_field(row.get('Internship_Status'), 'Not Started')
            placement_status = self.clean_text_field(row.get('Placement_Status'), 'Not Placed')
            company_name = self.clean_text_field(row.get('Company_Name'))
            
            ActivityRecord.objects.update_or_create(
                Roll_No=self.clean_text_field(row['Roll_No']),
                defaults={
                    'Dept': self.clean_text_field(row.get('Dept'), 'CSE'),
                    'Library_Hours': library_hours,
                    'Books_Borrowed': books_borrowed,
                    'Mock_Test_Score': mock_test_score,
                    'Placement_Attendance': placement_attendance,
                    'Internship_Status': internship_status,
                    'Placement_Status': placement_status,
                    'Company_Name': company_name
                }
            )