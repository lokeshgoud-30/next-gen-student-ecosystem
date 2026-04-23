import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()
import pandas as pd
from app.models import AcademicPerformance

df = pd.read_excel("Academic_Performance_final.xlsx")  

for index, row in df.iterrows():
    AcademicPerformance.objects.create(
        Roll_No=row['Roll_No'],
        Dept=row['Dept'],
        Semester=row['Semester'],

        Thesis_Work=int(row['Thesis_Work']) if pd.notna(row['Thesis_Work']) else None,
        Seminar=int(row['Seminar']) if pd.notna(row['Seminar']) else None,
        Internship=int(row['Internship']) if pd.notna(row['Internship']) else None,
        Project_Presentation=int(row['Project_Presentation']) if pd.notna(row['Project_Presentation']) else None,

        SGPA=float(row['SGPA']) if pd.notna(row['SGPA']) else None,
        CGPA=float(row['CGPA']) if pd.notna(row['CGPA']) else None,
        Backlogs=int(row['Backlogs']) if pd.notna(row['Backlogs']) else 0,

        AI_Applications=int(row['AI_Applications']) if pd.notna(row['AI_Applications']) else None,
        Cloud_Computing=int(row['Cloud_Computing']) if pd.notna(row['Cloud_Computing']) else None,
        Embedded_Systems=int(row['Embedded_Systems']) if pd.notna(row['Embedded_Systems']) else None,
        Cybersecurity=int(row['Cybersecurity']) if pd.notna(row['Cybersecurity']) else None,
        Deep_Learning=int(row['Deep_Learning']) if pd.notna(row['Deep_Learning']) else None,
        IoT_Systems=int(row['IoT_Systems']) if pd.notna(row['IoT_Systems']) else None,
        Big_DataAnalytics=int(row['Big_DataAnalytics']) if pd.notna(row['Big_DataAnalytics']) else None,
        Optimization_Techniques=int(row['Optimization_Techniques']) if pd.notna(row['Optimization_Techniques']) else None,
        Advanced_Algorithms=int(row['Advanced_Algorithms']) if pd.notna(row['Advanced_Algorithms']) else None,
        Machine_Learning=int(row['Machine_Learning']) if pd.notna(row['Machine_Learning']) else None,
        Data_Analytics=int(row['Data_Analytics']) if pd.notna(row['Data_Analytics']) else None,
        Research_Methodology=int(row['Research_Methodology']) if pd.notna(row['Research_Methodology']) else None,
    )

print("🎯 Successfully Imported Academic Data!")


