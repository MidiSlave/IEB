# IEB

## Invoice Extraction Bot

This is an invoice extraction bot built using Streamlit, LangChain, and a local Large Language Model (LLM). IEB can extract invoice data from PDF and DOCX files, including invoice number, date, client, description, hours, rate, and amount.

## Credits

This project was inspired by the blog post "Building Invoice Extraction Bot using LangChain and LLM" by Bilal Shaikh on Analytics Vidhya. (https://www.analyticsvidhya.com/blog/2023/10/building-invoice-extraction-bot-using-langchain-and-llm/)

## System and Model

IEB has been tested on a 2023 Mac mini with an M2 Pro chip and 16GB of RAM, using the Mistral model served through Ollama. The app can process invoices at an approximate rate of 5 seconds per invoice.

## Requirements

Python 3.6 or later
Streamlit
LangChain
LangChain-community
Pandas
PyPDF2
textract
tqdm
docx
tempfile
ast
Ollama (for serving the Mistral model locally)

You can install the required packages using pip:

pip install streamlit langchain langchain-community pandas PyPDF2 textract tqdm python-docx

Ollama needs to be installed separately. You can find the installation instructions on the Ollama GitHub repository. (https://github.com/ollama/ollama)

## Running the Bot

1. Clone or download the repository.
2. Navigate to the project directory.
3. Start the Ollama server with the Mistral model (ollama start mistral).
4. Run the following command to start the Streamlit app:

streamlit run app.py

5. Upload the invoices (PDF and docx files) in the Streamlit app.
6. Click the "Extract Data" button to process the invoices.
7. After processing, you can save the extracted data as a CSV file using the "Save CSV" button.

## Prompt Template

The bot uses the following prompt template to guide the LLM in extracting the invoice data:

Extract the following values from the invoice data:

Invoice no.
Date (in the format DD/MM/YYYY)
Client (listed after "TO:" or before the table)
Description, Hours, Rate, Amount from the table (Hours and Rate may be missing, in which case just extract the total Amount)
Invoice data:
{pages_data}

Expected output format (use "N/A" for missing values):
{{'Invoice no': 'INV0001', 'Date': '01/01/2023', 'Client': 'Client Name', 'Description': 'Service Description', 'Hours': '2 hours', 'Rate': '$50/h', 'Amount': '$100.00'}}

The expected output format has been anonymized to protect sensitive information.

## License

This project is licensed under the MIT License.

## Special Mention

This project was made by Nathan MacGregor, who has limited coding experience, but with the help of Claude.ai, was able to create this useful tool. The motivation behind this project was to help Nathan's wonderful partner, who is an accountant, by automating the tedious task of extracting invoice data.
