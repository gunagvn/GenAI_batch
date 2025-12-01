"""
Interactive RPG-style Storyteller
- Uses Hugging Face text-generation pipeline (google/gemma-2b)
- Persists state to story_state.json
- Create characters, start/continue story, make choices
"""

import json
import os
from datetime import datetime
from transformers import pipeline

STATE_FILE = "story_state.json"
MODEL_NAME = "google/gemma-2b"   # open model; no auth required

# -------------------------
# Load generation model
# -------------------------
print("Loading text generation model... (this may take a moment)")
generator = pipeline(
    "text-generation",
    model=MODEL_NAME,
    tokenizer=MODEL_NAME,
    max_new_tokens=300,
    temperature=0.8,
    do_sample=True,
    top_p=0.9
)

# -------------------------
# State helpers
# -------------------------
def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"characters": {}, "history": []}

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

state = load_state()

# -------------------------
# Character helpers
# -------------------------
def create_character(name, role, traits_text):
    """
    name: string
    role: short role e.g., 'hero', 'villain', 'companion'
    traits_text: short comma separated traits/descriptions
    """
    char = {
        "name": name,
        "role": role,
        "traits": traits_text,
        "created_at": datetime.utcnow().isoformat()
    }
    state["characters"][name.lower()] = char
    save_state(state)
    print(f"✅ Character '{name}' created.")

def edit_character(name, role=None, traits_text=None):
    key = name.lower()
    if key not in state["characters"]:
        print("No such character.")
        return
    if role:
        state["characters"][key]["role"] = role
    if traits_text:
        state["characters"][key]["traits"] = traits_text
    save_state(state)
    print(f"✅ Character '{name}' updated.")

def list_characters():
    if not state["characters"]:
        print("No characters yet.")
        return
    print("\nCharacters:")
    for c in state["characters"].values():
        print(f"- {c['name']} ({c['role']}): {c['traits']}")

# -------------------------
# Story helpers
# -------------------------
def create_story_seed(title, synopsis, protagonist_name):
    seed = {
        "title": title,
        "synopsis": synopsis,
        "created_at": datetime.utcnow().isoformat(),
        "chapter": 1,
        "protagonist": protagonist_name,
    }
    # initial story entry
    entry = {
        "chapter": 1,
        "timestamp": datetime.utcnow().isoformat(),
        "prompt_type": "seed",
        "prompt": synopsis,
        "text": f"Chapter 1 — {title}\n\n{synopsis}"
    }
    state["history"].append(entry)
    save_state(state)
    print(f"✅ Story '{title}' initialized. (Chapter 1)")

def get_recent_context(max_chars=2500):
    """
    Build a context window from recent history and character sheets.
    """
    parts = []
    # include character brief
    if state["characters"]:
        parts.append("CHARACTERS:")
        for c in state["characters"].values():
            parts.append(f"{c['name']} ({c['role']}): {c['traits']}")
    parts.append("\nRECENT STORY:")
    # add up to some length of recent story entries (most recent first)
    for entry in state["history"][-6:]:
        parts.append(f"CH{entry['chapter']} @ {entry['timestamp']}: {entry['text']}")
    context = "\n\n".join(parts)
    # trim if too long
    if len(context) > max_chars:
        context = context[-max_chars:]
    return context

def generate_story_segment(user_action, protagonist_hint=None, max_tokens=300):
    """
    user_action: the player's input (choice or free text)
    protagonist_hint: optional name to emphasize protagonist perspective
    """
    context = get_recent_context()
    prompt = f"""
You are a creative fantasy storyteller / dungeon master. Continue the story using the context and the player's action.

CONTEXT:
{context}

PLAYER ACTION:
{user_action}

GUIDELINES:
- Continue the narrative in a vivid, descriptive way (3-6 paragraphs).
- Keep characters consistent with their traits.
- Reflect consequences of the player's action.
- End with a clear set of 2-4 choices the player can pick from next (label them 1., 2., 3., ...).
- Keep the output as plain text (no JSON).

If protagonist is specified: emphasize their viewpoint: {protagonist_hint}

Generate the story continuation now.
"""
    # call model
    gen = generator(prompt, max_new_tokens=max_tokens, temperature=0.8)[0]["generated_text"]
    # sometimes the model repeats the prompt; remove prompt portion if present
    if prompt.strip() in gen:
        # naive trimming: try to keep only the generation after the prompt
        gen = gen.split(prompt)[-1]
    return gen.strip()

