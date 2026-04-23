from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .chatbot1 import *
import logging
from app.models import AcademicPerformance, AttendanceRecord, FeeRecord, ActivityRecord


logger = logging.getLogger(__name__)

class AcademicChatbot:
    """Handles academic queries and returns responses."""
    
    def get_academic_response(self, query):
        query_lower = query.lower()
        
        if 'top 10 students' in query_lower and 'department' in query_lower:
            return self.get_top_10_students_by_department()
        elif 'attendance less than 75%' in query_lower:
            return self.get_students_with_low_attendance()
        elif 'fee dues' in query_lower:
            return self.get_students_with_fee_dues()
        elif 'placed students' in query_lower:
            return self.get_placed_students()
        elif 'students not placed' in query_lower:
            return self.get_students_not_placed()
        elif 'students with backlogs' in query_lower:
            return self.get_students_with_backlogs()
        elif 'low attendance count' in query_lower:
            return self.get_low_attendance_count_per_department()
        elif 'fee due count' in query_lower:
            return self.get_fee_due_count_per_department()
        elif 'low attendance and backlogs' in query_lower:
            return self.get_students_with_low_attendance_and_backlogs()
        else:
            return "I can only help with queries related to attendance, grades, fees, placement status, and backlogs."

    def get_top_10_students_by_department(self):
        top_students = Student.objects.values('Dept').annotate(num_students=models.Count('Roll_No')).order_by('Dept')[:10]
        response = "\n".join([f"Department: {student['Dept']}, Students Count: {student['num_students']}" for student in top_students])
        return response
    
    def get_students_with_low_attendance(self):
        low_attendance_students = AttendanceRecord.objects.filter(Attendance_Percent__lt=75).values('Roll_No', 'Dept', 'Attendance_Percent')
        response = "\n".join([f"Roll No: {student['Roll_No']}, Department: {student['Dept']}, Attendance: {student['Attendance_Percent']}%" for student in low_attendance_students])
        return response
    
    def get_students_with_fee_dues(self):
        fee_due_students = FeeRecord.objects.filter(Fee_Due__gt=0).values('Roll_No', 'Dept', 'Fee_Due')
        response = "\n".join([f"Roll No: {student['Roll_No']}, Department: {student['Dept']}, Fee Due: {student['Fee_Due']}" for student in fee_due_students])
        return response
    
    def get_placed_students(self):
        placed_students = ActivityRecord.objects.filter(Placement_Status='Placed').values('Roll_No', 'Dept', 'Company_Name')
        response = "\n".join([f"Roll No: {student['Roll_No']}, Department: {student['Dept']}, Company: {student['Company_Name']}" for student in placed_students])
        return response
    
    def get_students_not_placed(self):
        not_placed_students = ActivityRecord.objects.filter(Placement_Status='Not Placed').values('Roll_No', 'Dept')
        response = "\n".join([f"Roll No: {student['Roll_No']}, Department: {student['Dept']}" for student in not_placed_students])
        return response
    
    def get_students_with_backlogs(self):
        students_with_backlogs = AcademicPerformance.objects.filter(Backlogs__gt=0).values('Roll_No', 'Dept', 'Backlogs')
        response = "\n".join([f"Roll No: {student['Roll_No']}, Department: {student['Dept']}, Backlogs: {student['Backlogs']}" for student in students_with_backlogs])
        return response
    
    def get_low_attendance_count_per_department(self):
        low_attendance_count = AttendanceRecord.objects.filter(Attendance_Percent__lt=75).values('Dept').annotate(num_students=models.Count('Roll_No'))
        response = "\n".join([f"Department: {attendance['Dept']}, Low Attendance Count: {attendance['num_students']}" for attendance in low_attendance_count])
        return response
    
    def get_fee_due_count_per_department(self):
        fee_due_count = FeeRecord.objects.filter(Fee_Due__gt=0).values('Dept').annotate(num_students=models.Count('Roll_No'))
        response = "\n".join([f"Department: {fee_due['Dept']}, Fee Due Count: {fee_due['num_students']}" for fee_due in fee_due_count])
        return response
    
    def get_students_with_low_attendance_and_backlogs(self):
        students = AttendanceRecord.objects.filter(Attendance_Percent__lt=75)
        students_with_backlogs = AcademicPerformance.objects.filter(Backlogs__gt=0)
        
        combined_students = set([student['Roll_No'] for student in students]) & set([student['Roll_No'] for student in students_with_backlogs])
        
        response = "\n".join([f"Roll No: {roll_no}" for roll_no in combined_students])
        return response

@csrf_exempt
def chatbot_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            
            if not message:
                return JsonResponse({
                    'success': True,
                    'response': "Please type your question! I can help with attendance, grades, fees, library, placement, and other academic matters."
                })
            
            # Get student context (if needed for personalized responses)
            student_context = None
            if request.session.get('user_type') == 'student':
                roll_no = request.session.get('roll_no')
                try:
                    student = Student.objects.get(Roll_No=roll_no)
                    student_context = {
                        'dept': student.Dept,
                        'year': student.Year,
                        'semester': student.Semester
                    }
                except Student.DoesNotExist:
                    pass
            
            # Create an instance of AcademicChatbot and fetch response
            academic_chatbot = AcademicChatbot()
            response = academic_chatbot.get_academic_response(message)
            
            # If the response contains error or fallback message, try Gemini AI
            if response.lower() in ["i can only help with queries related to attendance, grades, fees, placement status, and backlogs."]:
                response = chat_bot(message, student_context)
            
            return JsonResponse({
                'success': True,
                'response': response,
                'message': message
            })
            
        except Exception as e:
            logger.error(f"Chatbot API error: {e}")
            return JsonResponse({
                'success': True,
                'response': "I am here to help! You can ask me about attendance, grades, fees, library services, placement information, or any academic queries."
            })
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def chatbot_view(request):
    """Render the chatbot interface"""
    if not request.session.get('login'):
        return redirect('student_login')
    
    return render(request, 'chatbot.html')



def index(request):
    return render(request , 'index.html')


def about(request):
    return render(request , 'about.html')






# HOD Views
def hod_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if email == 'hod@gmail.com' and password == 'hod':
            request.session['email'] = email
            request.session['user_type'] = 'hod'
            request.session['login'] = True
            return redirect('hod_dashboard')
        else:
            messages.error(request, 'Invalid Credentials')
            return redirect('hod_login')
        
    return render(request, 'hod_login.html')

def hod_dashboard(request):
    if not request.session.get('login') or request.session.get('user_type') != 'hod':
        return redirect('hod_login')
    
    total_students = Student.objects.count()
    total_departments = Student.objects.values('Dept').distinct().count()
    return render(request, 'hod_dashboard.html', {'total_students': total_students , 'total_departments': total_departments})

def enter_roll_no(request):
    if not request.session.get('login') or request.session.get('user_type') != 'hod':
        return redirect('hod_login')
    
    if request.method == 'POST':
        roll_no = request.POST.get('roll_no')
        try:
            student = Student.objects.get(Roll_No=roll_no)
            return redirect('view_student_details', roll_no=roll_no)
        except Student.DoesNotExist:
            messages.error(request, 'Student not found')
    
    return render(request, 'enter_roll_no.html')

# def view_student_details(request, roll_no):
#     if not request.session.get('login') or request.session.get('user_type') != 'hod':
#         return redirect('hod_login')
    
#     try:
#         student = Student.objects.get(Roll_No=roll_no)
#         academic_data = AcademicPerformance.objects.filter(Roll_No=roll_no)
#         attendance_data = AttendanceRecord.objects.filter(Roll_No=roll_no)
#         fee_data = FeeRecord.objects.filter(Roll_No=roll_no).first()
#         activity_data = ActivityRecord.objects.filter(Roll_No=roll_no).first()
#         disciplinary_data = DisciplinaryRecord.objects.filter(Roll_No=roll_no).first()
        
#         context = {
#             'student': student,
#             'academic_data': academic_data,
#             'attendance_data': attendance_data,
#             'fee_data': fee_data,
#             'activity_data': activity_data,
#             'disciplinary_data': disciplinary_data,
#         }
#         return render(request, 'student_details.html', context)
#     except Student.DoesNotExist:
#         messages.error(request, 'Student not found')
#         return redirect('enter_roll_no')




