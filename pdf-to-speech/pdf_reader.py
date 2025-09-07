import os
import sys
import pyttsx3
from pypdf import PdfReader


def initialize_engine():
    """
    Initializes the TTS engine and intelligently searches for an
    English-speaking female voice.
    """
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    english_female_voice = None

    for voice in voices:
        # The 'languages' attribute may not exist on all systems
        # It often looks like [b'\x02en-us']
        languages = getattr(voice, 'languages', [])
        lang_is_english = any('en' in str(lang).lower() for lang in languages)

        # The 'gender' attribute may also not exist
        gender = getattr(voice, 'gender', '').lower()

        # Some voice names on Windows/Mac are reliable identifiers
        name = voice.name.lower()
        is_female_by_name = any(fem_name in name for fem_name in ['zira', 'susan', 'serena', 'hazel'])

        if lang_is_english and (gender == 'female' or is_female_by_name):
            english_female_voice = voice.id
            break  # Stop searching once we find a good match

    if english_female_voice:
        print("Found an English female voice.")
        engine.setProperty('voice', english_female_voice)
    else:
        print("Could not find a dedicated English female voice. Using system default.")

    engine.setProperty('rate', 150)
    engine.setProperty('volume', 0.9)
    return engine


def extract_text_from_pdf(file_path):
    """Extracts all text from a given PDF file."""
    print(f"Reading PDF: {file_path}")
    reader = PdfReader(file_path)
    print(f"PDF has {len(reader.pages)} pages.")

    full_text = "".join(page.extract_text() for page in reader.pages if page.extract_text())

    if not full_text.strip():
        print("No text could be extracted from the PDF.")
        return None

    print("\nPreview of text:")
    print(full_text[:200].strip() + "...")
    return full_text


def speak_text(engine, text):
    """Reads the given text aloud."""
    response = input("\nStart speaking? (y/n): ").lower()
    if response == 'y':
        print("Starting speech... (Press Ctrl+C to stop)")
        engine.say(text)
        engine.runAndWait()
        print("Finished speaking!")
    else:
        print("Speech cancelled.")


def save_text_to_audio(engine, text, output_file):
    """Saves the given text to an audio file."""
    print(f"Converting PDF to audio file: {output_file}")
    engine.save_to_file(text, output_file)
    engine.runAndWait()
    print(f"Audio saved successfully to: {output_file}")


def list_voices():
    """Lists all available TTS voices on the system."""
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    print("Available Text-to-Speech Voices:")
    print("-" * 50)
    for i, voice in enumerate(voices):
        languages = getattr(voice, 'languages', ['N/A'])
        gender = getattr(voice, 'gender', 'N/A')
        print(f"  {i}: {voice.name}")
        print(f"     - Gender: {gender}, Languages: {languages}")


def main():
    """Main function with command-line interface."""
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("PDF to Speech Reader")
        print("=" * 30)
        print("Usage:")
        print("  python pdf_reader.py <pdf_file>         - Read PDF aloud")
        print("  python pdf_reader.py <pdf_file> save    - Save to audio file")
        print("  python pdf_reader.py voices             - List available voices")
        return

    command = sys.argv[1]

    if command == "voices":
        list_voices()
        return

    file_path = command
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist!")
        return

    try:
        text = extract_text_from_pdf(file_path)
        if not text:
            return

        engine = initialize_engine()

        save_mode = len(sys.argv) > 2 and sys.argv[2].lower() == "save"

        if save_mode:
            output_name = os.path.splitext(os.path.basename(file_path))[0] + ".wav"
            save_text_to_audio(engine, text, output_name)
        else:
            speak_text(engine, text)

    except KeyboardInterrupt:
        print("\nOperation interrupted by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
