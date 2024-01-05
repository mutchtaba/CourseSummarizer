import time
import os
from openai import OpenAI
import threading

# Initialize the OpenAI client with your API key
client = OpenAI(api_key="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")

def list_course_files(course_folder):
    return [f for f in os.listdir(course_folder) if os.path.isfile(os.path.join(course_folder, f))]

def create_file(filename, purpose):
    return client.files.create(file=open(filename, "rb"), purpose=purpose)

def list_assistants():
    return client.beta.assistants.list()

def create_assistant(name, instructions, model, file_ids):
    # Check if an assistant with the same name already exists
    assistants = list_assistants()
    for assistant in assistants.data:
        if assistant.name == name:
            print(f"An assistant with the name '{name}' already exists with ID: {assistant.id}")
            return assistant
    
    # If no existing assistant is found, create a new one
    return client.beta.assistants.create(
        name=name,
        instructions=instructions,
        tools=[{"type": "retrieval"}],
        model=model,
        file_ids=file_ids
    )

def create_thread():
    return client.beta.threads.create()

def send_message(thread_id, content, file_ids=[]):
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=content,
        file_ids=file_ids
    )

def start_run(thread_id, assistant_id, instructions):
    return client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
        instructions=instructions
    )

def get_run_status(thread_id, run_id):
    return client.beta.threads.runs.retrieve(
        thread_id=thread_id,
        run_id=run_id
    )

def get_messages(thread_id):
    return client.beta.threads.messages.list(
        thread_id=thread_id
    )

def generate_summary(assistant_id, file_id):
    thread = create_thread()
    send_message(thread.id, "Provide lecture notes on the following file: " + str(file_id))
    # Start a run
    run = start_run(thread.id, assistant_id, "Generate content notes/summary for CS3005 course files.")
    # Monitor the run until it's completed and print the response
    while True:
        run_status = get_run_status(thread.id, run.id)
        if run_status.status == 'completed':
            break
        time.sleep(1)  # Wait for 1 second before checking again
    # Retrieve and print messages
    messages = get_messages(thread.id)
    for message in reversed(messages.data):
        print(message.role + ': ' + message.content[0].text.value)

def generate_questions(assistant_id, file_id):
    thread = create_thread()
    send_message(thread.id, str(file_id))
    # Start a run
    run = start_run(thread.id, assistant_id, "Generate 10 multiple choice question and answers for the content provide to test a student knowledge on the subject based the following file: " + str(file_id))
    # Monitor the run until it's completed and print the response
    while True:
        run_status = get_run_status(thread.id, run.id)
        if run_status.status == 'completed':
            break
        time.sleep(1)  # Wait for 1 second before checking again
    # Retrieve and print messages
    messages = get_messages(thread.id)
    for message in reversed(messages.data):
        print(message.role + ': ' + message.content[0].text.value)

def main():
    course_folder = "/Users/admin/Desktop/course summarizer/CS3305"
    course_files = list_course_files(course_folder)
    file_ids = []
    

    # Upload all course files to OpenAI, 
    # for file in course_files:
    #     file_path = os.path.join(course_folder, file)
    #     uploaded_file = create_file(file_path, "assistants")
    #     file_ids.append(uploaded_file.id)

    # Create an assistant for the course and tag the course’s files under that assistant
    summary_assistant_name = "CS3005 Course Assistant"
    summary_assistant = create_assistant(
        summary_assistant_name,
        "You are a content summarizer for CS3005. Generate lecture notes on any files provided",
        "gpt-4-1106-preview",
        file_ids
    )

    question_assistant_name = "CS3305 Question Assistant"
    question_assistant = create_assistant(
        question_assistant_name,
        "You are question generator for an online course. Generate 10 multiple choice question and answers for the content provide to test a student knowledge on the subject",
        "gpt-4-1106-preview",
        file_ids
    )
    # Initialize a list to keep track of threads
    threads = []

    # Create a thread for each file and start the process
    for file_id in summary_assistant.file_ids:
        # thread = threading.Thread(target=generate_questions, args=(question_assistant.id, file_id))
        thread = threading.Thread(target=generate_summary, args=(summary_assistant.id, file_id))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

# Run the main function
if __name__ == "__main__":
    main()