def add_history_entry(chapter, prompt_type, prompt_text, generated_text):
    entry = {
        "chapter": chapter,
        "timestamp": datetime.utcnow().isoformat(),
        "prompt_type": prompt_type,
        "prompt": prompt_text,
        "text": generated_text
    }
    state["history"].append(entry)
    save_state(state)

# -------------------------
# Interactive loop
# -------------------------
def interactive_loop():
    print("\n=== Interactive Storyteller (RPG style) ===")
    print("Type 'help' for commands. Type 'exit' to quit.\n")

    while True:
        cmd = input(">> ").strip()
        if not cmd:
            continue

        if cmd.lower() in ("exit", "quit"):
            print("Saving and exiting. Goodbye!")
            save_state(state)
            break

        if cmd.lower() == "help":
            print("""
Commands:
- create_char   -> create a new character
- edit_char     -> edit an existing character
- list_chars    -> show characters
- start_story   -> initialize a new story seed (title + synopsis)
- continue      -> continue story by choosing an action
- show_history  -> print recent story history
- exit / quit   -> save & exit
""")
            continue

        if cmd.lower() == "create_char":
            name = input("Name: ").strip()
            role = input("Role (hero/villain/companion/...): ").strip()
            traits = input("Traits (comma separated / short description): ").strip()
            create_character(name, role, traits)
            continue

        if cmd.lower() == "edit_char":
            name = input("Name to edit: ").strip()
            role = input("New role (enter to skip): ").strip()
            traits = input("New traits (enter to skip): ").strip()
            edit_character(name, role or None, traits or None)
            continue

        if cmd.lower() == "list_chars":
            list_characters()
            continue

        if cmd.lower() == "start_story":
            title = input("Story title: ").strip()
            synopsis = input("Synopsis / seed (one paragraph): ").strip()
            protagonist = input("Protagonist name (must exist in characters): ").strip()
            if protagonist.lower() not in state["characters"]:
                print("Protagonist not found in characters. Create them first.")
                continue
            # reset history and start fresh
            state["history"] = []
            create_story_seed(title, synopsis, protagonist)
            print("Story started.")
            continue

        if cmd.lower() == "show_history":
            print("\n=== STORY HISTORY (most recent last) ===")
            for i, entry in enumerate(state["history"], start=1):
                print(f"\n[{i}] CH{entry['chapter']} @ {entry['timestamp']}")
                print(entry["text"])
            continue

        if cmd.lower() == "continue":
            if not state["history"]:
                print("No story found. Use start_story to create a seed.")
                continue
            protagonist = state["history"][-1].get("protagonist") or state["history"][-1].get("protagonist", None)
            # show last segment
            print("\nMost recent passage:")
            print(state["history"][-1]["text"] if state["history"] else "(none)")
            action = input("\nYour action (free text, e.g. 'draw sword and charge' or menu choice): ").strip()
            # generate next
            print("\nGenerating continuation... (this may take a few seconds)")
            gen = generate_story_segment(action, protagonist_hint=state["history"][-1].get("protagonist"))
            # determine new chapter number
            new_chapter = state["history"][-1]["chapter"] + 1 if state["history"] else 1
            add_history_entry(new_chapter, "player_action", action, gen)
            print("\n=== NEW PASSAGE ===\n")
            print(gen)
            continue

        print("Unknown command. Type 'help' for commands.")

# -------------------------
# Start
# -------------------------
if __name__ == "__main__":
    print("Loaded state. Characters:", len(state["characters"]), "History entries:", len(state["history"]))
    interactive_loop()