def view_student_details(request, roll_no):
    if not request.session.get('login') or request.session.get('user_type') != 'hod':
        return redirect('hod_login')
    
    try:
        student = Student.objects.get(Roll_No=roll_no)
        academic_data = AcademicPerformance.objects.filter(Roll_No=roll_no).order_by('Semester')
        attendance_data = AttendanceRecord.objects.filter(Roll_No=roll_no).order_by('Semester')
        fee_data = FeeRecord.objects.filter(Roll_No=roll_no).first()
        activity_data = ActivityRecord.objects.filter(Roll_No=roll_no).first()
        disciplinary_data = DisciplinaryRecord.objects.filter(Roll_No=roll_no).first()
        
        # Prepare comprehensive chart data
        chart_data = prepare_complete_chart_data(academic_data, attendance_data)
        
        context = {
            'student': student,
            'academic_data': academic_data,
            'attendance_data': attendance_data,
            'fee_data': fee_data,
            'activity_data': activity_data,
            'disciplinary_data': disciplinary_data,
            'chart_data': chart_data,
        }
        return render(request, 'student_details.html', context)
    except Student.DoesNotExist:
        messages.error(request, 'Student not found')
        return redirect('enter_roll_no')

def prepare_complete_chart_data(academic_data, attendance_data):
    """Prepare complete data for all charts with detailed tooltip information"""
    
    # Academic Performance Data
    semesters = []
    sgpa_data = []
    cgpa_data = []
    attendance_percent = []
    absent_days = []
    medical_leaves = []
    behavior_ratings = []
    
    # Academic data
    for academic in academic_data:
        semesters.append(f"Sem {academic.Semester}")
        sgpa_data.append(float(academic.SGPA) if academic.SGPA else 0)
        cgpa_data.append(float(academic.CGPA) if academic.CGPA else 0)
    
    # Attendance data
    attendance_semesters = []
    for attendance in attendance_data:
        attendance_semesters.append(f"Sem {attendance.Semester}")
        attendance_percent.append(float(attendance.Attendance_Percent) if attendance.Attendance_Percent else 0)
        absent_days.append(attendance.Absent_Days or 0)
        medical_leaves.append(attendance.Medical_Leaves or 0)
        behavior_ratings.append(float(attendance.Behaviour_Rating) if attendance.Behaviour_Rating else 0)
    
    # Ensure all arrays have the same length
    max_semesters = max(len(semesters), len(attendance_semesters))
    all_semesters = semesters if len(semesters) >= len(attendance_semesters) else attendance_semesters
    
    # Bar Chart Data - Subject marks for latest semester
    latest_semester = academic_data.last()
    subject_marks = {}
    subject_tooltips = {}
    if latest_semester:
        subject_fields = [
            ('AI_Applications', 'AI Applications'),
            ('Cloud_Computing', 'Cloud Computing'),
            ('Embedded_Systems', 'Embedded Systems'),
            ('Cybersecurity', 'Cybersecurity'),
            ('Deep_Learning', 'Deep Learning'),
            ('IoT_Systems', 'IoT Systems'),
            ('Big_DataAnalytics', 'Big Data Analytics'),
            ('Optimization_Techniques', 'Optimization Techniques'),
            ('Advanced_Algorithms', 'Advanced Algorithms'),
            ('Machine_Learning', 'Machine Learning'),
            ('Data_Analytics', 'Data Analytics'),
            ('Research_Methodology', 'Research Methodology')
        ]
        
        for field, display_name in subject_fields:
            mark = getattr(latest_semester, field)
            if mark is not None:
                subject_marks[display_name] = mark
                # Create tooltip data
                grade = get_grade(mark)
                subject_tooltips[display_name] = {
                    'mark': mark,
                    'grade': grade,
                    'semester': f"Sem {latest_semester.Semester}"
                }
    
    # Performance Distribution
    performance_categories = {
        'Excellent (9+ SGPA)': 0,
        'Very Good (8-9 SGPA)': 0,
        'Good (7-8 SGPA)': 0,
        'Average (6-7 SGPA)': 0,
        'Below Average (<6 SGPA)': 0
    }
    
    performance_details = {}
    for academic in academic_data:
        if academic.SGPA:
            sgpa = float(academic.SGPA)
            semester_key = f"Sem {academic.Semester}"
            if sgpa >= 9:
                performance_categories['Excellent (9+ SGPA)'] += 1
                performance_details[semester_key] = {'sgpa': sgpa, 'category': 'Excellent'}
            elif sgpa >= 8:
                performance_categories['Very Good (8-9 SGPA)'] += 1
                performance_details[semester_key] = {'sgpa': sgpa, 'category': 'Very Good'}
            elif sgpa >= 7:
                performance_categories['Good (7-8 SGPA)'] += 1
                performance_details[semester_key] = {'sgpa': sgpa, 'category': 'Good'}
            elif sgpa >= 6:
                performance_categories['Average (6-7 SGPA)'] += 1
                performance_details[semester_key] = {'sgpa': sgpa, 'category': 'Average'}
            else:
                performance_categories['Below Average (<6 SGPA)'] += 1
                performance_details[semester_key] = {'sgpa': sgpa, 'category': 'Below Average'}
    
    # Backlog Analysis
    backlog_data = {
        'No Backlogs': 0,
        '1-2 Backlogs': 0,
        '3-5 Backlogs': 0,
        'More than 5 Backlogs': 0
    }
    
    backlog_details = {}
    for academic in academic_data:
        backlogs = academic.Backlogs or 0
        semester_key = f"Sem {academic.Semester}"
        if backlogs == 0:
            backlog_data['No Backlogs'] += 1
            backlog_details[semester_key] = {'backlogs': 0, 'category': 'No Backlogs'}
        elif backlogs <= 2:
            backlog_data['1-2 Backlogs'] += 1
            backlog_details[semester_key] = {'backlogs': backlogs, 'category': '1-2 Backlogs'}
        elif backlogs <= 5:
            backlog_data['3-5 Backlogs'] += 1
            backlog_details[semester_key] = {'backlogs': backlogs, 'category': '3-5 Backlogs'}
        else:
            backlog_data['More than 5 Backlogs'] += 1
            backlog_details[semester_key] = {'backlogs': backlogs, 'category': 'More than 5 Backlogs'}
    
    # Attendance Pattern Analysis
    attendance_pattern = {
        'Excellent (90-100%)': 0,
        'Good (75-89%)': 0,
        'Average (60-74%)': 0,
        'Poor (<60%)': 0
    }
    
    attendance_details = {}
    for attendance in attendance_data:
        if attendance.Attendance_Percent:
            percent = float(attendance.Attendance_Percent)
            semester_key = f"Sem {attendance.Semester}"
            if percent >= 90:
                attendance_pattern['Excellent (90-100%)'] += 1
                attendance_details[semester_key] = {
                    'percent': percent, 
                    'category': 'Excellent',
                    'absent_days': attendance.Absent_Days,
                    'medical_leaves': attendance.Medical_Leaves
                }
            elif percent >= 75:
                attendance_pattern['Good (75-89%)'] += 1
                attendance_details[semester_key] = {
                    'percent': percent, 
                    'category': 'Good',
                    'absent_days': attendance.Absent_Days,
                    'medical_leaves': attendance.Medical_Leaves
                }
            elif percent >= 60:
                attendance_pattern['Average (60-74%)'] += 1
                attendance_details[semester_key] = {
                    'percent': percent, 
                    'category': 'Average',
                    'absent_days': attendance.Absent_Days,
                    'medical_leaves': attendance.Medical_Leaves
                }
            else:
                attendance_pattern['Poor (<60%)'] += 1
                attendance_details[semester_key] = {
                    'percent': percent, 
                    'category': 'Poor',
                    'absent_days': attendance.Absent_Days,
                    'medical_leaves': attendance.Medical_Leaves
                }
    
    # Leave Analysis
    total_absent_days = sum(absent_days)
    total_medical_leaves = sum(medical_leaves)
    
    leave_distribution = {
        'Medical Leaves': total_medical_leaves,
        'Other Absences': total_absent_days
    }
    
    return {
        # Academic Charts
        'line_chart': {
            'semesters': all_semesters,
            'sgpa_data': sgpa_data + [0] * (max_semesters - len(sgpa_data)),
            'cgpa_data': cgpa_data + [0] * (max_semesters - len(cgpa_data)),
            'attendance_data': attendance_percent + [0] * (max_semesters - len(attendance_percent))
        },
        'bar_chart': {
            'subjects': list(subject_marks.keys()),
            'marks': list(subject_marks.values()),
            'tooltips': subject_tooltips
        },
        'pie_chart': {
            'labels': list(performance_categories.keys()),
            'data': list(performance_categories.values()),
            'colors': ['#28a745', '#20c997', '#ffc107', '#fd7e14', '#dc3545'],
            'details': performance_details
        },
        'donut_chart': {
            'labels': list(backlog_data.keys()),
            'data': list(backlog_data.values()),
            'colors': ['#28a745', '#20c997', '#ffc107', '#dc3545'],
            'details': backlog_details
        },
        # Attendance Charts
        'attendance_trend_chart': {
            'semesters': attendance_semesters,
            'attendance_percent': attendance_percent,
            'absent_days': absent_days,
            'medical_leaves': medical_leaves,
            'behavior_ratings': behavior_ratings
        },
        'attendance_pattern_chart': {
            'labels': list(attendance_pattern.keys()),
            'data': list(attendance_pattern.values()),
            'colors': ['#28a745', '#20c997', '#ffc107', '#dc3545'],
            'details': attendance_details
        },
        'behavior_chart': {
            'semesters': attendance_semesters,
            'ratings': behavior_ratings
        },
        'leave_analysis_chart': {
            'labels': list(leave_distribution.keys()),
            'data': list(leave_distribution.values()),
            'colors': ['#3498db', '#e74c3c']
        }
    }

