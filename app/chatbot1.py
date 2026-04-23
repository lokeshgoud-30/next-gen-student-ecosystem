# Adding the Gemini AI integration
import google.generativeai as genai

# 1. Setup your API Key
genai.configure(api_key="AIzaSyCrdpeWmcy5VS4bBp69Ss3X-dFsbu1PXkY")

# 2. Define the System Instruction (The "Brain" of your chatbot)
SYSTEM_INSTRUCTION = """
You are "EduAssist", an AI assistant for a Student Management System. You help students with academic queries, university information, and general guidance.

STUDENT MANAGEMENT SYSTEM FEATURES:
- Academic Records: SGPA, CGPA, subject marks, backlogs
- Attendance: Percentage, absent days, medical leaves
- Fees: Total fee, paid amount, due amount, payment status
- Library: Hours, books borrowed, study hours
- Placement: Internship status, placement status, company information
- Disciplinary: Action records, behavior ratings

RESPONSE GUIDELINES:
1. BE FRIENDLY, HELPFUL, AND PROFESSIONAL
2. Provide accurate information about student portal features
3. If asked about specific personal data (grades, attendance), explain that you don't have access to individual student records
4. Direct students to appropriate sections of the portal for specific information
5. Keep responses concise but informative
6. Use simple language without markdown or special symbols
7. Always maintain a positive and encouraging tone
8. If unsure, suggest contacting the department or administration

AVAILABLE SECTIONS IN STUDENT PORTAL:
- Dashboard: Overview and quick stats
- My Profile: Personal information
- Academic Details: Grades and performance
- Fee Details: Payment information
- Library & Placement: Library usage and career information
- Disciplinary Status: Behavior records
"""

# 3. Initialize the Model
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",  # Use the correct model version, in this case "gemini-2.5-flash"
    system_instruction=SYSTEM_INSTRUCTION
)

# 4. Function to handle text and images
def chat_bot(user_input=None, student_context=None):
    """
    Process user queries and generate a response with Gemini AI
    
    Args:
        user_input: Text query from the user
        student_context: Context about the student (department, year, semester)

    Returns:
        AI response as a string
    """
    context_info = ""
    if student_context:
        context_info = f"""
        CURRENT STUDENT CONTEXT (for personalized guidance):
        - Department: {student_context.get('dept', 'Not specified')}
        - Year: {student_context.get('year', 'Not specified')}
        - Semester: {student_context.get('semester', 'Not specified')}
        """
        full_prompt = f"{context_info}\nUSER'S QUESTION: {user_input}\n\nIMPORTANT: \n- Remember you don't have access to live student data\n- Guide them to the appropriate portal sections\n- Keep response simple and clear without any symbols or markdown\n- Be specific about which section of the portal to check\n\nEDUASSIST RESPONSE:"
    content = []
    
    # Add text input
    if user_input:
        content.append(user_input)
    
    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Error generating response: {str(e)}. Please try again."
