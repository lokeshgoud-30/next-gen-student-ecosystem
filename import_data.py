import pandas as pd
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

django.setup()

from app.models import Student, AcademicPerformance, AttendanceRecord, FeeRecord, ActivityRecord, DisciplinaryRecord

def import_all_data():
    """Import data from all Excel files in data folder"""
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_folder = os.path.join(current_dir, 'data')
    
    # CORRECTED FILE NAMES - using actual file names from your folder
    files = {
        'student': 'Student_Information.xlsx',
        'academic': 'Academic_Performance.xlsx', 
        'attendance': 'Attendance_Discipline.xlsx',  # ← FIXED: Double dots
        'fees': 'Fees_Finance.xlsx',
        'library': 'Libraries_Placement.xlsx'
    }
    
    print("Starting data import...")
    print(f"Script location: {current_dir}")
    print(f"Data folder: {data_folder}")
    print(f"Files to import: {files}")
    
    # Check if data folder exists and list files
    if not os.path.exists(data_folder):
        print(f"❌ Data folder not found: {data_folder}")
        return
    
    print(f"📁 Files in data folder: {os.listdir(data_folder)}")
    
    imported_count = 0
    for data_type, file_name in files.items():
        file_path = os.path.join(data_folder, file_name)
        
        print(f"\n{'='*60}")
        print(f"Importing {data_type} from {file_name}")
        print(f"File path: {file_path}")
        
        if os.path.exists(file_path):
            try:
                df = pd.read_excel(file_path)
                print(f"✅ File loaded successfully")
                print(f"📊 Columns: {list(df.columns)}")
                print(f"📝 Records: {len(df)}")
                
                if data_type == 'student':
                    count = import_students(df)
                elif data_type == 'academic':
                    count = import_academic_corrected(df)  # ← FIXED column names
                elif data_type == 'attendance':
                    count = import_attendance_and_discipline(df)
                elif data_type == 'fees':
                    count = import_fees(df)
                elif data_type == 'library':
                    count = import_library(df)
                
                imported_count += count
                print(f"✅ Successfully processed {count} {data_type} records")
                
            except Exception as e:
                print(f"❌ Error importing {data_type}: {str(e)}")
                import traceback
                traceback.print_exc()
        else:
            print(f"❌ File not found: {file_path}")
    
    print(f"\n{'='*60}")
    print(f"🎉 Import completed!")
    print(f"📈 Total records processed: {imported_count}")
    print(f"{'='*60}")

def import_students(df):
    count = 0
    for index, row in df.iterrows():
        passed_out_year = row['Passed_Out_Year'] if pd.notna(row.get('Passed_Out_Year')) else None
        
        obj, created = Student.objects.update_or_create(
            Roll_No=str(row['Roll_No']),
            defaults={
                'Name': row['Name'],
                'Dept': row['Dept'],
                'Year': int(row['Year']),
                'Semester': int(row['Semester']),
                'Joined_Year': int(row['Joined_Year']),
                'Passed_Out_Year': passed_out_year
            }
        )
        if created:
            count += 1
    return count