def get_grade(mark):
    """Helper function to get grade based on marks"""
    if mark >= 90:
        return 'A+'
    elif mark >= 80:
        return 'A'
    elif mark >= 70:
        return 'B+'
    elif mark >= 60:
        return 'B'
    elif mark >= 50:
        return 'C'
    elif mark >= 40:
        return 'D'
    else:
        return 'F'


def hod_logout(request):
    request.session.flush()
    return redirect('/')

# Student Views
def student_login(request):
    if request.method == 'POST':
        roll_no = request.POST.get('roll_no')
        password = request.POST.get('password')
        
        try:
            student = Student.objects.get(Roll_No=roll_no, password=password)
            request.session['roll_no'] = roll_no
            request.session['user_type'] = 'student'
            request.session['login'] = True
            
            # Get performance data for messages
            messages_data = get_student_performance_messages(roll_no)
            request.session['performance_messages'] = messages_data
            
            return redirect('student_dashboard')
        except Student.DoesNotExist:
            messages.error(request, 'Invalid Roll No or Password')
    
    return render(request, 'student_login.html')

def get_student_performance_messages(roll_no):
    """Get performance-based messages for the student"""
    messages_list = []
    
    try:
        # Get latest attendance record
        latest_attendance = AttendanceRecord.objects.filter(Roll_No=roll_no).order_by('-Semester').first()
        
        # Get latest academic performance
        latest_academic = AcademicPerformance.objects.filter(Roll_No=roll_no).order_by('-Semester').first()
        
        # Get fee status
        fee_record = FeeRecord.objects.filter(Roll_No=roll_no).first()
        
        # Get activity record
        activity_record = ActivityRecord.objects.filter(Roll_No=roll_no).first()
        
        # Attendance Messages
        if latest_attendance:
            attendance_percent = latest_attendance.Attendance_Percent
            if attendance_percent >= 90:
                messages_list.append({
                    'type': 'success',
                    'title': 'Excellent Attendance! 🎉',
                    'message': f'Your attendance is {attendance_percent}%. Keep up the great work!',
                    'icon': '✅'
                })
            elif attendance_percent >= 75:
                messages_list.append({
                    'type': 'info',
                    'title': 'Good Attendance 👍',
                    'message': f'Your attendance is {attendance_percent}%. Maintain this consistency.',
                    'icon': '📊'
                })
            elif attendance_percent >= 60:
                messages_list.append({
                    'type': 'warning',
                    'title': 'Attendance Needs Improvement ⚠️',
                    'message': f'Your attendance is {attendance_percent}%. Try to improve your attendance.',
                    'icon': '📉'
                })
            else:
                messages_list.append({
                    'type': 'danger',
                    'title': 'Low Attendance Alert! 🔴',
                    'message': f'Your attendance is {attendance_percent}%. Please attend classes regularly.',
                    'icon': '🚨'
                })
        
        # Academic Performance Messages
        if latest_academic:
            if latest_academic.SGPA:
                sgpa = float(latest_academic.SGPA)
                if sgpa >= 9.0:
                    messages_list.append({
                        'type': 'success',
                        'title': 'Outstanding Performance! 🌟',
                        'message': f'Excellent SGPA of {sgpa}! Keep up the great work!',
                        'icon': '🏆'
                    })
                elif sgpa >= 8.0:
                    messages_list.append({
                        'type': 'success',
                        'title': 'Very Good Performance! 👍',
                        'message': f'Great SGPA of {sgpa}! You are doing well.',
                        'icon': '📚'
                    })
                elif sgpa >= 7.0:
                    messages_list.append({
                        'type': 'info',
                        'title': 'Good Performance 📊',
                        'message': f'Good SGPA of {sgpa}. There is room for improvement.',
                        'icon': '📈'
                    })
                elif sgpa >= 6.0:
                    messages_list.append({
                        'type': 'warning',
                        'title': 'Average Performance ⚠️',
                        'message': f'Your SGPA is {sgpa}. Focus on improving your grades.',
                        'icon': '📝'
                    })
                else:
                    messages_list.append({
                        'type': 'danger',
                        'title': 'Need Immediate Attention! 🔴',
                        'message': f'Your SGPA is {sgpa}. Please meet your mentor.',
                        'icon': '🚨'
                    })
            
            # Backlog messages
            if latest_academic.Backlogs and latest_academic.Backlogs > 0:
                if latest_academic.Backlogs <= 2:
                    messages_list.append({
                        'type': 'warning',
                        'title': 'Backlogs Alert ⚠️',
                        'message': f'You have {latest_academic.Backlogs} backlog(s). Focus on clearing them.',
                        'icon': '📚'
                    })
                else:
                    messages_list.append({
                        'type': 'danger',
                        'title': 'Multiple Backlogs! 🔴',
                        'message': f'You have {latest_academic.Backlogs} backlogs. Immediate attention required.',
                        'icon': '🚨'
                    })
        
        # Fee Status Messages
        if fee_record:
            if fee_record.Fee_Status == 'Pending':
                messages_list.append({
                    'type': 'danger',
                    'title': 'Fee Pending! 💰',
                    'message': f'Your fee of ₹{fee_record.Fee_Due} is pending. Please clear it soon.',
                    'icon': '💳'
                })
            elif fee_record.Fee_Status == 'Partial':
                messages_list.append({
                    'type': 'warning',
                    'title': 'Partial Fee Payment ⚠️',
                    'message': f'You have paid ₹{fee_record.Fee_Paid} out of ₹{fee_record.Total_Fee}.',
                    'icon': '💰'
                })
            elif fee_record.Fee_Status == 'Paid':
                messages_list.append({
                    'type': 'success',
                    'title': 'Fee Paid ✅',
                    'message': 'Your fees are fully paid. Thank you!',
                    'icon': '✅'
                })
        
        # Placement/Internship Messages
        if activity_record:
            if activity_record.Placement_Status == 'Placed':
                messages_list.append({
                    'type': 'success',
                    'title': 'Congratulations! 🎓',
                    'message': f'You are placed at {activity_record.Company_Name}. Well done!',
                    'icon': '🎉'
                })
            elif activity_record.Internship_Status == 'Completed':
                messages_list.append({
                    'type': 'success',
                    'title': 'Internship Completed ✅',
                    'message': 'Great job completing your internship!',
                    'icon': '💼'
                })
            elif activity_record.Internship_Status == 'Ongoing':
                messages_list.append({
                    'type': 'info',
                    'title': 'Internship in Progress 📅',
                    'message': 'Your internship is ongoing. Make the most of it!',
                    'icon': '📊'
                })
        
        # Behavior Rating Messages
        if latest_attendance and latest_attendance.Behaviour_Rating:
            behavior_rating = float(latest_attendance.Behaviour_Rating)
            if behavior_rating >= 9.0:
                messages_list.append({
                    'type': 'success',
                    'title': 'Excellent Behavior! 🌟',
                    'message': f'Your behavior rating is {behavior_rating}/10. Outstanding!',
                    'icon': '⭐'
                })
            elif behavior_rating <= 6.0:
                messages_list.append({
                    'type': 'warning',
                    'title': 'Behavior Improvement Needed ⚠️',
                    'message': f'Your behavior rating is {behavior_rating}/10. Please maintain discipline.',
                    'icon': '📝'
                })
        
        # If no specific messages, show welcome message
        if not messages_list:
            messages_list.append({
                'type': 'info',
                'title': 'Welcome Back! 👋',
                'message': 'Check your dashboard for latest updates and performance.',
                'icon': '📊'
            })
            
    except Exception as e:
        # Fallback welcome message
        messages_list.append({
            'type': 'info',
            'title': 'Welcome! 👋',
            'message': 'Good to see you back in the system.',
            'icon': '🎓'
        })
    
    return messages_list

