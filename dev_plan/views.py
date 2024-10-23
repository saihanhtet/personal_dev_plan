from django.shortcuts import render
from .forms import ResumeForm
import os
import PyPDF2
import docx
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI
import markdown

# Load environment variables
load_dotenv(find_dotenv())

# Initialize OpenAI client

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


def convert_markdown_to_html(markdown_text):
    """Convert Markdown text to HTML."""
    html = markdown.markdown(markdown_text)
    return html


def upload_resume(request):
    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save()
            # Process the resume file
            development_plan = generate_development_plan(resume.file.path)
            resume.development_plan = convert_markdown_to_html(development_plan)  # Convert to HTML
            resume.save()
            return render(request, 'success.html', {'development_plan': resume.development_plan})  # Pass HTML to template
    else:
        form = ResumeForm()

    return render(request, 'upload.html', {'resume_form': form})

def generate_development_plan(resume_path):
    extension = os.path.splitext(resume_path)[1].lower()

    if extension == '.pdf':
        resume_content = extract_text_from_pdf(resume_path)
    elif extension == '.docx':
        resume_content = extract_text_from_docx(resume_path)
    else:
        raise ValueError("Unsupported file format")

    # Generate the development plan using OpenAI
    response = client.chat.completions.create(model="gpt-4o-mini",  # Adjust to your preferred model
    messages=[
        {"role": "system", "content": "You are a career advisor assistant."},
        {
            "role": "user",
            "content": f"""
                Based on this resume, generate a detailed personal development plan.

                The output should be in a **HTML tabular format** with the following columns:
                - Skill/Competency to Develop
                - Courses to Take (Online/Offline)
                - Timeline (Months to Completion)
                - Estimated Hours per Week
                - Additional Notes or Resources

                Resume Content:
                {resume_content}
                """
        }
    ])

    # Returning the generated tabular development plan
    return response.choices[0].message.content

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text

def extract_text_from_docx(docx_path):
    doc = docx.Document(docx_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text
