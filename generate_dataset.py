# Import necessary libraries
from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader
from langsmith import Client
from openai import OpenAI


# Load environment variables
load_dotenv()

# Load documents from a directory (you can change this path as needed)
documents = SimpleDirectoryReader("data").load_data()

client = OpenAI()

# Function to generate questions and answers
def generate_qa(prompt, text, temperature=0.2):    
    response = client.chat.completions.create(
        # model="gpt-4o-mini",
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": text}],
        temperature=temperature,
    )
    
    print(response.choices[0].message.content)

    # Strip extraneous symbols from the response content
    content = response.choices[0].message.content.strip()
    
    # Remove potential JSON code block markers
    content = content.strip()
    if content.startswith('```'):
        content = content.split('\n', 1)[-1]
    if content.endswith('```'):
        content = content.rsplit('\n', 1)[0]
    content = content.strip()
    
    # Attempt to parse the cleaned content as JSON
    try:
        parsed_content = json.loads(content.strip())
        return parsed_content
    except json.JSONDecodeError:
        print("Error: Unable to parse JSON. Raw content:")
        print(content)
        return []

factual_prompt = """
You are an expert educational content creator tasked with generating factual questions and answers based on the following document excerpt. 
These questions should focus on retrieving specific details, figures, definitions, and key facts from the text.

Instructions:

- Generate **5** factual questions, each with a corresponding **expected_output**.
- Ensure all questions are directly related to the document excerpt.
- Present the output in the following structured JSON format:

[
  {
    "question": "What is the main purpose of the project described in the document?",
    "expected_output": "To develop a new framework for data security using AI-powered tools."
  },
  {
    "question": "Who authored the report mentioned in the document?",
    "expected_output": "Dr. Jane Smith."
  }
]
"""

# Generate dataset
import os
import json

dataset_file = 'qa_dataset.json'

if os.path.exists(dataset_file):
    # Load dataset from local file if it exists
    with open(dataset_file, 'r') as f:
        dataset = json.load(f)
else:
    # Generate dataset if local file doesn't exist
    dataset = []
    for doc in documents:
        qa_pairs = generate_qa(factual_prompt, doc.text, temperature=0.2)
        dataset.extend(qa_pairs)
    
    # Write dataset to local file
    with open(dataset_file, 'w') as f:
        json.dump(dataset, f)


langsmithClient = Client()
dataset_name = "Consumer Product Research bot evalaution dataset"

# Store
dataset_ref = langsmithClient.create_dataset(
    dataset_name=dataset_name,
    description="QA pairs about Consumer Product Research bot",
)


for item in dataset:
    langsmithClient.create_examples(
    inputs=[{"question": item["question"]}],
    outputs=[{"answer": item["expected_output"]}],
    dataset_id=dataset_ref.id,
)