def student_dashboard(request):
    if not request.session.get('login') or request.session.get('user_type') != 'student':
        return redirect('student_login')
    
    roll_no = request.session.get('roll_no')
    student = Student.objects.get(Roll_No=roll_no)
    return render(request, 'student_dashboard.html', {'student': student})

def view_profile(request):
    if not request.session.get('login') or request.session.get('user_type') != 'student':
        return redirect('student_login')
    
    roll_no = request.session.get('roll_no')
    student = Student.objects.get(Roll_No=roll_no)
    return render(request, 'view_profile.html', {'student': student})

def view_academic_details(request):
    if not request.session.get('login') or request.session.get('user_type') != 'student':
        return redirect('student_login')
    
    roll_no = request.session.get('roll_no')
    student = Student.objects.get(Roll_No=roll_no)
    academic_data = AcademicPerformance.objects.filter(Roll_No=roll_no)
    return render(request, 'academic_details.html', {
        'student': student,
        'academic_data': academic_data
    })

def view_financial_details(request):
    if not request.session.get('login') or request.session.get('user_type') != 'student':
        return redirect('student_login')
    
    roll_no = request.session.get('roll_no')
    student = Student.objects.get(Roll_No=roll_no)
    fee_data = FeeRecord.objects.filter(Roll_No=roll_no).first()
    return render(request, 'financial_details.html', {
        'student': student,
        'fee_data': fee_data
    })

def view_library_status(request):
    if not request.session.get('login') or request.session.get('user_type') != 'student':
        return redirect('student_login')
    
    roll_no = request.session.get('roll_no')
    student = Student.objects.get(Roll_No=roll_no)
    activity_data = ActivityRecord.objects.filter(Roll_No=roll_no).first()
    return render(request, 'library_status.html', {
        'student': student,
        'activity_data': activity_data
    })

def view_disciplinary_status(request):
    if not request.session.get('login') or request.session.get('user_type') != 'student':
        return redirect('student_login')
    
    roll_no = request.session.get('roll_no')
    student = Student.objects.get(Roll_No=roll_no)
    disciplinary_data = DisciplinaryRecord.objects.filter(Roll_No=roll_no).first()
    return render(request, 'disciplinary_status.html', {
        'student': student,
        'disciplinary_data': disciplinary_data
    })

def student_logout(request):
    request.session.flush()
    return redirect('/')

# Admin Views
# def admin_login(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         password = request.POST.get('password')

#         if email == 'admin@gmail.com' and password == 'admin':
#             request.session['email'] = email
#             request.session['user_type'] = 'admin'
#             request.session['login'] = True
#             return redirect('admin_dashboard')
#         else:
#             messages.error(request, 'Invalid Credentials')
#             return redirect('admin_login')
        
#     return render(request, 'admin_login.html')

# def admin_dashboard(request):
#     if not request.session.get('login') or request.session.get('user_type') != 'admin':
#         return redirect('admin_login')
    
#     total_students = Student.objects.count()
#     return render(request, 'admin_dashboard.html', {'total_students': total_students})

# def admin_logout(request):
#     request.session.flush()
#     return redirect('admin_login')

# # Admin Management Functions
# def manage_students(request):
#     if not request.session.get('login') or request.session.get('user_type') != 'admin':
#         return redirect('admin_login')
    
#     students = Student.objects.all()
    
#     if request.method == 'POST':
#         if 'add_student' in request.POST:
#             Roll_No = request.POST.get('Roll_No')
#             Name = request.POST.get('Name')
#             Dept = request.POST.get('Dept')
#             Year = request.POST.get('Year')
#             Semester = request.POST.get('Semester')
#             Joined_Year = request.POST.get('Joined_Year')
#             Passed_Out_Year = request.POST.get('Passed_Out_Year')
            
#             Student.objects.create(
#                 Roll_No=Roll_No,
#                 Name=Name,
#                 Dept=Dept,
#                 Year=Year,
#                 Semester=Semester,
#                 Joined_Year=Joined_Year,
#                 Passed_Out_Year=Passed_Out_Year
#             )
#             messages.success(request, 'Student added successfully')
        
#         elif 'delete_student' in request.POST:
#             roll_no = request.POST.get('roll_no')
#             Student.objects.filter(Roll_No=roll_no).delete()
#             messages.success(request, 'Student deleted successfully')
    
#     return render(request, 'manage_students.html', {'students': students})

# def manage_academic(request):
#     if not request.session.get('login') or request.session.get('user_type') != 'admin':
#         return redirect('admin_login')
    
#     if request.method == 'POST':
#         Roll_No = request.POST.get('Roll_No')
#         Semester = request.POST.get('Semester')
        
#         try:
#             student = Student.objects.get(Roll_No=Roll_No)
#             AcademicPerformance.objects.create(
#                 Roll_No=Roll_No,
#                 Dept=student.Dept,
#                 Semester=Semester,
#                 Thesis_Work=request.POST.get('Thesis_Work'),
#                 Seminar=request.POST.get('Seminar'),
#                 Internship=request.POST.get('Internship'),
#                 Project_Presentation=request.POST.get('Project_Presentation'),
#                 SGPA=request.POST.get('SGPA'),
#                 CGPA=request.POST.get('CGPA'),
#                 Backlogs=request.POST.get('Backlogs', 0),
#                 AI_Applications=request.POST.get('AI_Applications') == 'on',
#                 Cloud_Computing=request.POST.get('Cloud_Computing') == 'on',
#                 Embedded_Systems=request.POST.get('Embedded_Systems') == 'on',
#                 Cybersecurity=request.POST.get('Cybersecurity') == 'on',
#                 Deep_Learning=request.POST.get('Deep_Learning') == 'on',
#                 IoT_Systems=request.POST.get('IoT_Systems') == 'on',
#                 Big_Data_Analytics=request.POST.get('Big_Data_Analytics') == 'on',
#                 Optimization_Techniques=request.POST.get('Optimization_Techniques') == 'on',
#                 Advanced_Algorithms=request.POST.get('Advanced_Algorithms') == 'on',
#                 Machine_Learning=request.POST.get('Machine_Learning') == 'on',
#                 Data_Analytics=request.POST.get('Data_Analytics') == 'on',
#                 Research_Methodology=request.POST.get('Research_Methodology') == 'on',
#             )
#             messages.success(request, 'Academic data added successfully')
#         except Student.DoesNotExist:
#             messages.error(request, 'Student not found')
    
#     return render(request, 'manage_academic.html')

# def manage_attendance(request):
#     if not request.session.get('login') or request.session.get('user_type') != 'admin':
#         return redirect('admin_login')
    
#     if request.method == 'POST':
#         Roll_No = request.POST.get('Roll_No')
#         Semester = request.POST.get('Semester')
        
