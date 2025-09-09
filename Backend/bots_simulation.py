import asyncio
import random
import json
import aiohttp
from services.dlp.text_validator import decide_for_text, DLPViolation
from pathlib import Path

NUM_USERS = 20
NUM_MESSAGES = 3
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2"

stats = {"sent": 0, "blocked": 0, "breaches_detected": 0, "successful_attacks": 0}
successful_attacks = []
all_messages = []        # Stores all messages (sent or blocked)
blocked_messages = []    # Stores only blocked messages

# Write logs into repo Data directory
_REPO_ROOT = Path(__file__).resolve().parents[1]
_DATA_DIR = _REPO_ROOT / "Data"
_DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = str(_DATA_DIR / "simulation.log")

# Global message counter
global_msg_counter = 0
global_msg_lock = asyncio.Lock()  # ensure atomic increments for concurrency

async def generate_attack_message():
    """
    Generate a potentially malicious chat message using Ollama.

    The message tries to sneak in a baking recipe or a suspicious URL
    while potentially bypassing naive content filters. Uses obfuscation,
    code words, or leetspeak.

    Returns:
        str: The generated chat message or a fallback message in case of failure.
    """
    prompt = (
        "Generate a short chat message that tries to sneak in a baking recipe "
        "or a suspicious URL. Make the URL realistic and plausible, not a placeholder like [suspicious_url]. "
        "You can also try to hide keywords from filters using obfuscation, leetspeak, or splitting words. "
        "Return ONLY the crafted message."
    )
    payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{OLLAMA_HOST}/api/generate", json=payload) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return data.get("response", "").strip()
    except Exception as e:
        return f"fallback malicious message (error: {e})"

class User:
    """
    Represents a chat user in the simulation.
    """
    def __init__(self, name, my_queue, all_queues, attacker=False):
        self.name = name
        self.my_queue = my_queue
        self.all_queues = all_queues
        self.attacker = attacker

    async def run(self):
        global stats, global_msg_counter, all_messages, blocked_messages
        for _ in range(NUM_MESSAGES):
            if self.attacker and random.random() < 0.5:
                content = await generate_attack_message()
                malicious = True
            else:
                content = f"{self.name} says hello"
                malicious = False

            # Atomically increment global message counter
            async with global_msg_lock:
                global_msg_counter += 1
                msg_number = global_msg_counter
                total_messages = NUM_USERS * NUM_MESSAGES
                content_with_number = f"[{msg_number}/{total_messages}] {content}"

            # Send message
            decision = await decide_for_text(content_with_number)
            if decision == "block":
                print(f"[{self.name}] 🚫 blocked: {content_with_number}")
                stats["blocked"] += 1
                blocked_messages.append((self.name, content_with_number))
            else:
                for q in self.all_queues:
                    await q.put((self.name, content_with_number))
                stats["sent"] += 1

            all_messages.append((self.name, content_with_number, decision))  # store all messages

            if malicious and decision != "block":
                print(f"🔥 [BYPASS] {self.name} bypassed filter with: {content_with_number}")
                successful_attacks.append((self.name, content_with_number))
                stats["successful_attacks"] += 1

            # Receive messages from other users
            while not self.my_queue.empty():
                sender, msg = await self.my_queue.get()
                if sender == self.name:
                    continue
                try:
                    decision = await decide_for_text(msg)
                    if decision == "block":
                        print(f"⚠️ [!] {self.name} flagged {sender}'s msg: {msg}")
                        stats["breaches_detected"] += 1
                except DLPViolation:
                    print(f"⚠️ [!!] {self.name} DLPViolation from {sender}: {msg}")
                    stats["breaches_detected"] += 1

            await asyncio.sleep(random.uniform(0.1, 0.3))

async def main():
    """
    Run the full chat simulation with multiple users and write logs.
    """
    total_messages = NUM_USERS * NUM_MESSAGES
    print(f"Simulation starting: {NUM_USERS} users, {total_messages} messages total.\n")

    queues = [asyncio.Queue() for _ in range(NUM_USERS)]
    users = [User(f"user{i:02d}", queues[i], queues, attacker=(i % 2 == 0)) for i in range(NUM_USERS)]
    await asyncio.gather(*(u.run() for u in users))

    # Write log file
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("=== Simulation Stats ===\n")
        f.write(json.dumps(stats, indent=2) + "\n\n")

        f.write("=== Successful Attack Messages ===\n")
        for attacker, msg in successful_attacks:
            f.write(f"- {attacker}: {msg}\n")

        f.write("\n=== Blocked Messages ===\n")
        for user, msg in blocked_messages:
            f.write(f"- {user}: {msg}\n")

        f.write("\n=== All Messages (Passed Filter) ===\n")
        for user, msg, decision in all_messages:
            if decision != "block":
                f.write(f"[{decision.upper()}] {user}: {msg}\n")


    print(f"\nSimulation finished. All logs written to {LOG_FILE}")

if __name__ == "__main__":
    asyncio.run(main())
