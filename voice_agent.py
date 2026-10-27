import datetime
import speech_recognition as sr
import pyttsx3
import json
import requests
import ollama

# Initialize Text-to-Speech engine
engine = pyttsx3.init()

def speak(text):
    """Converts text response to speech."""
    print(f"\n[Agent]: {text}")
    engine.say(text)
    engine.runAndWait()

def listen_command():
    """Captures microphone input and converts it to text via Google STT."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n🎙️ Listening for your command...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
            text = recognizer.recognize_google(audio)
            print(f"👤 You said: '{text}'")
            return text
        except sr.WaitTimeoutError:
            print("Listening timed out. No speech detected.")
            return ""
        except sr.UnknownValueError:
            print("Could not understand audio.")
            return ""
        except sr.RequestError as e:
            print(f"Speech recognition service error: {e}")
            return ""

# --- Define Agent Tools / External APIs ---

def tool_get_time():
    """Tool to check current system time."""
    current_time = datetime.datetime.now().strftime("%I:%M %p")
    return f"The current time is {current_time}."

def tool_create_note(command_text):
    """Tool to create a local text file note from voice input."""
    filename = "voice_notes.txt"
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now()}] {command_text}\n")
    return f"I've successfully saved that note to {filename}."

def tool_get_weather(city_name):
    """External API Tool: Fetch weather for a given city."""
    try:
        # Example using wttr.in free public API (No key required for testing)
        url = f"https://wttr.in/{city_name}?format=3"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return f"The weather report: {response.text.strip()}"
        return "Could not fetch weather data right now."
    except Exception as e:
        return f"API error: {str(e)}"

# Map tool names to actual Python functions
AVAILABLE_TOOLS = {
    "tool_get_time": tool_get_time,
    "tool_create_note": tool_create_note,
    "tool_get_weather": tool_get_weather
}

# Define Tool Schemas for Ollama / LLM
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "tool_get_time",
            "description": "Get the current local system time.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tool_create_note",
            "description": "Save a note or reminder text into a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command_text": {"type": "string", "description": "The exact note content to remember."}
                },
                "required": ["command_text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tool_get_weather",
            "description": "Get current weather conditions for any city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city_name": {"type": "string", "description": "Name of the city, e.g. Delhi, Mumbai"}
                },
                "required": ["city_name"]
            }
        }
    }
]

# --- Agent Core Loop with LLM Intelligence ---

def run_voice_agent():
    speak("Agentic voice assistant initialized. How can I help you?")
    
    # Keep conversation history for context
    messages = [{'role': 'system', 'content': 'You are a helpful voice assistant with access to tools. Use tools when needed.'}]
    
    while True:
        user_prompt = listen_command()
        
        if not user_prompt:
            continue
            
        # Exit condition
        if any(word in user_prompt.lower() for word in ["exit loop", "shut down", "stop", "goodbye"]):
            speak("Shutting down voice agent. Goodbye!")
            break

        messages.append({'role': 'user', 'content': user_prompt})

        try:
            # 1. Send prompt & tool definitions to local Ollama model (e.g., llama3)
            response = ollama.chat(
                model='llama3', # Ya jo model aap use kar rahe hain
                messages=messages,
                tools=TOOLS_SCHEMA,
            )
            
            # 2. Check if LLM decided to call a tool/API
            if response.get('message', {}).get('tool_calls'):
                for tool_call in response['message']['tool_calls']:
                    func_name = tool_call['function']['name']
                    func_args = tool_call['function']['arguments']
                    
                    print(lambda: f"\n[Agent Tool Trigger]: Calling {func_name} with {func_args}")
                    
                    # Execute corresponding Python function
                    if func_name in AVAILABLE_TOOLS:
                        tool_output = AVAILABLE_TOOLS[func_name](**func_args)
                        
                        # Feed result back to LLM for final conversational response
                        messages.append(response['message'])
                        messages.append({'role': 'tool', 'content': str(tool_output)})
                        
                        final_res = ollama.chat(model='llama3', messages=messages)
                        final_reply = final_res['message']['content']
                        
                        speak(final_reply)
                        messages.append({'role': 'assistant', 'content': final_reply})
            else:
                # Normal text response without tool
                reply = response['message']['content']
                speak(reply)
                messages.append({'role': 'assistant', 'content': reply})

        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            print(error_msg)
            speak("Sorry, I encountered an issue processing that.")

if __name__ == "__main__":
    run_voice_agent()