#         try:
#             student = Student.objects.get(Roll_No=Roll_No)
#             AttendanceRecord.objects.create(
#                 Roll_No=Roll_No,
#                 Dept=student.Dept,
#                 Semester=Semester,
#                 Attendance_Percent=request.POST.get('Attendance_Percent'),
#                 Absent_Days=request.POST.get('Absent_Days'),
#                 Medical_Leaves=request.POST.get('Medical_Leaves', 0),
#                 Behaviour_Rating=request.POST.get('Behaviour_Rating')
#             )
#             messages.success(request, 'Attendance record added successfully')
#         except Student.DoesNotExist:
#             messages.error(request, 'Student not found')
    
#     return render(request, 'manage_attendance.html')

# def manage_fees(request):
#     if not request.session.get('login') or request.session.get('user_type') != 'admin':
#         return redirect('admin_login')
    
#     if request.method == 'POST':
#         Roll_No = request.POST.get('Roll_No')
        
#         try:
#             student = Student.objects.get(Roll_No=Roll_No)
#             FeeRecord.objects.create(
#                 Roll_No=Roll_No,
#                 Dept=student.Dept,
#                 Total_Fee=request.POST.get('Total_Fee'),
#                 Fee_Paid=request.POST.get('Fee_Paid'),
#                 Fee_Due=request.POST.get('Fee_Due'),
#                 Fee_Status=request.POST.get('Fee_Status')
#             )
#             messages.success(request, 'Fee record added successfully')
#         except Student.DoesNotExist:
#             messages.error(request, 'Student not found')
    
#     return render(request, 'manage_fees.html')

# def manage_library(request):
#     if not request.session.get('login') or request.session.get('user_type') != 'admin':
#         return redirect('admin_login')
    
#     if request.method == 'POST':
#         Roll_No = request.POST.get('Roll_No')
        
#         try:
#             student = Student.objects.get(Roll_No=Roll_No)
#             ActivityRecord.objects.create(
#                 Roll_No=Roll_No,
#                 Dept=student.Dept,
#                 Library_Hours=request.POST.get('Library_Hours'),
#                 Books_Borrowed=request.POST.get('Books_Borrowed'),
#                 Mock_Test_Score=request.POST.get('Mock_Test_Score'),
#                 Placement_Attendance=request.POST.get('Placement_Attendance'),
#                 Internship_Status=request.POST.get('Internship_Status'),
#                 Placement_Status=request.POST.get('Placement_Status'),
#                 Company_Name=request.POST.get('Company_Name')
#             )
#             messages.success(request, 'Activity record added successfully')
#         except Student.DoesNotExist:
#             messages.error(request, 'Student not found')
    
#     return render(request, 'manage_library.html')

# def manage_disciplinary(request):
#     if not request.session.get('login') or request.session.get('user_type') != 'admin':
#         return redirect('admin_login')
    
#     if request.method == 'POST':
#         Roll_No = request.POST.get('Roll_No')
        
#         try:
#             student = Student.objects.get(Roll_No=Roll_No)
#             DisciplinaryRecord.objects.create(
#                 Roll_No=Roll_No,
#                 Action_Taken=request.POST.get('Action_Taken') == 'on',
#                 Description=request.POST.get('Description')
#             )
#             messages.success(request, 'Disciplinary record added successfully')
#         except Student.DoesNotExist:
#             messages.error(request, 'Student not found')
    
#     return render(request, 'manage_disciplinary.html')



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import *

# Admin Authentication
def admin_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if email == 'admin@gmail.com' and password == 'admin':
            request.session['email'] = email
            request.session['user_type'] = 'admin'
            request.session['login'] = True
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid Credentials')
            return redirect('admin_login')
        
    return render(request, 'admin_login.html')

def admin_dashboard(request):
    if not request.session.get('login') or request.session.get('user_type') != 'admin':
        return redirect('admin_login')
    
    total_students = Student.objects.count()
    total_academic_records = AcademicPerformance.objects.count()
    total_attendance_records = AttendanceRecord.objects.count()
    total_fee_records = FeeRecord.objects.count()
    
    context = {
        'total_students': total_students,
        'total_academic_records': total_academic_records,
        'total_attendance_records': total_attendance_records,
        'total_fee_records': total_fee_records,
    }
    return render(request, 'admin_dashboard.html', context)

def admin_logout(request):
    request.session.flush()
    return redirect('/')

# Student Management
def manage_students(request):
    if not request.session.get('login') or request.session.get('user_type') != 'admin':
        return redirect('admin_login')
    
    students = Student.objects.all()
    search_results = None
    
    # Handle search functionality
    search_roll_no = request.GET.get('search_roll_no', '').strip()
    if search_roll_no:
        search_results = Student.objects.filter(Roll_No__icontains=search_roll_no)
    
    if request.method == 'POST':
        if 'add_student' in request.POST:
            Roll_No = request.POST.get('Roll_No')
            Name = request.POST.get('Name')
            Dept = request.POST.get('Dept')
            Year = request.POST.get('Year')
            Semester = request.POST.get('Semester')
            Joined_Year = request.POST.get('Joined_Year')
            Passed_Out_Year = request.POST.get('Passed_Out_Year')
            password = request.POST.get('password', 'student123')
            
            # Check if student already exists
            if Student.objects.filter(Roll_No=Roll_No).exists():
                messages.error(request, f'Student with Roll No {Roll_No} already exists!')
            else:
                Student.objects.create(
                    Roll_No=Roll_No,
                    Name=Name,
                    Dept=Dept,
                    Year=Year,
                    Semester=Semester,
                    Joined_Year=Joined_Year,
                    Passed_Out_Year=Passed_Out_Year,
                    password=password
                )
                messages.success(request, f'Student {Name} added successfully!')
        
        elif 'update_student' in request.POST:
            Roll_No = request.POST.get('Roll_No')
            Name = request.POST.get('Name')
            Dept = request.POST.get('Dept')
            Year = request.POST.get('Year')
            Semester = request.POST.get('Semester')
            Joined_Year = request.POST.get('Joined_Year')
            Passed_Out_Year = request.POST.get('Passed_Out_Year')
            
            try:
                student = Student.objects.get(Roll_No=Roll_No)
                student.Name = Name
                student.Dept = Dept
                student.Year = Year
                student.Semester = Semester
                student.Joined_Year = Joined_Year
                student.Passed_Out_Year = Passed_Out_Year
                student.save()
                messages.success(request, f'Student {Name} updated successfully!')
            except Student.DoesNotExist:
                messages.error(request, 'Student not found!')
        
        elif 'delete_student' in request.POST:
            roll_no = request.POST.get('roll_no')
            try:
                student = Student.objects.get(Roll_No=roll_no)
                student_name = student.Name
                student.delete()
                messages.success(request, f'Student {student_name} deleted successfully!')
            except Student.DoesNotExist:
                messages.error(request, 'Student not found!')
    
    return render(request, 'manage_students.html', {'students': students , 'search_results':search_results})

# Academic Performance Management
# def manage_academic(request):
#     if not request.session.get('login') or request.session.get('user_type') != 'admin':
#         return redirect('admin_login')
    
#     academic_records = AcademicPerformance.objects.all()
    
#     if request.method == 'POST':
#         Roll_No = request.POST.get('Roll_No')
#         Semester = request.POST.get('Semester')
        
#         try:
#             student = Student.objects.get(Roll_No=Roll_No)
            
#             # Handle subject marks - convert empty strings to None
#             def get_mark_value(value):
#                 return int(value) if value and value.strip() else None
            
