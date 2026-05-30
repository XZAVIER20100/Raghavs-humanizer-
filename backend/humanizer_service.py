import re
import time
import ollama

# Define the strict guidelines for the AI
ESSAY_GUIDELINES = """
You are an expert academic editor. Your task is to rephrase the provided text 
strictly adhering to these guidelines:
1. ELIMINATE FILLER: No conversational openers or hedging fillers.
2. FORMAL VOCABULARY: Use precise, academic language.
3. SENTENCE STRUCTURE: Clear subject-verb structure, varied sentence length.
4. TRANSITIONS: Logical connectors only.
5. FORMAL TONE: Consistent, analytical tone.
6. PRECISION: State facts accurately.
7. NO REPETITION: Do not repeat ideas or phrases.
Output ONLY the rephrased text.
"""

GRAMMAR_FIX_PROMPT = """
You are a professional copyeditor. Your ONLY task is to check the provided text 
for any grammatical, spelling, or punctuation errors. 
Fix the errors while keeping the original meaning and style exactly the same.
Output ONLY the corrected text.
"""

# Using the lightweight Qwen model
MODEL = "qwen2.5:0.5b"

def call_ai(text, prompt):
    """
    Calls the local Ollama model to process text based on a prompt.
    """
    response = ollama.chat(model=MODEL, messages=[
        {'role': 'system', 'content': prompt},
        {'role': 'user', 'content': text},
    ])
    return response['message']['content']

def recursive_humanize(text, iterations=3, intensity='standard'):
    """
    Pipeline: 
    1. Perform rephrasing loop using Ollama.
    2. Perform final grammar/punctuation check using Ollama.
    """
    current_text = text
    
    # 1. Rephrasing Loop
    print(f"Starting humanization loop ({iterations} iterations) with {MODEL}...")
    for i in range(1, iterations + 1):
        try:
            print(f"Iteration {i}/{iterations}...")
            current_text = call_ai(current_text, ESSAY_GUIDELINES)
            time.sleep(0.5) 
        except Exception as e:
            print(f"Error in iteration {i}: {e}")
            break

    # 2. Final Grammatical Polish
    print("Performing final grammar check...")
    try:
        current_text = call_ai(current_text, GRAMMAR_FIX_PROMPT)
    except Exception as e:
        print(f"Error in final grammar check: {e}")

    # Final cleanup
    cleaned = re.sub(r" +", " ", current_text).strip()
    
    return cleaned, f"Process complete (3 iterations + grammar check using {MODEL})."
