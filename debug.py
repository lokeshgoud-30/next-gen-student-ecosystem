import pandas as pd
import os

def debug_all_files():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_folder = os.path.join(current_dir, 'data')
    
    print(f"Current directory: {current_dir}")
    print(f"Data folder: {data_folder}")
    print(f"Data folder exists: {os.path.exists(data_folder)}")
    
    if os.path.exists(data_folder):
        print(f"Files in data folder: {os.listdir(data_folder)}")
    
    files = {
        'academic': 'Academic_Performance.xlsx',
        'attendance': 'Attendance_Discipline.xlsx'
    }
    
    for data_type, file_name in files.items():
        file_path = os.path.join(data_folder, file_name)
        print(f"\n{'='*60}")
        print(f"Checking: {file_name}")
        print(f"Full path: {file_path}")
        print(f"File exists: {os.path.exists(file_path)}")
        
        if os.path.exists(file_path):
            try:
                df = pd.read_excel(file_path)
                print(f"✅ File loaded successfully!")
                print(f"Shape: {df.shape}")
                print(f"Columns: {list(df.columns)}")
                print(f"First 3 rows:")
                print(df.head(3))
                
                if data_type == 'academic':
                    # Check if all expected columns are present
                    expected_columns = [
                        'Roll_No', 'Dept', 'Semester', 'Thesis_Work', 'Seminar', 
                        'Internship', 'Project_Presentation', 'SGPA', 'CGPA', 'Backlogs'
                    ]
                    missing_columns = [col for col in expected_columns if col not in df.columns]
                    if missing_columns:
                        print(f"❌ Missing columns: {missing_columns}")
                    else:
                        print(f"✅ All expected columns present")
                        
            except Exception as e:
                print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    debug_all_files()