from fpdf import FPDF
import os
from datetime import datetime

class ResumePDF:
    def __init__(self, data):
        self.pdf = FPDF()
        self.data = data
        
    def generate(self):
        self.pdf.add_page()
        self.add_header()
        self.add_contact_info()
        self.add_experience()
        self.add_education()
        self.add_projects()
        self.add_skills()
        return self.save_pdf()
    
    def add_header(self):
        #name section
        self.pdf.set_font('Arial', 'B', 24)
        self.pdf.cell(0, 10, self.data['name'], 0, 1, 'C')
        
        #occupation section
        self.pdf.set_font('Arial', 'I', 14)
        self.pdf.cell(0, 10, self.data['occupation'], 0, 1, 'C')
        self.pdf.ln(5)
    
    def add_contact_info(self):
        self.pdf.set_font('Arial', '', 10)
        
        #contatc
        contact_line = f"{self.data['email']} | {self.data['phone']} | {self.data['location']}"
        self.pdf.cell(0, 5, contact_line, 0, 1, 'C')
        
        #sociallinks
        social_line = f"LinkedIn: {self.data['linkedin']} | GitHub: {self.data['github']}"
        self.pdf.cell(0, 5, social_line, 0, 1, 'C')
        self.pdf.ln(10)
    
    def add_section_header(self, title):
        self.pdf.set_font('Arial', 'B', 14)
        self.pdf.cell(0, 10, title.upper(), 0, 1)
        self.pdf.line(10, self.pdf.get_y(), 200, self.pdf.get_y())
        self.pdf.ln(5)
    
    def add_experience(self):
        self.add_section_header('Professional Experience')
        self.pdf.set_font('Arial', '', 11)
        self.pdf.multi_cell(0, 5, self.data['experience'])
        self.pdf.ln(5)
    
    def add_education(self):
        self.add_section_header('Education')
        self.pdf.set_font('Arial', '', 11)
        self.pdf.multi_cell(0, 5, self.data['education'])
        self.pdf.ln(5)
    
    def add_projects(self):
        self.add_section_header('Projects')
        self.pdf.set_font('Arial', '', 11)
        self.pdf.multi_cell(0, 5, self.data['projects'])
        self.pdf.ln(5)
    
    def add_skills(self):
        self.add_section_header('Skills')
        self.pdf.set_font('Arial', '', 11)
        self.pdf.multi_cell(0, 5, self.data['skills'])
        self.pdf.ln(5)
    
    def save_pdf(self):
        # making a directory for resume
        if not os.path.exists('resumes'):
            os.makedirs('resumes')
            
        # pdf name with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"resumes/resume_{self.data['name'].replace(' ', '_')}_{timestamp}.pdf"
        
        self.pdf.output(filename)
        return filename

