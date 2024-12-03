import os
import wave
import sys
import time
import datetime
import pyaudio  # Use sounddevice if you encounter issues with pyaudio
import keyboard  # To detect spacebar input
from google.cloud import speech
from AI_normalizer import process_new_transcripts  # Import the function to process transcripts

# Function to record audio from the microphone with a recording animation
def record_audio(filename):
    chunk = 1024  # Record in chunks
    format = pyaudio.paInt16  # 16-bit resolution
    channels = 1  # Mono channel
    rate = 16000  # 16kHz sample rate (Google Speech-to-Text recommendation)
    p = pyaudio.PyAudio()

    # Animation frames (rotating characters)
    animation_frames = ['|', '/', '-', '\\']
    animation_index = 0

    # Start recording
    print("Starting PyAudio...")
    try:
        stream = p.open(format=format, channels=channels, rate=rate,
                        input=True, frames_per_buffer=chunk)
        print("Recording... Press spacebar to stop recording.")
        frames = []

        # Record until the spacebar is pressed again
        while True:
            data = stream.read(chunk)
            frames.append(data)

            # Update the animation in the CLI
            sys.stdout.write(f"\rRecording {animation_frames[animation_index % len(animation_frames)]}")
            sys.stdout.flush()
            animation_index += 1

            # Sleep a bit to control the animation speed
            time.sleep(0.1)

            # Check if the spacebar is pressed
            if keyboard.is_pressed("space"):
                break

        print("\nRecording finished.")
        stream.stop_stream()
        stream.close()
        p.terminate()

        # Save the recorded data as a WAV file
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(p.get_sample_size(format))
            wf.setframerate(rate)
            wf.writeframes(b''.join(frames))
        print(f"Audio saved as {filename}")

    except Exception as e:
        print(f"Error recording audio: {e}")

# Function to transcribe audio using Google Cloud Speech-to-Text and save as a .txt file
def transcribe_audio_file(audio_filepath, transcript_filepath):
    client = speech.SpeechClient()

    # Read the audio file content
    with open(audio_filepath, 'rb') as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US"
    )
    print("---------------------------------------------------------------")
    print(f"Transcribing audio: {audio_filepath} ...")
    response = client.recognize(config=config, audio=audio)

    # Initialize an empty string to store the full transcript
    full_transcript = ""

    # Loop through the results and concatenate the transcripts
    for result in response.results:
        transcript = result.alternatives[0].transcript
        full_transcript += transcript + " "  # Add a space between segments
    
    # Write the final merged transcript to the .txt file
    with open(transcript_filepath, 'w') as txt_file:
        txt_file.write(full_transcript.strip())  # Remove any trailing spaces
    
    print(f"Transcription saved as {transcript_filepath}")
    print("---------------------------------------------------------------")

# Function to list available logs in a folder
def list_logs(folder):
    try:
        files = [f for f in os.listdir(folder) if f.endswith('.wav')]
        if files:
            print("Available logs:")
            for idx, file in enumerate(files, 1):
                print(f"{idx}. {file}")
        else:
            print("No logs found.")
    except Exception as e:
        print(f"Error listing logs: {e}")

# Function to generate unique filenames for both audio and transcripts based on the current date
def generate_filename(base_folder, file_type):
    now = datetime.datetime.now().strftime("%d-%m-%y")
    count = len([f for f in os.listdir(base_folder) if f.startswith(f"{file_type}_{now}")]) + 1
    return f"{file_type}_{now}_{count}"

# Main menu to interact with the journal system
def main_menu():
    while True:
        print("1. Start Journal")
        print("2. Check Previous Logs")
        print("3. Manage Logs")
        print("4. Exit")
        print("---------------------------------------------------------------")

        choice = input("Choose an option: ")

        if choice == "1":
            print("---------------------------------------------------------------")
            print("\nTo start recording, press the spacebar. To stop, press the spacebar again.")
            print("Please press space to begin...")
            keyboard.wait("space")
            print("---------------------------------------------------------------")
            start_journal()  # Start the journal process
            process_new_transcripts()  # Call the AI normalizer after the journal is processed
        elif choice == "2":
            check_previous_logs()
        elif choice == "3":
            manage_logs()
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

# Function to start recording and transcribing
def start_journal():
    base_folder = "Journal.ai"
    audio_folder = os.path.join(base_folder, "audios")
    transcript_folder = os.path.join(base_folder, "transcripts")

    # Ensure the "Journal.ai" folder and subfolders exist
    if not os.path.exists(base_folder):
        os.makedirs(base_folder)
    if not os.path.exists(audio_folder):
        os.makedirs(audio_folder)
    if not os.path.exists(transcript_folder):
        os.makedirs(transcript_folder)

    # Generate filenames for the audio and transcript based on date and count
    audio_filename = generate_filename(audio_folder, "audio")
    transcript_filename = generate_filename(transcript_folder, "transcript")

    # File paths for audio and transcript
    audio_filepath = os.path.join(audio_folder, f"{audio_filename}.wav")
    transcript_filepath = os.path.join(transcript_folder, f"{transcript_filename}.txt")

    # Record and transcribe the audio
    record_audio(audio_filepath)
    transcribe_audio_file(audio_filepath, transcript_filepath)

# Function to check previous logs
def check_previous_logs():
    audio_folder = os.path.join("Journal.ai", "audios")
    list_logs(audio_folder)

# Placeholder for managing logs (e.g., delete or archive logs)
def manage_logs():
    print("Manage logs functionality coming soon...")

if __name__ == "__main__":
    print("""
   ___                              _      ___  _____ 
  |_  |                            | |    / _ \\|_   _|
    | | ___  _   _ _ __ _ __   __ _| |   / /_\\ \\ | |  
    | |/ _ \\| | | | '__| '_ \\ / _` | |   |  _  | | |  
/\\__/ / (_) | |_| | |  | | | | (_| | |  _| | | |_| |_ 
\\____/ \\___/ \\__,_|_|  |_| |_|\\__,_|_| (_)_| |_\\___/ 
                                       
    """)
    # Show welcome screen
    print("""
 _    _      _                          
| |  | |    | |                         
| |  | | ___| | ___ ___  _ __ ___   ___ 
| |/\\| |/ _ \\ |/ __/ _ \\| '_ ` _ \\ / _ \\
\\  /\\  /  __/ | (_| (_) | | | | | |  __/
 \\/  \\/ \\___|_|\\___\\___/|_| |_| |_|\\___|
                                      

    """)
    # Start the main menu
    main_menu()
