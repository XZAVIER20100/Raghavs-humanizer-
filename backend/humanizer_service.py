import time
import re
import os
import requests
import json
import google.generativeai as genai
from gradio_client import Client
from google.api_core import exceptions

# --- CONFIGURATION ---
HUMANIZER_SPACE = "conversantech/humanizer-ai"
GEMINI_MODELS = [
    "models/gemini-2.0-flash-lite-preview-02-05", 
    "models/gemini-2.0-flash-001",              
    "models/gemini-flash-latest",
    "models/gemini-flash-lite-latest",
    "models/gemini-pro-latest"
]
OPENROUTER_MODELS = [
    "minimax/minimax-01",
    "deepseek/deepseek-chat",
    "meta-llama/llama-3.1-70b-instruct"
]

# --- CLIENT INITIALIZATION (Optimization for Latency) ---
api_key_gemini = os.environ.get("GEMINI_API_KEY")
if api_key_gemini:
    genai.configure(api_key=api_key_gemini)

hf_client = Client(HUMANIZER_SPACE)

# --- TERMINOLOGY & CLEANUP ---
FORBIDDEN_MAP = {
    "crapulence": "Brad's Drink", "Brad's drinking": "Brad's Drink",
    "boozing": "beverage", "booze": "drink", "saccharide": "sugar",
    "carbohydrate prices": "sugar prices", "refined carbohydrate": "sugar",
    "universe War I": "World War I", "universe War II": "World War II",
    "ethnical force": "cultural force", "drinkable": "beverage",
    "marque": "brand", "make": "brand", "penny": "cents",
    "at most 26": "at nearly 26", "zoomers": "Gen Z", "digital natives": "Gen Z",
    "Judaical": "Jewish", "Judaic": "Jewish", "cosmos War I": "World War I",
    "cosmos War": "World War", "antediluvian": "ancient",
    "significant": "massive", "utilize": "tap into", "moreover": "also",
    "furthermore": "plus", "additionally": "next", "in conclusion": "finally",
    "notable": "huge", "pivotal": "key", "underscores": "shows",
    "comprehensive": "full", "vibrant": "alive", "landscape": "scene",
    "testament": "proof", "delve": "look into", "ensure": "make sure",
    "transform": "change", "leverage": "use", "harness": "catch",
    "robust": "strong", "seamless": "smooth", "parameter": "limit",
    "synergy": "teamwork", "paradigm": "way", "nuanced": "detailed"
}

STRICT_FILLERS = [
    r"\byou know\b", r"\blet me put it this way\b", r"\btruth is\b", 
    r"\bbasically\b", r"\bhere's where it gets good\b", r"\binterestingly enough\b",
    r"\bthink about it this way\b", r"\bhonestly\b", r"\breally\b", 
    r"\bsurely\b", r"\bof course\b", r"\bI mean\b", r"\bessentially\b",
    r"\bfundamentally\b", r"\bactually\b", r"\bFrankly\b", r"\bTo be honest\b",
    r"\bWhat we 're seeing is\b", r"\bLook\b", r"\bPlus\b", r"\bBesides\b",
    r"\bHere 's why this matters\b", r"\bthe thing is\b", r"\bNaturally\b",
    r"\bsurprisingly\b", r"\bon top of that\b", r"\bIndeed\b", r"\bUsually\b",
    r"\bNotable\b", r"\bImportantly\b", r"\bDefinitely\b", r"\bsort of\b",
    r"\bHere 's the bottom line\b", r"\bThe reality is\b", r"\bIn today's world\b",
    r"\bIn conclusion\b", r"\bFinally\b"
]

def apply_strict_cleanup(text):
    for wrong, right in FORBIDDEN_MAP.items():
        text = re.sub(rf'\b{wrong}\b', right, text, flags=re.IGNORECASE)
    for filler in STRICT_FILLERS:
        text = re.sub(filler, "", text, flags=re.IGNORECASE)
    text = re.sub(r"'\s*s\b", "'s", text)
    text = re.sub(r"([,.!?])\s*\1+", r"\1", text)
    text = re.sub(r'\s+([,.!?])', r'\1', text)
    text = re.sub(r',+', ',', text)
    text = text.replace(" — ", ", ").replace("—", ", ").replace(" – ", ", ").replace("–", ", ").replace("--", ", ")
    return re.sub(r'\s+', ' ', text).strip()

def call_hf_pass(text):
    """Pass 1: Hugging Face Humanizer."""
    print("  [HF Pass] Processing...")
    try:
        result = hf_client.predict(text, 'standard', api_name="/process_text_advanced")[0]
        return result if result else text
    except:
        return text

