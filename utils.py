from langchain_community.llms import Ollama
from pypdf import PdfReader
import pandas as pd
import re
from langchain.prompts import PromptTemplate
import textract
import tempfile
import ast

# Initialize Ollama LLM
llm = Ollama(base_url='http://localhost:11434', model="mistral")

# Extract Information from PDF file
def get_pdf_text(pdf_doc):
    text = ""
    pdf_reader = PdfReader(pdf_doc)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Extract Information from docx file
def get_docx_text(docx_doc):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp.write(docx_doc.getvalue())
        tmp_path = tmp.name

    text = textract.process(tmp_path).decode('utf-8')
    return text

def extract_data(pages_data, retry_count):
    if retry_count == 0:
        template = '''Extract the following values from the invoice data:
        - Invoice no. 
        - Date (in the format DD/MM/YYYY)
        - Client (listed after "TO:" or before the table)
        - Description, Hours, Rate, Amount from the table (Hours and Rate may be missing, in which case just extract the total Amount)
        
        Invoice data:
        {pages_data}
        
        Expected output format (use "N/A" for missing values):
        {{'Invoice no': 'INV0001', 'Date': '01/01/2023', 'Client': 'Client Name', 'Description': 'Service Description', 'Hours': 'N/A', 'Rate': 'N/A', 'Amount': '$100.00'}}
        '''
    else:
        template = '''The previous output had invalid syntax. Please try again to extract the following values from the invoice data:
        - Invoice no.
        - Date (in the format DD/MM/YYYY)
        - Client (listed after "TO:" or before the table)
        - Description, Hours, Rate, Amount from the table (Hours and Rate may be missing, in which case just extract the total Amount)
        
        Invoice data:
        {pages_data}
        
        Expected output format (use "N/A" for missing values):
        {{'Invoice no': 'INV0001', 'Date': '01/01/2023', 'Client': 'Client Name', 'Description': 'Service Description', 'Hours': 'N/A', 'Rate': 'N/A', 'Amount': '$100.00'}}
        '''

    prompt_template = PromptTemplate(input_variables=['pages_data'], template=template)
    full_response = llm.invoke(prompt_template.format(pages_data=pages_data))
    return full_response

# iterate over files in that user uploaded PDF and DOCX files, one by one
def create_docs(user_file_list, df):
    total_retries = 0
    for filename in user_file_list:
        file_extension = filename.name.split('.')[-1].lower()
        if file_extension == 'pdf':
            raw_data = get_pdf_text(filename)
        elif file_extension == 'docx':
            raw_data = get_docx_text(filename)
        else:
            print(f"Unsupported file format: {file_extension}")
            continue

        retries, data_dict = extract_data_with_retry(raw_data)
        total_retries += retries

        print("********************DONE***************")

    return total_retries, data_dict

def extract_data_with_retry(pages_data):
    max_retries = 5  # Number of times to retry in case of invalid syntax
    retry_count = 0

    while retry_count < max_retries:
        llm_extracted_data = extract_data(pages_data, retry_count)
        pattern = r'{(.+)}'
        match = re.search(pattern, llm_extracted_data, re.DOTALL)
        if match:
            extracted_text = match.group(1)
            try:
                data_dict = ast.literal_eval('{' + extracted_text + '}')
                return retry_count, data_dict
            except (ValueError, SyntaxError) as e:
                print(f"Invalid syntax in extracted text: {extracted_text}")
                retry_count += 1
                if retry_count < max_retries:
                    print(f"Retrying with feedback... (Attempt {retry_count + 1})")
                else:
                    print("Maximum retries reached. Skipping this file.")
                    return retry_count, {}
        else:
            print("No match found.")
            return retry_count, {}

    return retry_count, {}

def extract_data(pages_data, retry_count):
    if retry_count == 0:
        template = '''Extract the following values from the invoice data:
        - Invoice no. 
        - Date (in the format DD/MM/YYYY)
        - Client (listed after "TO:" or before the table)
        - Description, Hours, Rate, Amount from the table (Hours and Rate may be missing, in which case just extract the total Amount)
        
        Invoice data:
        {pages_data}
        
        Expected output format (use "N/A" for missing values):
        {{'Invoice no': 'JB201010', 'Date': '10/10/2020', 'Client': 'QUEENSLAND CONSERVATORIUM GRIFFITH UNIVERSITY', 'Description': 'City Sounds Josh Batka Quartet ($200 for myself) Bede Prince Connor Sharpe Spencer Wilson', 'Hours': '2hrs', 'Rate': '$100 ×4 = $400 × 2', 'Amount': '$800.00 AUD'}}
        '''
    else:
        template = '''The previous output had invalid syntax. Please try again to extract the following values from the invoice data:
        - Invoice no.
        - Date (in the format DD/MM/YYYY)
        - Client (listed after "TO:" or before the table)
        - Description, Hours, Rate, Amount from the table (Hours and Rate may be missing, in which case just extract the total Amount)
        
        Invoice data:
        {pages_data}
        
        Expected output format (use "N/A" for missing values):
        {{'Invoice no': 'JB201010', 'Date': '10/10/2020', 'Client': 'QUEENSLAND CONSERVATORIUM GRIFFITH UNIVERSITY', 'Description': 'City Sounds Josh Batka Quartet ($200 for myself) Bede Prince Connor Sharpe Spencer Wilson', 'Hours': '2hrs', 'Rate': '$100 ×4 = $400 × 2', 'Amount': '$800.00 AUD'}}
        '''

    prompt_template = PromptTemplate(input_variables=['pages_data'], template=template)
    full_response = llm.invoke(prompt_template.format(pages_data=pages_data))
    return full_response
