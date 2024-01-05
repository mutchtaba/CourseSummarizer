import time
import os
from openai import OpenAI
import threading
import slate3k as slate

# Initialize the OpenAI client with your API key
client = OpenAI(api_key="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")

# Specify the directory where your PDF files are located
pdf_directory = '/Users/admin/Desktop/course summarizer/'

# Get a list of PDF files in the directory
pdf_files = [file for file in os.listdir(pdf_directory) if file.endswith('.pdf')]

for pdf_file in pdf_files:
    with open(os.path.join(pdf_directory, pdf_file), 'rb') as f:
        doc = slate.PDF(f)

    clean_string = ""
    for item in doc:
        # Replace special characters with an empty string or space as needed
        item = item.replace('\t', '')  # Remove tabs
        item = item.replace('\r', '')  # Remove carriage returns
        item = item.replace('\xa0', ' ')  # Replace non-breaking spaces with a normal space
        item = item.replace('\u202f', ' ')  # Replace narrow no-break spaces with a normal space

        # Append the cleaned item to the clean_string
        clean_string += item

    # Generate a summary
    summary_completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Generate a summary written in markdown for the contents in the file"},
            {"role": "user", "content": clean_string}
        ]
    )

    # Generate multiple choice questions and answers
    mcq_completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Generate 10 multiple choice questions and answers based on the file given, format the answer in markdown"},
            {"role": "user", "content": clean_string}
        ]
    )

    # Print or save the results as needed
    print(f"Summary for {pdf_file}:\n{summary_completion.choices[0].message.content}")
    print(f"Multiple Choice Questions for {pdf_file}:\n{mcq_completion.choices[0].message.content}")