#             academic_record, created = AcademicPerformance.objects.update_or_create(
#                 Roll_No=Roll_No,
#                 Semester=Semester,
#                 defaults={
#                     'Dept': student.Dept,
#                     'Thesis_Work': request.POST.get('Thesis_Work') or None,
#                     'Seminar': request.POST.get('Seminar') or None,
#                     'Internship': request.POST.get('Internship') or None,
#                     'Project_Presentation': request.POST.get('Project_Presentation') or None,
#                     'SGPA': request.POST.get('SGPA') or None,
#                     'CGPA': request.POST.get('CGPA') or None,
#                     'Backlogs': request.POST.get('Backlogs', 0),
#                     'AI_Applications': get_mark_value(request.POST.get('AI_Applications')),
#                     'Cloud_Computing': get_mark_value(request.POST.get('Cloud_Computing')),
#                     'Embedded_Systems': get_mark_value(request.POST.get('Embedded_Systems')),
#                     'Cybersecurity': get_mark_value(request.POST.get('Cybersecurity')),
#                     'Deep_Learning': get_mark_value(request.POST.get('Deep_Learning')),
#                     'IoT_Systems': get_mark_value(request.POST.get('IoT_Systems')),
#                     'Big_Data_Analytics': get_mark_value(request.POST.get('Big_Data_Analytics')),
#                     'Optimization_Techniques': get_mark_value(request.POST.get('Optimization_Techniques')),
#                     'Advanced_Algorithms': get_mark_value(request.POST.get('Advanced_Algorithms')),
#                     'Machine_Learning': get_mark_value(request.POST.get('Machine_Learning')),
#                     'Data_Analytics': get_mark_value(request.POST.get('Data_Analytics')),
#                     'Research_Methodology': get_mark_value(request.POST.get('Research_Methodology')),
#                 }
#             )
            
#             if created:
#                 messages.success(request, f'Academic record for {Roll_No} Semester {Semester} created successfully!')
#             else:
#                 messages.success(request, f'Academic record for {Roll_No} Semester {Semester} updated successfully!')
                
#         except Student.DoesNotExist:
#             messages.error(request, f'Student with Roll No {Roll_No} not found!')
    
#     return render(request, 'manage_academic.html', {'academic_records': academic_records})




def manage_academic(request):
    if not request.session.get('login') or request.session.get('user_type') != 'admin':
        return redirect('admin_login')
    
    academic_records = AcademicPerformance.objects.all()
    search_results = None
    
    # Handle search functionality
    search_roll_no = request.GET.get('search_roll_no', '').strip()
    if search_roll_no:
        search_results = AcademicPerformance.objects.filter(Roll_No__icontains=search_roll_no)
    if request.method == 'POST':
        Roll_No = request.POST.get('Roll_No')
        Semester = request.POST.get('Semester')
        
        try:
            student = Student.objects.get(Roll_No=Roll_No)
            
            # Handle subject marks - convert empty strings to None
            def get_mark_value(value):
                return int(value) if value and value.strip() else None
            
            # Check if record already exists
            try:
                academic_record = AcademicPerformance.objects.get(Roll_No=Roll_No, Semester=Semester)
                created = False
                # Update only the fields that are provided in the form
                if request.POST.get('Thesis_Work'):
                    academic_record.Thesis_Work = request.POST.get('Thesis_Work')
                if request.POST.get('Seminar'):
                    academic_record.Seminar = request.POST.get('Seminar')
                if request.POST.get('Internship'):
                    academic_record.Internship = request.POST.get('Internship')
                if request.POST.get('Project_Presentation'):
                    academic_record.Project_Presentation = request.POST.get('Project_Presentation')
                if request.POST.get('SGPA'):
                    academic_record.SGPA = request.POST.get('SGPA')
                if request.POST.get('CGPA'):
                    academic_record.CGPA = request.POST.get('CGPA')
                if request.POST.get('Backlogs'):
                    academic_record.Backlogs = request.POST.get('Backlogs')
                
                # Update subject marks only if provided
                if request.POST.get('AI_Applications'):
                    academic_record.AI_Applications = get_mark_value(request.POST.get('AI_Applications'))
                if request.POST.get('Cloud_Computing'):
                    academic_record.Cloud_Computing = get_mark_value(request.POST.get('Cloud_Computing'))
                if request.POST.get('Embedded_Systems'):
                    academic_record.Embedded_Systems = get_mark_value(request.POST.get('Embedded_Systems'))
                if request.POST.get('Cybersecurity'):
                    academic_record.Cybersecurity = get_mark_value(request.POST.get('Cybersecurity'))
                if request.POST.get('Deep_Learning'):
                    academic_record.Deep_Learning = get_mark_value(request.POST.get('Deep_Learning'))
                if request.POST.get('IoT_Systems'):
                    academic_record.IoT_Systems = get_mark_value(request.POST.get('IoT_Systems'))
                if request.POST.get('Big_DataAnalytics'):
                    academic_record.Big_DataAnalytics = get_mark_value(request.POST.get('Big_DataAnalytics'))
                if request.POST.get('Optimization_Techniques'):
                    academic_record.Optimization_Techniques = get_mark_value(request.POST.get('Optimization_Techniques'))
                if request.POST.get('Advanced_Algorithms'):
                    academic_record.Advanced_Algorithms = get_mark_value(request.POST.get('Advanced_Algorithms'))
                if request.POST.get('Machine_Learning'):
                    academic_record.Machine_Learning = get_mark_value(request.POST.get('Machine_Learning'))
                if request.POST.get('Data_Analytics'):
                    academic_record.Data_Analytics = get_mark_value(request.POST.get('Data_Analytics'))
                if request.POST.get('Research_Methodology'):
                    academic_record.Research_Methodology = get_mark_value(request.POST.get('Research_Methodology'))
                
                academic_record.save()
                
            except AcademicPerformance.DoesNotExist:
                # Create new record with all provided values
                academic_record = AcademicPerformance.objects.create(
                    Roll_No=Roll_No,
                    Semester=Semester,
                    Dept=student.Dept,
                    Thesis_Work=request.POST.get('Thesis_Work') or None,
                    Seminar=request.POST.get('Seminar') or None,
                    Internship=request.POST.get('Internship') or None,
                    Project_Presentation=request.POST.get('Project_Presentation') or None,
                    SGPA=request.POST.get('SGPA') or None,
                    CGPA=request.POST.get('CGPA') or None,
                    Backlogs=request.POST.get('Backlogs', 0),
                    AI_Applications=get_mark_value(request.POST.get('AI_Applications')),
                    Cloud_Computing=get_mark_value(request.POST.get('Cloud_Computing')),
                    Embedded_Systems=get_mark_value(request.POST.get('Embedded_Systems')),
                    Cybersecurity=get_mark_value(request.POST.get('Cybersecurity')),
                    Deep_Learning=get_mark_value(request.POST.get('Deep_Learning')),
                    IoT_Systems=get_mark_value(request.POST.get('IoT_Systems')),
                    Big_DataAnalytics=get_mark_value(request.POST.get('Big_DataAnalytics')),
                    Optimization_Techniques=get_mark_value(request.POST.get('Optimization_Techniques')),
                    Advanced_Algorithms=get_mark_value(request.POST.get('Advanced_Algorithms')),
                    Machine_Learning=get_mark_value(request.POST.get('Machine_Learning')),
                    Data_Analytics=get_mark_value(request.POST.get('Data_Analytics')),
                    Research_Methodology=get_mark_value(request.POST.get('Research_Methodology')),
                )
                created = True
            
            if created:
                messages.success(request, f'Academic record for {Roll_No} Semester {Semester} created successfully!')
            else:
                messages.success(request, f'Academic record for {Roll_No} Semester {Semester} updated successfully!')
                
        except Student.DoesNotExist:
            messages.error(request, f'Student with Roll No {Roll_No} not found!')

    context = {
        'academic_records': academic_records,
        'search_results': search_results,
    }
    
    return render(request, 'manage_academic.html', context)





# Attendance Management
# def manage_attendance(request):
#     if not request.session.get('login') or request.session.get('user_type') != 'admin':
#         return redirect('admin_login')
    
#     attendance_records = AttendanceRecord.objects.all()
    
#     if request.method == 'POST':
#         Roll_No = request.POST.get('Roll_No')
#         Semester = request.POST.get('Semester')
        
#         try:
#             student = Student.objects.get(Roll_No=Roll_No)
            
#             attendance_record, created = AttendanceRecord.objects.update_or_create(
#                 Roll_No=Roll_No,
#                 Semester=Semester,
#                 defaults={
#                     'Dept': student.Dept,
#                     'Attendance_Percent': request.POST.get('Attendance_Percent'),
#                     'Absent_Days': request.POST.get('Absent_Days'),
#                     'Medical_Leaves': request.POST.get('Medical_Leaves', 0),
#                     'Behaviour_Rating': request.POST.get('Behaviour_Rating')
#                 }
#             )
            
