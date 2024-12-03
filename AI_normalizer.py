import os
import json
import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Initialize OpenAI client with the API key from environment variables
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define base folder relative to the script location
BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))

# Define relative paths
TRANSCRIPTS_FOLDER = os.path.join(BASE_FOLDER, "transcripts")
PROCESSED_FILE = os.path.join(BASE_FOLDER, "processed_transcripts.txt")
MARKDOWN_OUTPUT_FOLDER = os.path.join(BASE_FOLDER, "markdown_journals")
DICTIONARY_TABLE_FOLDER = os.path.join(BASE_FOLDER, "dictionary_table")
DICTIONARY_FILE = os.path.join(DICTIONARY_TABLE_FOLDER, 'transcript_dictionary.json')

# Ensure output folders exist
os.makedirs(MARKDOWN_OUTPUT_FOLDER, exist_ok=True)
os.makedirs(DICTIONARY_TABLE_FOLDER, exist_ok=True)

# Load or initialize the transcript dictionary
def load_transcript_dictionary():
    if os.path.exists(DICTIONARY_FILE):
        with open(DICTIONARY_FILE, 'r') as f:
            return json.load(f)
    return {}

# Save the transcript dictionary
def save_transcript_dictionary(transcript_dict):
    with open(DICTIONARY_FILE, 'w') as f:
        json.dump(transcript_dict, f, indent=4)

# Function to create a journal entry from the transcript using OpenAI's newer API
def create_journal_entry(transcript_content, filename):
    # Prepare the prompt
    system_message = {
        "role": "system",
        "content": "You are a helpful journal assistant. Your job is to take the transcript of a person's day and format it as a journal entry in Markdown, summarizing events clearly."
    }

    user_message = {
        "role": "user",
        "content": f"""
        Transcript:
        {transcript_content}

        Please summarize and format this as a Markdown journal entry.
        """
    }
    
    # Call OpenAI API to generate the journal entry
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[system_message, user_message],
        max_tokens=1500,
        temperature=0.7
    )

    # Retrieve the generated text
    journal_entry = response.choices[0].message.content.strip()

    # Generate markdown file name based on date
    now = datetime.datetime.now().strftime("%d-%m-%y")
    entry_number = len([f for f in os.listdir(MARKDOWN_OUTPUT_FOLDER) if f.startswith(f"journal_{now}")]) + 1
    markdown_filename = os.path.join(MARKDOWN_OUTPUT_FOLDER, f"journal_{now}_{entry_number}.md")

    # Markdown template
    markdown_template = f"""
# Journal Entry {entry_number} - {now}

---

{journal_entry}

---

"""

    # Write the journal entry to the markdown file
    with open(markdown_filename, 'w') as md_file:
        md_file.write(markdown_template.strip())

    print(f"Journal entry saved as {markdown_filename}")

# Function to check for new transcripts, process them, and generate journal entries
def process_new_transcripts():
    transcript_dict = load_transcript_dictionary()

    # Get all transcript files in the transcripts folder
    all_transcripts = [f for f in os.listdir(TRANSCRIPTS_FOLDER) if f.endswith('.txt')]

    # Check for new transcripts that have not been processed
    unprocessed_transcripts = []
    for transcript_file in all_transcripts:
        # Check if transcript is already processed or not
        if transcript_file in transcript_dict and transcript_dict[transcript_file] == 1:
            print(f"Transcript {transcript_file} already processed. Skipping.")
        else:
            unprocessed_transcripts.append(transcript_file)

    if not unprocessed_transcripts:
        print("No new transcripts to process.")
        return

    # Process each unprocessed transcript
    for transcript_file in unprocessed_transcripts:
        transcript_path = os.path.join(TRANSCRIPTS_FOLDER, transcript_file)

        # Read the content of the transcript
        with open(transcript_path, 'r') as f:
            transcript_content = f.read()

        # Create a journal entry using OpenAI
        create_journal_entry(transcript_content, transcript_file)

        # Mark this transcript as processed in the dictionary
        transcript_dict[transcript_file] = 1

    # Save the updated transcript dictionary
    save_transcript_dictionary(transcript_dict)

    print(f"Processed {len(unprocessed_transcripts)} new transcripts.")

if __name__ == "__main__":
    process_new_transcripts()