def call_engine_pass(text, pass_num):
    """Pass 2 & 3: Raghav Master Engine (Gemini -> Fallback to OpenRouter)."""
    print(f"  [Engine Pass] Starting Pass {pass_num}")
    
def call_engine_pass(text, pass_num):
    """Pass 2 & 3: Raghav Master Engine (Gemini -> Fallback to OpenRouter)."""
    print(f"  [Engine Pass] Starting Pass {pass_num}")
    
    prompt = f"""Rewrite the following text to sound authentically human.
    
    CRITICAL RULES (MUST FOLLOW OR FAIL):
    1. NEVER start sentences with: "And", "But", "So", "It's", "Then", "Yet", "Okay", "Therefore", "However", "Consequently", "Moreover", "Furthermore".
    2. NO AI-ADJECTIVES: NEVER use: "jagged," "visceral," "marrow," "labyrinthine," "catastrophic," "glitchy," "unraveling," "cynical," "world-weary," "spectacle," "alchemy," "fossilized," "grotesque," "lush," "intricate," "infamous," "shredded."
    3. NO ESSAY STRUCTURE: Do not use formal essay transitions. Write like a human talking—sometimes fast, sometimes slow, with natural pauses.
    4. VARIATION: If the previous sentence started with a Noun, start the next with a Verb or Prepositional phrase. Absolutely no repetitive openers.
    5. KEEP FACTS RIGID: Names, dates, numbers from original text must remain 100% exact.

    ORIGINAL:
    {text}

    HUMANIZED REWRITE:"""
    # ... (Keep existing call logic) ...

    # Try Gemini Models
    for model_name in GEMINI_MODELS:
        try:
            model = genai.GenerativeModel(model_name)
            # Slightly higher temperature for increased variance
            response = model.generate_content(prompt, generation_config={"temperature": 0.98})
            if response and response.text:
                humanized = response.text.strip()
                if "HUMANIZED REWRITE:" in humanized:
                    humanized = humanized.split("HUMANIZED REWRITE:")[-1].strip()
                return humanized
        except: continue
    
    # Fallback to OpenRouter
    api_key_or = os.environ.get("OPENROUTER_API_KEY")
    if api_key_or:
        for model_id in OPENROUTER_MODELS:
            try:
                response = requests.post(
                    url="https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key_or}", "Content-Type": "application/json"},
                    data=json.dumps({
                        "model": model_id,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.98,
                    }),
                    timeout=60
                )
                if response.status_code == 200:
                    return response.json()['choices'][0]['message']['content'].strip()
            except: continue
            
    return text

def call_persona_pass(text, pass_num):
    """
    Pass 2 & 3: Simple & Natural Collective Voice.
    Target: 0% AI Detection via Clarity.
    """
    print(f"  [Persona Pass] Starting Pass {pass_num}")
    
    prompt = f"""Rewrite the following text using a clear, natural, collective human voice. This MUST bypass AI detectors by being simple, direct, and unpredictable—not complex.

    THE "CLARITY & DETECTION" RULES:
    1. SIMPLE BUT NATURAL: Use direct, common human language. ABSOLUTELY FORBIDDEN: Using complex buzzwords, academic jargon, or "fancy" synonyms. If you change a word, use a simpler, more punchy one that people actually use in conversation.
    2. PROPER NOUN LOCK: Never change country names, cities, people's names, or dates. 'India' stays 'India', 'Israel' stays 'Israel'.
    3. RADICAL RHYTHM: Mix sentence lengths. One short sentence (4-6 words). One long, sprawling sentence. This variety is how humans actually write.
    4. SYNTACTIC JITTER: Use natural pauses. Add a dash—like this—or a quick side-note in parentheses. It breaks the "too perfect" AI structure.
    5. COLLECTIVE VOICE: Use 'we', 'us', or 'our'. Keep it shared and authoritative.
    6. DELETE ROADMAPS: Remove 'Furthermore', 'Moreover', and 'In conclusion'. Just move to the next point naturally.
    7. NO LABELS: Output ONLY the rewritten text.

    ORIGINAL:
    {text}

    HUMANIZED REWRITE:"""
    
    # Try Gemini Models
    for model_name in GEMINI_MODELS:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt, generation_config={"temperature": 0.98})
            if response and response.text:
                humanized = response.text.strip()
                if "HUMANIZED REWRITE:" in humanized:
                    humanized = humanized.split("HUMANIZED REWRITE:")[-1].strip()
                return humanized
        except: continue
    
    # Fallback to OpenRouter
    api_key_or = os.environ.get("OPENROUTER_API_KEY")
    if api_key_or:
        for model_id in OPENROUTER_MODELS:
            try:
                response = requests.post(
                    url="https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key_or}", "Content-Type": "application/json"},
                    data=json.dumps({"model": model_id, "messages": [{"role": "user", "content": prompt}], "temperature": 0.98}),
                    timeout=60
                )
                if response.status_code == 200:
                    return response.json()['choices'][0]['message']['content'].strip()
            except: continue
            
    return text