#             if created:
#                 messages.success(request, f'Attendance record for {Roll_No} Semester {Semester} created successfully!')
#             else:
#                 messages.success(request, f'Attendance record for {Roll_No} Semester {Semester} updated successfully!')
                
#         except Student.DoesNotExist:
#             messages.error(request, f'Student with Roll No {Roll_No} not found!')
    
#     return render(request, 'manage_attendance.html', {'attendance_records': attendance_records})





def manage_attendance(request):
    if not request.session.get('login') or request.session.get('user_type') != 'admin':
        return redirect('admin_login')
    
    attendance_records = AttendanceRecord.objects.all()
    
    if request.method == 'POST':
        Roll_No = request.POST.get('Roll_No')
        Semester = request.POST.get('Semester')
        
        try:
            student = Student.objects.get(Roll_No=Roll_No)
            
            # Check if record already exists
            try:
                attendance_record = AttendanceRecord.objects.get(Roll_No=Roll_No, Semester=Semester)
                created = False
                
                # Update only the fields that are provided in the form
                if request.POST.get('Attendance_Percent'):
                    attendance_record.Attendance_Percent = request.POST.get('Attendance_Percent')
                if request.POST.get('Absent_Days'):
                    attendance_record.Absent_Days = request.POST.get('Absent_Days')
                if request.POST.get('Medical_Leaves'):
                    attendance_record.Medical_Leaves = request.POST.get('Medical_Leaves')
                if request.POST.get('Behaviour_Rating'):
                    attendance_record.Behaviour_Rating = request.POST.get('Behaviour_Rating')
                
                attendance_record.save()
                
            except AttendanceRecord.DoesNotExist:
                # Create new record with all provided values
                attendance_record = AttendanceRecord.objects.create(
                    Roll_No=Roll_No,
                    Semester=Semester,
                    Dept=student.Dept,
                    Attendance_Percent=request.POST.get('Attendance_Percent'),
                    Absent_Days=request.POST.get('Absent_Days'),
                    Medical_Leaves=request.POST.get('Medical_Leaves', 0),
                    Behaviour_Rating=request.POST.get('Behaviour_Rating')
                )
                created = True
            
            if created:
                messages.success(request, f'Attendance record for {Roll_No} Semester {Semester} created successfully!')
            else:
                messages.success(request, f'Attendance record for {Roll_No} Semester {Semester} updated successfully!')
                
        except Student.DoesNotExist:
            messages.error(request, f'Student with Roll No {Roll_No} not found!')
    
    return render(request, 'manage_attendance.html', {'attendance_records': attendance_records})












# Fee Management
def manage_fees(request):
    if not request.session.get('login') or request.session.get('user_type') != 'admin':
        return redirect('admin_login')
    
    fee_records = FeeRecord.objects.all()
    
    if request.method == 'POST':
        Roll_No = request.POST.get('Roll_No')
        
        try:
            student = Student.objects.get(Roll_No=Roll_No)
            
            # Check if record already exists
            try:
                fee_record = FeeRecord.objects.get(Roll_No=Roll_No)
                created = False
                
                # Update only the fields that are provided in the form
                if request.POST.get('Total_Fee'):
                    fee_record.Total_Fee = request.POST.get('Total_Fee')
                if request.POST.get('Fee_Paid'):
                    fee_record.Fee_Paid = request.POST.get('Fee_Paid')
                if request.POST.get('Fee_Due'):
                    fee_record.Fee_Due = request.POST.get('Fee_Due')
                if request.POST.get('Fee_Status'):
                    fee_record.Fee_Status = request.POST.get('Fee_Status')
                
                fee_record.save()
                
            except FeeRecord.DoesNotExist:
                # Create new record with all provided values
                fee_record = FeeRecord.objects.create(
                    Roll_No=Roll_No,
                    Dept=student.Dept,
                    Total_Fee=request.POST.get('Total_Fee'),
                    Fee_Paid=request.POST.get('Fee_Paid'),
                    Fee_Due=request.POST.get('Fee_Due'),
                    Fee_Status=request.POST.get('Fee_Status', 'Pending')  # Default status
                )
                created = True
            
            if created:
                messages.success(request, f'Fee record for {Roll_No} created successfully!')
            else:
                messages.success(request, f'Fee record for {Roll_No} updated successfully!')
                
        except Student.DoesNotExist:
            messages.error(request, f'Student with Roll No {Roll_No} not found!')
        except Exception as e:
            messages.error(request, f'Error updating fee record: {str(e)}')
    
    return render(request, 'manage_fees.html', {'fee_records': fee_records})

# Library & Placement Management
def manage_library(request):
    if not request.session.get('login') or request.session.get('user_type') != 'admin':
        return redirect('admin_login')
    
    activity_records = ActivityRecord.objects.all()
    
    if request.method == 'POST':
        Roll_No = request.POST.get('Roll_No')
        
        try:
            student = Student.objects.get(Roll_No=Roll_No)
            
            # Check if record already exists
            try:
                activity_record = ActivityRecord.objects.get(Roll_No=Roll_No)
                created = False
                
                # Update only the fields that are provided in the form
                if request.POST.get('Library_Hours'):
                    activity_record.Library_Hours = request.POST.get('Library_Hours')
                if request.POST.get('Books_Borrowed'):
                    activity_record.Books_Borrowed = request.POST.get('Books_Borrowed')
                if request.POST.get('Mock_Test_Score'):
                    activity_record.Mock_Test_Score = request.POST.get('Mock_Test_Score')
                if request.POST.get('Placement_Attendance'):
                    activity_record.Placement_Attendance = request.POST.get('Placement_Attendance')
                if request.POST.get('Internship_Status'):
                    activity_record.Internship_Status = request.POST.get('Internship_Status')
                if request.POST.get('Placement_Status'):
                    activity_record.Placement_Status = request.POST.get('Placement_Status')
                if request.POST.get('Company_Name'):
                    activity_record.Company_Name = request.POST.get('Company_Name')
                
                activity_record.save()
                
            except ActivityRecord.DoesNotExist:
                # Create new record with all provided values
                activity_record = ActivityRecord.objects.create(
                    Roll_No=Roll_No,
                    Dept=student.Dept,
                    Library_Hours=request.POST.get('Library_Hours', 0),
                    Books_Borrowed=request.POST.get('Books_Borrowed', 0),
                    Mock_Test_Score=request.POST.get('Mock_Test_Score') or None,
                    Placement_Attendance=request.POST.get('Placement_Attendance', 0),
                    Internship_Status=request.POST.get('Internship_Status', 'Not Started'),
                    Placement_Status=request.POST.get('Placement_Status', 'Not Placed'),
                    Company_Name=request.POST.get('Company_Name') or None
                )
                created = True
            
            if created:
                messages.success(request, f'Activity record for {Roll_No} created successfully!')
            else:
                messages.success(request, f'Activity record for {Roll_No} updated successfully!')
                
        except Student.DoesNotExist:
            messages.error(request, f'Student with Roll No {Roll_No} not found!')
        except Exception as e:
            messages.error(request, f'Error updating activity record: {str(e)}')
    
    return render(request, 'manage_library.html', {'activity_records': activity_records})

# Disciplinary Management
def manage_disciplinary(request):
    if not request.session.get('login') or request.session.get('user_type') != 'admin':
        return redirect('admin_login')
    
    disciplinary_records = DisciplinaryRecord.objects.all()
    
    if request.method == 'POST':
        Roll_No = request.POST.get('Roll_No')
        
        try:
            student = Student.objects.get(Roll_No=Roll_No)
            
            disciplinary_record, created = DisciplinaryRecord.objects.update_or_create(
                Roll_No=Roll_No,
                defaults={
                    'Action_Taken': request.POST.get('Action_Taken') == 'on',
                    'Description': request.POST.get('Description') or None
                }
            )
            
            if created:
                messages.success(request, f'Disciplinary record for {Roll_No} created successfully!')
            else:
                messages.success(request, f'Disciplinary record for {Roll_No} updated successfully!')
                
        except Student.DoesNotExist:
            messages.error(request, f'Student with Roll No {Roll_No} not found!')
    
    return render(request, 'manage_disciplinary.html', {'disciplinary_records': disciplinary_records})

