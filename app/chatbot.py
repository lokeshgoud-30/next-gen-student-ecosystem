import logging
from google import genai
from django.conf import settings

logger = logging.getLogger(__name__)

def get_gemini_client():
    """Initializes and returns the Gemini client."""
    api_key = getattr(settings, 'GEMINI_API_KEY', "AIzaSyCrdpeWmcy5VS4bBp69Ss3X-dFsbu1PXkY")
    if not api_key:
        logger.error("Gemini API key is missing in settings.")
        return None
    
    try:
        return genai.Client(api_key=api_key)
    except Exception as e:
        logger.error(f"Failed to initialize Gemini client: {e}")
        return None

def build_gemini_prompt(message, student_context=None):
    """Constructs the structured prompt for the AI."""
    base_prompt = """
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
    
    context_info = ""
    if student_context:
        context_info = f"""
CURRENT STUDENT CONTEXT (for personalized guidance):
- Department: {student_context.get('dept', 'Not specified')}
- Year: {student_context.get('year', 'Not specified')}
- Semester: {student_context.get('semester', 'Not specified')}
"""

    full_prompt = f"{base_prompt}\n{context_info}\nUSER'S QUESTION: {message}\n\nIMPORTANT: \n- Remember you don't have access to live student data\n- Guide them to the appropriate portal sections\n- Keep response simple and clear without any symbols or markdown\n- Be specific about which section of the portal to check\n\nEDUASSIST RESPONSE:"
    return full_prompt

def get_chatbot_response(message, student_context=None):
    """Main function to be called by views/other modules."""
    client = get_gemini_client()
    
    if not client:
        return "🤖 The AI assistant is currently unavailable. Please use the quick links or contact support for immediate help."
    
    try:
        prompt = build_gemini_prompt(message, student_context)
        
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )
        
        return response.text
        
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return "🤖 I'm experiencing some technical difficulties. Please try again in a moment or use the quick links for immediate assistance."
    

# response = model.generate_content(content)