def import_academic_corrected(df):
    """Import academic data with actual marks storage"""
    count = 0
    missing_data_count = 0
    
    print("🔍 Academic data columns found:", list(df.columns))
    
    for index, row in df.iterrows():
        try:
            # Handle subject marks - store actual values instead of boolean
            subject_fields = [
                'AI Applications', 'Cloud Computing', 'Embedded Systems', 'Cybersecurity',
                'Deep Learning', 'IoT Systems', 'Big Data Analytics', 'Optimization Techniques',
                'Advanced Algorithms', 'Machine Learning', 'Data Analytics', 'Research Methodology'
            ]
            
            subject_data = {}
            for field in subject_fields:
                value = row.get(field, None)
                if pd.notna(value) and value != '':
                    try:
                        subject_data[field.replace(' ', '_')] = int(float(value))
                    except (ValueError, TypeError):
                        subject_data[field.replace(' ', '_')] = None
                else:
                    subject_data[field.replace(' ', '_')] = None
            
            # Handle main academic fields
            sgpa = float(row['SGPA']) if pd.notna(row.get('SGPA')) and row['SGPA'] != '' else None
            cgpa = float(row['CGPA']) if pd.notna(row.get('CGPA')) and row['CGPA'] != '' else None
            
            # Text fields
            thesis_work = str(row.get('Thesis Work', '')) if pd.notna(row.get('Thesis Work')) and row['Thesis Work'] != '' else ''
            seminar = str(row.get('Seminar', '')) if pd.notna(row.get('Seminar')) and row['Seminar'] != '' else ''
            internship = str(row.get('Internship', '')) if pd.notna(row.get('Internship')) and row['Internship'] != '' else ''
            project_presentation = str(row.get('Project Presentation', '')) if pd.notna(row.get('Project Presentation')) and row['Project Presentation'] != '' else ''
            
            # Handle backlogs
            backlogs_value = row.get('Backlogs', 0)
            if pd.isna(backlogs_value) or backlogs_value == '':
                backlogs_value = 0
            else:
                backlogs_value = int(backlogs_value)
            
            # Debug output for first few records
            if index < 3:
                print(f"📝 Sample data for {row['Roll_No']}:")
                print(f"   Thesis: '{thesis_work}', Seminar: '{seminar}'")
                print(f"   SGPA: {sgpa}, CGPA: {cgpa}")
                print(f"   Subjects: AI={subject_data.get('AI_Applications')}, Cloud={subject_data.get('Cloud_Computing')}")
            
            obj, created = AcademicPerformance.objects.update_or_create(
                Roll_No=str(row['Roll_No']),
                Semester=int(row['Semester']),
                defaults={
                    'Dept': row['Dept'],
                    'Thesis_Work': thesis_work,
                    'Seminar': seminar,
                    'Internship': internship,
                    'Project_Presentation': project_presentation,
                    'SGPA': sgpa,
                    'CGPA': cgpa,
                    'Backlogs': backlogs_value,
                    **subject_data
                }
            )
            if created:
                count += 1
                
        except Exception as e:
            print(f"❌ Error importing academic data for {row['Roll_No']}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    return count

def import_attendance_and_discipline(df):
    """Import both attendance and discipline data"""
    attendance_count = 0
    discipline_count = 0
    
    print("🔍 Attendance/Discipline columns found:", list(df.columns))
    
    for index, row in df.iterrows():
        try:
            # Import Attendance Record
            attendance_obj, attendance_created = AttendanceRecord.objects.update_or_create(
                Roll_No=str(row['Roll_No']),
                Semester=int(row['Semester']),
                defaults={
                    'Dept': row['Dept'],
                    'Attendance_Percent': float(row['Attendance_%']),
                    'Absent_Days': int(row['Absent_Days']),
                    'Medical_Leaves': int(row.get('Medical_Leaves', 0)) if pd.notna(row.get('Medical_Leaves')) else 0,
                    'Behaviour_Rating': float(row['Behaviour_Rating'])
                }
            )
            if attendance_created:
                attendance_count += 1
                
            # Import Disciplinary Record if columns exist
            if 'Action_Taken' in df.columns or 'Disciplinary_Action' in df.columns:
                action_taken_col = 'Action_Taken' if 'Action_Taken' in df.columns else 'Disciplinary_Action'
                action_value = row.get(action_taken_col, False)
                
                if pd.notna(action_value):
                    if isinstance(action_value, (int, float)):
                        action_bool = (action_value != 0)
                    elif isinstance(action_value, str):
                        action_bool = action_value.lower() in ['true', '1', 'yes', 'y', 't']
                    else:
                        action_bool = bool(action_value)
                else:
                    action_bool = False
                
                discipline_obj, discipline_created = DisciplinaryRecord.objects.update_or_create(
                    Roll_No=str(row['Roll_No']),
                    defaults={
                        'Action_Taken': action_bool,
                        'Description': str(row.get('Description', '')) if pd.notna(row.get('Description')) else ''
                    }
                )
                if discipline_created:
                    discipline_count += 1
                    
        except Exception as e:
            print(f"❌ Error importing attendance/discipline for {row['Roll_No']}: {str(e)}")
    
    print(f"📊 Attendance records: {attendance_count}")
    print(f"📊 Discipline records: {discipline_count}")
    return attendance_count + discipline_count

def import_fees(df):
    count = 0
    for index, row in df.iterrows():
        obj, created = FeeRecord.objects.update_or_create(
            Roll_No=str(row['Roll_No']),
            defaults={
                'Dept': row['Dept'],
                'Total_Fee': float(row['Total_Fee']),
                'Fee_Paid': float(row['Fee_Paid']),
                'Fee_Due': float(row['Fee_Due']),
                'Fee_Status': row['Fee_Status']
            }
        )
        if created:
            count += 1
    return count

def import_library(df):
    count = 0
    for index, row in df.iterrows():
        mock_test_score = float(row['Mock_Test_Score']) if pd.notna(row.get('Mock_Test_Score')) else None
        
        obj, created = ActivityRecord.objects.update_or_create(
            Roll_No=str(row['Roll_No']),
            defaults={
                'Dept': row['Dept'],
                'Library_Hours': int(row.get('Library_Hours', 0)) if pd.notna(row.get('Library_Hours')) else 0,
                'Books_Borrowed': int(row.get('Books_Borrowed', 0)) if pd.notna(row.get('Books_Borrowed')) else 0,
                'Mock_Test_Score': mock_test_score,
                'Placement_Attendance': int(row.get('Placement_Attendance', 0)) if pd.notna(row.get('Placement_Attendance')) else 0,
                'Internship_Status': row.get('Internship_Status', 'Not Started'),
                'Placement_Status': row.get('Placement_Status', 'Not Placed'),
                'Company_Name': str(row.get('Company_Name', '')) if pd.notna(row.get('Company_Name')) else ''
            }
        )
        if created:
            count += 1
    return count

if __name__ == "__main__":
    import_all_data()