# Search and View Student Details
def admin_search_student(request):
    if not request.session.get('login') or request.session.get('user_type') != 'admin':
        return redirect('admin_login')
    
    students = []
    search_query = ""
    
    if request.method == 'POST':
        search_query = request.POST.get('search_query', '').strip()
        if search_query:
            students = Student.objects.filter(
                Q(Roll_No__icontains=search_query) | 
                Q(Name__icontains=search_query) |
                Q(Dept__icontains=search_query)
            )[:50]
            
            if not students:
                messages.info(request, f'No students found for "{search_query}"')
    
    return render(request, 'admin_search_student.html', {
        'students': students,
        'search_query': search_query
    })

def admin_student_details(request, roll_no):
    if not request.session.get('login') or request.session.get('user_type') != 'admin':
        return redirect('admin_login')
    
    try:
        student = Student.objects.get(Roll_No=roll_no)
        academic_data = AcademicPerformance.objects.filter(Roll_No=roll_no).order_by('Semester')
        attendance_data = AttendanceRecord.objects.filter(Roll_No=roll_no).order_by('Semester')
        fee_data = FeeRecord.objects.filter(Roll_No=roll_no).first()
        activity_data = ActivityRecord.objects.filter(Roll_No=roll_no).first()
        disciplinary_data = DisciplinaryRecord.objects.filter(Roll_No=roll_no).first()
        
        context = {
            'student': student,
            'academic_data': academic_data,
            'attendance_data': attendance_data,
            'fee_data': fee_data,
            'activity_data': activity_data,
            'disciplinary_data': disciplinary_data,
        }
        return render(request, 'admin_student_details.html', context)
        
    except Student.DoesNotExist:
        messages.error(request, 'Student not found')
        return redirect('admin_search_student')

# Bulk Operations
def bulk_operations(request):
    if not request.session.get('login') or request.session.get('user_type') != 'admin':
        return redirect('admin_login')
    
    if request.method == 'POST':
        # Handle bulk operations here
        messages.info(request, 'Bulk operations feature coming soon!')
    
    return render(request, 'bulk_operations.html')
def analytics_portal(request):
    return render(request, "analytics_portal.html")
from django.shortcuts import render
from .models import AcademicPerformance

def filter_top_performers(request):
    dept = request.GET.get("dept")
    sem = request.GET.get("semester")

    data = AcademicPerformance.objects.filter(
        Dept=dept,
        Semester=sem
    ).exclude(CGPA=None).order_by("-CGPA").values(
        "Roll_No", "Dept", "Semester", "CGPA"
    )[:10]

    return render(request, "analytics_portal.html", {
        "results": list(data),
        "heading": f"Top Performers (CGPA) - {dept} Sem {sem}"
    })


from .models import AttendanceRecord

def filter_low_attendance(request):
    dept = request.GET.get("dept")
    sem = request.GET.get("semester")

    data = AttendanceRecord.objects.filter(
        Dept=dept, Semester=sem, Attendance_Percent__lt=75
    )

    return render(request, "analytics_portal.html", {
        "results": list(data.values()),
        "heading": f"Low Attendance (<75%) in {dept} - Sem {sem}"
    })

from django.shortcuts import render
from app.models import AcademicPerformance  # Ensure this model is imported


def filter_backlogs(request):
    dept = request.GET.get('dept')
    semester = request.GET.get('semester')

    students = AcademicPerformance.objects.filter(
        Dept=dept,
        Semester=semester,
        Backlogs__gt=0   # <-- Only students with backlogs
    )

    return render(request, "filter_results.html", {
        "title": "Backlog Students",
        "students": students,
        "message": f"Students with backlogs in {dept} - Semester {semester}"
    })
# 🎯 CGPA Risk Zone (CGPA < 6)
def filter_cgpa_risk(request):
    dept = request.GET.get("dept")
    semester = request.GET.get("semester")

    students = AcademicPerformance.objects.filter(
        Dept=dept, Semester=semester, CGPA__lt=6
    )

    context = {
        "title": "⚠️ CGPA Risk Zone (CGPA < 6)",
        "message": f"Students in CGPA risk zone from {dept} - Semester {semester}",
        "students": students,
    }

    return render(request, "filter_results.html", context)
# 🚨 Behaviour Rating < 5
def filter_behavior_rating(request):
    dept = request.GET.get("dept")
    semester = request.GET.get("semester")
    results = AttendanceRecord.objects.filter(Dept=dept, Semester=semester, Behaviour_Rating__lt=5)
    return render(request, "filter_results.html", {
        "title": "🚨 Behaviour Rating Issues (Rating < 5)",
        "message": f"{dept} - Semester {semester}",
        "students": results,
    })

# 💸 Partial Fee Payment (Fee Due still exists)
def filter_partial_fee(request):
    dept = request.GET.get("dept")

    data = FeeRecord.objects.filter(
        Dept=dept,
        Fee_Due__gt=0,
        Fee_Paid__gt=0
    ).values(
        "Roll_No",
        "Dept",
        "Total_Fee",
        "Fee_Paid",
        "Fee_Due",
        "Fee_Status"
    )

    return render(request, "analytics_portal.html", {
        "results": list(data),
        "heading": f"Partial Fee Payment Students - {dept} Dept"
    })


# 🏆 Placed Students (Final Years Only)
def filter_placed(request):
    dept = request.GET.get("dept")

    data = ActivityRecord.objects.filter(
        Dept=dept,
        Placement_Status="Placed"
    ).values(
        "Roll_No",
        "Dept",
        "Placement_Status",
        "Company_Name"
    )

    return render(request, "analytics_portal.html", {
        "results": list(data),
        "heading": f"Placed Students - {dept} Department"
    })


# 😕 Not Placed Students
from app.models import ActivityRecord, Student

def filter_not_placed(request):
    dept = request.GET.get("dept")

    # Step 1: Get 4th semester students of that department
    fourth_sem_students = Student.objects.filter(
        Dept=dept,
        Semester=4
    ).values_list("Roll_No", flat=True)

    # Step 2: Get NOT PLACED students from ActivityRecord
    data = ActivityRecord.objects.filter(
        Dept=dept,
        Placement_Status="Not Placed",
        Roll_No__in=fourth_sem_students
    ).values(
        "Roll_No",
        "Dept",
        "Placement_Status"
    )

    return render(request, "analytics_portal.html", {
        "results": list(data),
        "heading": f"Not Placed Students (4th Semester) - {dept}"
    })


# ❌ Internship Not Completed
from app.models import ActivityRecord, Student

def filter_internship_not_done(request):
    dept = request.GET.get("dept")

    # Step 1: Get 4th semester students of the department
    fourth_sem_students = Student.objects.filter(
        Dept=dept,
        Semester=4
    ).values_list("Roll_No", flat=True)

    # Step 2: Filter internship NOT DONE students from ActivityRecord
    data = ActivityRecord.objects.filter(
        Dept=dept,
        Internship_Status="Not Done",
        Roll_No__in=fourth_sem_students
    ).values(
        "Roll_No",
        "Dept",
        "Internship_Status"
    )

    return render(request, "analytics_portal.html", {
        "results": list(data),
        "heading": f"Internship Not Done (4th Semester) - {dept}"
    })


# 📉 Mock Test Score Low (< 60 Marks)
from app.models import ActivityRecord, Student

def filter_mock_low(request):
    dept = request.GET.get("dept")

    # Step 1: Get 4th semester students of the department
    fourth_sem_students = Student.objects.filter(
        Dept=dept,
        Semester=4
    ).values_list("Roll_No", flat=True)

    # Step 2: Filter low mock test score students (< 60)
    data = ActivityRecord.objects.filter(
        Dept=dept,
        Mock_Test_Score__lt=60,
        Roll_No__in=fourth_sem_students
    ).values(
        "Roll_No",
        "Dept",
        "Mock_Test_Score"
    )

    return render(request, "analytics_portal.html", {
        "results": list(data),
        "heading": f"Low Mock Test Score (<60) – 4th Semester – {dept}"
    })