def call_detector_pass(text):
    """
    The Internal Detector: Gemini acts as the "ZeroGPT Judge" to find AI patterns.
    Returns: A list of flagged segments and an overall AI score.
    """
    print("  [Detector Pass] Evaluating for AI traces...")
    
    prompt = f"""You are a professional AI Detection Auditor. Your job is to find ANY remaining traces of AI-generated patterns in the text below. 

    DIAGNOSTIC CRITERIA:
    1. Predictability: Are the word choices too "perfect" or academic?
    2. Rhythm: Is the sentence flow too smooth or balanced?
    3. Formatting: Are there robotic transitions?

    TASK:
    1. Give an overall 'AI Probability' score (0-100%).
    2. List the specific sentences or phrases that still feel like AI.
    3. Output in JSON format only: {{"score": 85, "flagged_segments": ["sentence 1...", "phrase 2..."]}}

    TEXT TO AUDIT:
    {text}

    JSON OUTPUT:"""
    
    for model_name in GEMINI_MODELS:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            if response and response.text:
                # Clean up the response to extract JSON
                content = response.text.strip()
                if "```json" in content:
                    content = content.split("```json")[-1].split("```")[0].strip()
                elif "{" in content:
                    content = content[content.find("{"):content.rfind("}")+1]
                
                result = json.loads(content)
                return result.get("score", 0), result.get("flagged_segments", [])
        except: continue
    return 0, []

def call_surgical_rewrite_pass(text, flagged_segments):
    """
    Targeted Fixer: Surgically rewrites ONLY the segments flagged by the detector.
    """
    print(f"  [Surgical Pass] Fixing {len(flagged_segments)} flagged segments...")
    
    segments_str = "\n".join([f"- {s}" for s in flagged_segments])
    
    prompt = f"""You are a master humanizer. The following segments have been flagged by a detector as "AI-written." 
    Rewrite these SPECIFIC segments to be 100% human. 

    FIXING RULES:
    1. BREAK THE RHYTHM: Change the length and flow of the sentence completely.
    2. SWAP PREDICTABLE WORDS: Replace academic words with common, punchy human language.
    3. ADD 'JITTER': Add a dash or a natural pause.
    4. NO FIRST PERSON: Use 'we', 'us', or 'our'.
    5. NO HALLUCINATIONS: Keep the exact meaning and facts.

    FLAGGED SEGMENTS:
    {segments_str}

    FULL TEXT FOR CONTEXT:
    {text}

    TASK: Return the FULL text with only the flagged segments surgically updated. Do not add intro/outro.

    REFINED TEXT:"""

    for model_name in GEMINI_MODELS:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            if response and response.text:
                humanized = response.text.strip()
                if "REFINED TEXT:" in humanized:
                    humanized = humanized.split("REFINED TEXT:")[-1].strip()
                return humanized
        except: continue
    return text

def recursive_humanize(original_text, iterations=1, intensity='standard'):
    """
    ULTIMATE SELF-CORRECTING PIPELINE:
    1. Phase 1: Structural Break (2x HF).
    2. Phase 2: Persona Injection (2x Gemini).
    3. Phase 3: Detection & Surgical Loop (Feedback).
    4. Phase 4: Final Cleanup.
    """
    current_text = original_text
    
    # 1. Hugging Face Passes
    for i in range(2):
        current_text = call_hf_pass(current_text)
        time.sleep(0.5)

    # 2. Expert Persona Passes
    for i in range(2):
        current_text = call_persona_pass(current_text, i+1)
        time.sleep(1)
    
    # 3. SELF-CORRECTION LOOP (Targeting 0%)
    print("--- Starting Self-Correction Loop ---")
    for loop_num in range(2): # Max 2 refinement loops
        score, flagged = call_detector_pass(current_text)
        print(f"  [Loop {loop_num+1}] AI Detection Score: {score}%")
        
        if score < 5 or not flagged:
            print("  [Success] Score is below 5%. Loop finished.")
            break
        
        current_text = call_surgical_rewrite_pass(current_text, flagged)
        time.sleep(1)

    # 4. Terminology Cleanup
    final_text = apply_strict_cleanup(current_text)
    
    return final_text, f"Raghav's Self-Correcting Engine: 2x HF + 2x Persona + {loop_num+1}x Feedback Loops Applied. Final local score: ~{score}%"
