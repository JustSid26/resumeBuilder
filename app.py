from flask import Flask, render_template, request, flash, redirect, url_for, session, send_file
import google.generativeai as genai
import re
from resumepdf import ResumePDF
from abc import ABC, abstractmethod
from db import DatabaseHandler
import os
from dotenv import load_dotenv

load_dotenv()
class AIModelInterface(ABC):
    """Abstract base class for AI model interactions"""
    @abstractmethod
    def initialize_model(self):
        pass
    
    @abstractmethod
    def generate_content(self, prompt):
        pass

class GeminiModel(AIModelInterface):
    """Concrete implementation for Gemini AI model"""
    def __init__(self, api_key):
        self.__api_key = api_key  # Private attribute
        self.__model = None  # Private attribute
        self.initialize_model()
    
    @property
    def api_key(self):
        """Getter for api_key"""
        return self.__api_key
    
    def initialize_model(self):
        try:
            genai.configure(api_key=self.__api_key)
            self.__model = genai.GenerativeModel('gemini-2.0-flash')
        except Exception as e:
            raise AIModelInitializationError(f"Failed to initialize Gemini model: {str(e)}")
    
    def generate_content(self, prompt):
        try:
            if not self.__model:
                raise AIModelInitializationError("Model not initialized")
            response = self.__model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            raise AIContentGenerationError(f"Failed to generate content: {str(e)}")

class CustomException(Exception):
    """Base exception class for custom exceptions"""
    pass

class AIModelInitializationError(CustomException):
    """Raised when AI model initialization fails"""
    pass

class AIContentGenerationError(CustomException):
    """Raised when content generation fails"""
    pass

class AuthenticationError(CustomException):
    """Raised when authentication fails"""
    pass

class ResumeBuilder:
    """Class to handle resume building operations"""
    _section_prompts = {
        'experience': 'Convert these job experience keywords into short 2 sentences, make it as if you are writing a professional resume for urself and formal, only one option and dont term it as option just a text: ',
        'education': 'Convert these education detail keywords into short 2 sentences, make it as if you are writing a professional resume for urself and formal, only one option and dont term it as option just a text:',
        'skills': 'Convert these skillset keywords into short 2 sentences, make it as if you are writing a professional resume for urself and formal, only one option and dont term it as option just a text:',
        'projects': 'Convert these project experience and working keywords into short 2 sentences, make it as if you are writing a professional resume for urself and formal, only one option and dont term it as option just a text:'
    }

    def __init__(self, ai_model):
        self.__ai_model = ai_model  #private attributes
    
    @staticmethod
    def get_prompt_for_section(section_type):
        """Static method to get prompt for specific section"""
        return ResumeBuilder._section_prompts.get(section_type)
    
    def enhance_text(self, keywords, section_type):
        """Enhance text using AI model"""
        try:
            prompt = f"{self.get_prompt_for_section(section_type)}{keywords}"
            return self.__ai_model.generate_content(prompt)
        except AIContentGenerationError as e:
            raise AIContentGenerationError(f"Error enhancing {section_type}: {str(e)}")

class Authentication:
    """Class to handle authentication"""
    def __init__(self, username, password):
        self.__username = username  #private attribute
        self.__password = password  
    
    @property
    def username(self):
        """Getter for username"""
        return self.__username
    
    def verify_credentials(self, input_password):
        """Verify login credentials"""
        if input_password != self.__password:
            raise AuthenticationError("Invalid password")
        return True

class FlaskAppWrapper:
    """Class to wrap Flask application with all its routes and functionality"""
    def __init__(self):
        self.__app = Flask(__name__)  # Private attribute
        self.__app.secret_key = 'your_secret_key_here'
        self.__about = 'This is a simple portfolio/resume builder in which it will create a portfolio/resume for you based on your inputs. The portfolio/resume is also downloadable as a pdf. Try it, because it is free and convenient.'
        
        #initializing components
        self.__ai_model = GeminiModel(os.getenv("GEMINI_API_KEY"))
        self.__resume_builder = ResumeBuilder(self.__ai_model)

        self.__auth = Authentication(
        os.getenv("ADMIN_USERNAME"),
        os.getenv("ADMIN_PASSWORD")
)
        self.__register_routes()
    
    @property
    def about(self):
        """Getter for about text"""
        return self.__about
    
    @property
    def app(self):
        """Getter for Flask app"""
        return self.__app
    
    def __register_routes(self):  # Private method
        """Register all routes for the application"""
        
        @self.__app.route("/")
        def index():
            return render_template("index.html", about=self.__about)
        
        @self.__app.route("/portfolio")
        def portfolio_maker():
            return render_template("resume_form.html")
        
        @self.__app.route("/contact")
        def contact_info():
            return render_template("contact.html")
        
        @self.__app.route("/donate")
        def donate():
            return render_template("donate.html")
        
        @self.__app.route('/login', methods=['GET', 'POST'])
        def admin_login():
            if request.method == 'POST':
                try:
                    self.__auth.verify_credentials(request.form['password'])
                    return render_template("resume_form.html")
                except AuthenticationError as e:
                    return render_template('login.html', error=str(e))
            return render_template('login.html')
        
        @self.__app.route('/generate_resume', methods=['POST'])
        def generate_resume():
            try:
                #getting user information
                email = request.form.get('email', '')
                if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                    raise ValueError("Invalid email format")
                    
                resume_data = {
                    'name': request.form.get('name', ''),
                    'occupation': request.form.get('occupation', ''),
                    'email': email,
                    'phone': request.form.get('phone', ''),
                    'location': request.form.get('location', ''),
                    'linkedin': request.form.get('linkedin', ''),
                    'github': request.form.get('github', '')
                }

                for section in ['experience', 'education', 'projects', 'skills']:
                    resume_data[section] = self.__resume_builder.enhance_text(
                        request.form.getlist(section)[0] if section != 'skills' else request.form.get('skills', ''),
                        section
                    )

                #generates pdf
                resume = ResumePDF(resume_data)
                pdf_file = resume.generate()
                
                return send_file(pdf_file, as_attachment=True, download_name='resume.pdf')

            except (AIContentGenerationError, Exception) as e:
                print(f"Error generating resume: {str(e)}")
                return f"Error generating resume: {str(e)}", 400
    
    def run(self, host='0.0.0.0', port='10000', debug=True):
        """Run the Flask application"""
        self.__app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    app = FlaskAppWrapper()
    app.run()