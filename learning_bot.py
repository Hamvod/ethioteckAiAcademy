import os
from typing import Dict, List

from dotenv import load_dotenv
from google import genai
from google.genai import types
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackContext, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_NAME = os.getenv("BOT_NAME", "Hamvod")
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini").lower()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("AI_MODEL", "gemini-3.8-flash")

LANGUAGE_NAMES = {"en": "English", "am": "Amharic"}
AI_SYSTEM_PROMPT = (
    "You are Hamvod, a patient learning tutor. Give accurate, beginner-friendly answers "
    "about the courses offered by the bot. Keep answers concise and safe."
)

WELCOME_TEXT = """👋 Welcome to Hamvod!
Learn Web Development, Cyber Security, Networking, Viral Video Content, and Robotics with Arduino — with an AI tutor to answer your questions anytime.
Choose a language to begin."""

COURSES: Dict[str, Dict[str, List[Dict[str, str]]]] = {
    "web": {
        "title": "Web Development",
        "units": [
            {
                "title": "How Computers Actually Work",
                "body": "- **Bit** — smallest unit of data: `0` or `1` (like a light switch, off/on).\n- **Byte** — 8 bits grouped together (e.g. `01001000`); one byte usually represents one character.\n- **Binary** — the number system (only 0s and 1s) that all computer data is built from — code, images, video, everything.\n- **CPU** — executes binary instructions billions of times per second.\n- **RAM vs. Storage** — RAM is short-term working memory (cleared when power is off); storage (SSD/HDD) keeps data permanently.\n- **Client vs. Server** — your browser (client) requests a webpage; a remote computer (server) sends back the files that build that page.\n\n**Why it matters:** every website you'll ever build is, underneath, just text files turned into binary, sent across a network, and rendered by a browser. Understanding this layer makes debugging and performance much less mysterious."
            },
            {
                "title": "How the Web Works",
                "body": "- **URL** — the address of a resource (e.g. `https://example.com/page`)\n- **DNS** — the \"phonebook\" of the internet, turning domain names into IP addresses\n- **HTTP/HTTPS** — the protocol browsers and servers use to talk; HTTPS adds encryption\n- **Request/response cycle:** browser sends a request → server processes it → server sends back HTML/CSS/JS → browser renders the page\n- **Frontend vs. Backend:**\n\n- *Frontend* = what runs in the user's browser (HTML, CSS, JavaScript) — what they see and click\n- *Backend* = what runs on the server (handles data, logic, databases, security)"
            },
            {
                "title": "HTML: Structure",
                "body": "HTML (HyperText Markup Language) builds the skeleton of every page using **tags**.\n\n```html\n<!DOCTYPE html>\n<html>\n  <head>\n    <title>My First Page</title>\n  </head>\n  <body>\n    <h1>Hello, Hamvod!</h1>\n    <p>This is my first web page.</p>\n    <a href=\"https://example.com\">Click here</a>\n  </body>\n</html>\n```\n\nKey tags to master: `<h1>`–`<h6>`, `<p>`, `<a>`, `<img>`, `<div>`, `<span>`, `<ul>`/`<li>`, `<form>`, `<input>`, `<button>`.\n\n**Mini project:** build a simple personal profile page with a heading, a photo, a paragraph about yourself, and a link to one social account."
            },
            {
                "title": "CSS: Styling",
                "body": "CSS (Cascading Style Sheets) controls color, layout, spacing, and fonts.\n\n```css\nbody {\n  font-family: Arial, sans-serif;\n  background-color: #f4f4f4;\n}\nh1 {\n  color: #2563eb;\n  text-align: center;\n}\n```\n\nCore concepts: **selectors**, the **box model** (margin/border/padding/content), **Flexbox** and **Grid** for layout, **responsive design** (`@media` queries so a site works on phones and desktops both).\n\n**Mini project:** style Unit 3's profile page — center it, add colors, make it look good on both phone and desktop screen sizes."
            },
            {
                "title": "JavaScript: Behavior",
                "body": "JavaScript makes a page interactive — it runs *inside* the browser.\n\n```js\nconst button = document.querySelector(\"button\");\nbutton.addEventListener(\"click\", () => {\n  alert(\"You clicked the button!\");\n});\n```\n\nCore concepts: **variables** (`let`, `const`), **functions**, **if/else logic**, **loops**, the **DOM** (how JS reads/changes the page), and **events** (click, submit, input).\n\n**Mini project:** add a button to the profile page that changes its background color when clicked."
            },
            {
                "title": "Git & GitHub",
                "body": "Git tracks changes to your code over time; GitHub hosts your code online and lets you share it.\n\n```bash\ngit init\ngit add .\ngit commit -m \"First version of my site\"\ngit remote add origin <your-repo-url>\ngit push -u origin main\n```\n\nWhy it matters professionally: every real dev job expects comfort with Git — it's how teams collaborate without overwriting each other's work, and how you build a public portfolio."
            },
            {
                "title": "Backend Basics & Databases",
                "body": "- **Backend language options:** Node.js (JavaScript), Python (Django/Flask), PHP, etc.\n- **What a backend does:** handles logins, saves/reads data, processes payments, talks to other services\n- **Database basics:**\n\n- *SQL* (structured, table-based — e.g. PostgreSQL, MySQL)\n- *NoSQL* (flexible, document-based — e.g. MongoDB)\n- **API** — the way a frontend asks a backend for data (commonly JSON over HTTP)\n\n**Mini project (conceptual):** design the database table you'd need to store users for the profile-page project (fields like `name`, `email`, `password_hash`, `bio`)."
            },
            {
                "title": "Putting a Site Online",
                "body": "1. Buy or get a free domain (or use a free subdomain for practice)\n2. Choose hosting: static sites → Netlify/Vercel/GitHub Pages (free, beginner-friendly); full apps with a backend → Render, Railway, or a VPS\n3. Connect your GitHub repo so it deploys automatically on every `git push`\n4. Add HTTPS (most modern hosts do this automatically)\n\n**Mini project:** deploy the profile page from Units 3–5 live on the internet with a real URL you can share."
            },
            {
                "title": "Becoming Job-Ready",
                "body": "- **Build a portfolio:** 3–5 real small projects beat 1 huge unfinished one\n- **Learn to read error messages** — this is 50% of real development work\n- **Practice problem-solving** — sites like freeCodeCamp, exercises, small daily challenges\n- **Specialize eventually:** Frontend (React/Vue), Backend (Node/Django), or Full-Stack\n- **Where to apply:** freelance platforms, local companies, remote jobs, or build your own product (you already have app ideas — this is exactly the skill set that lets you build them yourself)"
            }
        ]
    },
    "cyber": {
        "title": "Cyber Security",
        "units": [
            {
                "title": "What Is Cyber Security?",
                "body": "Cyber security is the practice of protecting computers, networks, and data from unauthorized access, damage, or theft.\n\n**The CIA Triad** (the 3 goals of every security system):\n\n- **Confidentiality** — only authorized people can see the data (e.g. encryption, passwords)\n- **Integrity** — data isn't tampered with or corrupted (e.g. checksums, digital signatures)\n- **Availability** — systems stay up and usable (e.g. backups, protection from attacks that take systems offline)\n\n**Mini exercise:** for your Telegram channel, name one thing you do for each of the 3 (e.g. confidentiality = only you have the bot token; availability = the server stays running)."
            },
            {
                "title": "The OSI Model (7 Layers)",
                "body": "Layer\nName\nRole\nExample\n\n7\nApplication\nUser-facing software\nBrowser, Telegram\n\n6\nPresentation\nFormats/encrypts\nSSL/TLS, HTTPS\n\n5\nSession\nManages connections\nStaying logged in\n\n4\nTransport\nReliable delivery\nTCP, UDP\n\n3\nNetwork\nRouting/addressing\nIP, routers\n\n2\nData Link\nLocal delivery\nMAC address, switches\n\n1\nPhysical\nThe actual signal\nCable, WiFi radio waves\n\nData goes **down** the stack on the sender's device, travels the network, then **up** the stack on the receiver's device. Most real attacks target specific layers — e.g. phishing targets Layer 7 (the human/app), while sniffing attacks target Layer 1–2 (the raw signal)."
            },
            {
                "title": "How Attacks Work (Awareness Level)",
                "body": "Understanding attacker methods is how defenders learn to stop them. This course teaches the *concepts*, not working attack tools:\n\n- **Phishing** — fake emails/messages/login pages designed to trick you into giving up credentials. *Defense:* always check the actual URL before entering a password; never trust urgency.\n- **Social engineering** — manipulating a person (not a machine) into breaking security rules, e.g. pretending to be IT support. *Defense:* verify identity through a separate channel before acting.\n- **Credential stuffing / weak passwords** — attackers try leaked username+password lists against many sites, because people reuse passwords. *Defense:* unique password per site + a password manager.\n- **Malware** — malicious software that gets installed, often through fake downloads or email attachments. *Defense:* don't run unknown executables; keep software updated.\n- **Unpatched software** — attackers exploit publicly known bugs in old software versions. *Defense:* enable automatic updates.\n\n> This course deliberately does not include working exploit code, password-cracking tools, or step-by-step attack instructions. Real, legal security testing only happens with written authorization from the system's owner."
            },
            {
                "title": "Passwords & Authentication",
                "body": "- **Strong passwords:** length matters more than complexity — a 16-character passphrase (`correct-horse-battery-staple`) beats `P@ssw0rd1`.\n- **Never reuse passwords** across sites — one leaked site compromises all of them.\n- **Password managers** (Bitwarden, 1Password) generate and store unique passwords so you don't have to remember them.\n- **2-Factor Authentication (2FA)** — a second proof of identity (a code from an app, not SMS when avoidable) so a stolen password alone isn't enough to break in.\n\n**Mini exercise:** check which of your own accounts don't have 2FA enabled yet, and turn it on for the most important 3 (email, bank, Telegram)."
            },
            {
                "title": "Network Security Basics",
                "body": "- **Firewall** — a filter that blocks unwanted traffic in/out of a network or device.\n- **VPN** — encrypts your traffic and hides your real IP address; important on public WiFi.\n- **Encryption, simply explained** — scrambling data with a key so only someone with the right key can read it; HTTPS (the padlock icon) means your connection to a site is encrypted.\n- **Public WiFi risk** — on an open network, other people on the same WiFi can potentially intercept unencrypted traffic; a VPN or sticking to HTTPS sites reduces this risk."
            },
            {
                "title": "Safe Browsing & Social Media Safety",
                "body": "Especially relevant since you also run a Telegram channel and teach viral content creation — creators and admins are common targets:\n\n- Check a link's actual destination before clicking (hover on desktop, long-press on mobile)\n- Never share your bot token, API keys, or 2FA codes with anyone — treat them like passwords\n- Use separate admin accounts/roles for a channel when possible, instead of one shared login\n- Be skeptical of unsolicited \"collab\" or \"sponsorship\" messages asking you to click a link or install something"
            },
            {
                "title": "Careers & Next Steps",
                "body": "- **Ethical hacking / \"white hat\"** — security testing done legally, with written permission from the system owner.\n- **Entry certifications:** CompTIA Security+, (ISC)² Certified in Cybersecurity (CC) — both beginner-friendly and well-recognized.\n- **Legal practice platforms:** TryHackMe and HackTheBox let you practice real techniques legally, in sandboxed environments built for learning.\n- **Career paths:** SOC analyst, penetration tester, security engineer, incident responder."
            }
        ]
    },
    "networking": {
        "title": "Networking",
        "units": [
            {
                "title": "What Is a Network?",
                "body": "A network is simply two or more devices connected so they can share data. Every network — from 2 laptops in a room to the entire internet — is built from the same basic building blocks: devices, a connection medium (cable or wireless), and a shared set of rules (protocols) they all agree to follow."
            },
            {
                "title": "TCP/IP: The Language of the Internet",
                "body": "- **IP (Internet Protocol)** — gives every device a unique address, so data knows where to go (like a house address).\n- **TCP (Transmission Control Protocol)** — breaks data into numbered packets, makes sure every packet arrives, and reassembles them in the right order, resending anything lost.\n- **UDP** — faster but unreliable alternative to TCP, used when speed matters more than perfection (e.g. live video calls).\n\n**Mini exercise:** open a terminal and run `ping google.com` — this sends small packets to Google's servers and measures how long they take to return (your connection's latency)."
            },
            {
                "title": "A Short History of the Internet",
                "body": "Started as **ARPANET** in 1969, a U.S. research network linking a handful of universities. Through the 1980s–90s, TCP/IP became the universal standard all networks agreed to speak. The invention of the **World Wide Web** (HTML + browsers) in the early 1990s made the internet easy enough for ordinary people to use, turning a research tool into the global network we have today."
            },
            {
                "title": "IP Addresses & Subnetting (Basics)",
                "body": "- An IPv4 address looks like `192.168.1.10` — 4 numbers (0–255) separated by dots.\n- **Private vs. public IPs:** addresses starting with `192.168.x.x` or `10.x.x.x` are private, used only inside a home/office network; your router has one public IP that represents your whole network to the internet.\n- **Subnet mask** (e.g. `255.255.255.0`) defines how many devices can share one local network segment."
            },
            {
                "title": "Devices That Build a Network",
                "body": "Device\nRole\n\n**Router**\nConnects your network to the internet; assigns addresses to your devices\n\n**Switch**\nConnects multiple devices within one LAN, passing data only to the right device\n\n**Access Point**\nBroadcasts WiFi so devices can join the network wirelessly\n\n**Modem**\nConverts your ISP's signal (cable/fiber) into a format your router understands"
            },
            {
                "title": "LAN, WiFi, and WAN",
                "body": "Term\nMeaning\n\n**LAN**\nLocal Area Network — devices in one home/office, connected by cable or WiFi\n\n**WiFi**\nWireless way to join a LAN using radio signals instead of cables\n\n**WAN**\nWide Area Network — connects LANs across cities/countries; the internet is the largest WAN\n\n**Mini exercise:** when 4–5 PCs share one router, they form a LAN. On Windows, open \"Network\" in File Explorer, or run `arp -a` in a terminal, to see other devices currently on your own network."
            },
            {
                "title": "Basic Troubleshooting",
                "body": "Command\nWhat it tells you\n\n`ping <address>`\nIs the device reachable, and how fast?\n\n`ipconfig` (Windows) / `ifconfig` (Linux/Mac)\nYour own device's IP address and network info\n\n`tracert <address>` (Windows) / `traceroute` (Linux/Mac)\nThe path your data takes, hop by hop, to reach a destination\n\n**Mini exercise:** run `tracert google.com` and count how many \"hops\" (routers) your data passes through before reaching Google's servers."
            },
            {
                "title": "Where to Go Next",
                "body": "- **CompTIA Network+** — vendor-neutral, beginner-friendly networking certification\n- **Cisco CCNA** — industry-standard, more advanced, widely required for networking jobs\n- **Practice tool:** Cisco Packet Tracer — a free simulator to build and test virtual networks without needing real hardware"
            }
        ]
    },
    "video": {
        "title": "Viral Video Content",
        "units": [
            {
                "title": "Spy on the Competition",
                "body": "Before creating anything, study what's already working in your niche.\n\n- List 5–10 accounts already succeeding in your niche\n- For each, note: their most-viewed video, the hook (first 2 seconds), video length, and posting frequency\n- **AI's role:** paste a few competitor video transcripts/descriptions and ask AI to summarize the common patterns — hooks, pacing, topics — across all of them."
            },
            {
                "title": "Generate a Character Idea",
                "body": "A consistent character/persona makes content recognizable and memorable.\n\n- Decide: human presenter, animated character, or AI-generated persona?\n- Define: name, personality (3 adjectives), tone of voice, and one clear \"thing they're known for\"\n- **AI's role:** describe your niche and audience to AI and ask for 5 character concepts with distinct personalities to choose from."
            },
            {
                "title": "Generate the Photo",
                "body": "- Create a consistent look: same character design, same color palette, same style across all content\n- Use an AI image tool to generate a reference image, then reuse that same character/style in every thumbnail and video\n- Keep a small \"style guide\" (colors, fonts, character reference image) so every post looks like it belongs to the same brand"
            },
            {
                "title": "Map Out Viral Content",
                "body": "Turn one idea into a repeatable content system.\n\n- Build a simple content calendar: what topic, what format, what day\n- **The 3-bucket method:** mix *educational* (teaches something), *entertaining* (makes people laugh/feel something), and *trending* (jumps on a current trend) content\n- **AI's role:** give AI your niche + the 3 buckets and ask for 30 video topic ideas at once — a month of content in one sitting."
            },
            {
                "title": "Give Them a Voice",
                "body": "- Decide: your own voice, a voice actor, or AI text-to-speech/voice cloning\n- If using AI voice tools, always get proper rights/consent for any voice you clone, and disclose AI use where platforms require it\n- Keep the same voice/tone consistently so the audience recognizes it instantly"
            },
            {
                "title": "Bring Them to Use (Production)",
                "body": "- Script → record/generate visuals → edit → add captions (most viewers watch with sound off) → add music/sound effects\n- Common tools: CapCut, Premiere/DaVinci Resolve, or AI video generation tools for the visuals\n- Keep hooks in the **first 1–2 seconds** — that's what decides if someone keeps watching"
            },
            {
                "title": "Launch Your Accounts",
                "body": "- Launch consistently across multiple platforms (TikTok, YouTube Shorts, Instagram Reels, Telegram) under one unified brand name and visual style\n- Post on a regular schedule — consistency beats occasional \"perfect\" videos\n- Cross-promote: mention your Telegram channel in your videos, and vice versa"
            },
            {
                "title": "Crown the Winner (A/B Testing)",
                "body": "- Try 2–3 different hooks or formats for similar content\n- Use each platform's own analytics (watch time, retention graph, shares) to see which actually performs\n- Double down on the winning format/hook style, and retire what isn't working"
            },
            {
                "title": "Start Making Money",
                "body": "Common monetization paths, usually combined:\n\n1. **Platform ad revenue** (YouTube Partner Program, TikTok Creator Rewards)\n2. **Brand sponsorships** — once you have an engaged audience\n3. **Affiliate links** — earning a commission promoting others' products\n4. **Your own product/service** — e.g. selling access to one of your own apps, or your Telegram channel's premium content"
            },
            {
                "title": "Count the Profits",
                "body": "- Track revenue **per platform and per video type**, not just total income\n- Reinvest in whatever format is actually earning — more of what works, less of what doesn't\n- Review monthly: which videos performed best, and why — feed that back into competitor research and content planning"
            }
        ]
    },
    "arduino": {
        "title": "Robotics with Arduino",
        "units": [
            {
                "title": "What Is Robotics?",
                "body": "Robotics is the field of designing, building, and programming machines that can **sense** their environment (via sensors) and **act** on it (via motors/actuators) — often automatically, with little or no direct human control.\n\nEvery robot, simple or advanced, follows the same loop: **Sense → Think → Act**."
            },
            {
                "title": "What Is Arduino?",
                "body": "Arduino is a small, affordable, open-source **microcontroller board** — a tiny computer built specifically to read sensors and control motors, lights, and other hardware.\n\n- **Arduino board** (e.g. Arduino Uno) — the physical hardware\n- **Arduino IDE** — free software where you write code (a simplified C/C++) and upload it to the board\n- **Why Arduino for beginners:** low cost, huge community, thousands of free tutorials, and you see cause → code → physical effect immediately"
            },
            {
                "title": "Core Components",
                "body": "Component\nRole\n\n**Microcontroller (the chip itself)**\nRuns your code\n\n**Digital pins**\nRead/send ON-OFF (HIGH/LOW) signals\n\n**Analog pins**\nRead a range of values (e.g. exact light brightness, not just on/off)\n\n**Breadboard**\nLets you build circuits without soldering\n\n**Jumper wires**\nConnect components to the board\n\n**Resistor**\nLimits current to protect components like LEDs"
            },
            {
                "title": "Your First Program: Blink an LED",
                "body": "```cpp\nvoid setup() {\n  pinMode(13, OUTPUT);   // tell pin 13 it will send signals\n}\n\nvoid loop() {\n  digitalWrite(13, HIGH); // turn LED on\n  delay(1000);            // wait 1 second\n  digitalWrite(13, LOW);  // turn LED off\n  delay(1000);            // wait 1 second\n}\n```\n\n`setup()` runs once when the board powers on; `loop()` repeats forever. This is the structure of **every** Arduino program."
            },
            {
                "title": "Sensors (Inputs)",
                "body": "Sensors let the robot \"sense\" its environment:\n\n- **Ultrasonic sensor (HC-SR04)** — measures distance using sound waves, like bat echolocation\n- **Light sensor (LDR)** — detects brightness\n- **Button** — detects a simple press (HIGH/LOW)\n- **Temperature sensor** — reads surrounding temperature\n\n```cpp\nint buttonState = digitalRead(2); // reads the button on pin 2\nif (buttonState == HIGH) {\n  // button is pressed\n}\n```"
            },
            {
                "title": "Actuators (Outputs)",
                "body": "Actuators let the robot \"act\" on the world:\n\n- **DC motor** — spins wheels (needs a motor driver like L298N since Arduino pins alone can't supply enough power)\n- **Servo motor** — moves to a precise angle (e.g. a robotic arm joint)\n- **LED** — simple visual output\n- **Buzzer** — simple sound output"
            },
            {
                "title": "Combining Sensors + Actuators",
                "body": "```cpp\n// Simplified logic: stop the motor if an object is too close\nint distance = readUltrasonicDistance(); // custom function using the sensor\nif (distance < 10) {\n  stopMotor();\n} else {\n  moveForward();\n}\n```\n\nThis simple pattern — **read a sensor, decide, act** — is the foundation of almost every real robot behavior, from obstacle avoidance to self-driving cars."
            },
            {
                "title": "Suggested Project Progression",
                "body": "1. Blink an LED\n2. Read a button press and light an LED when pressed\n3. Read an ultrasonic sensor and print the distance to the Serial Monitor\n4. Control a motor so it stops when an object gets close (first real \"robot\" behavior)\n5. Build a simple **obstacle-avoiding robot**: moves forward, turns when it detects something close\n6. Build a simple **line-following robot** using light sensors to follow a dark line on the floor"
            }
        ]
    }
}


def get_main_menu() -> InlineKeyboardMarkup:
    buttons = []
    for key, info in COURSES.items():
        buttons.append([
            InlineKeyboardButton(info["title"], callback_data=f"course:{key}")
        ])
    buttons.append([InlineKeyboardButton("Ask AI", callback_data="ai:ask")])
    return InlineKeyboardMarkup(buttons)


async def ask_gemini(system_prompt: str, history: list[dict]) -> str:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    client = genai.Client(api_key=GEMINI_API_KEY)
    contents = [
        types.Content(
            role="model" if turn["role"] == "assistant" else "user",
            parts=[types.Part.from_text(text=turn["content"])],
        )
        for turn in history
    ]
    response = await client.aio.models.generate_content(
        model=MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            max_output_tokens=800,
        ),
    )
    if not response.text:
        raise RuntimeError("Gemini returned an empty response")
    return response.text


async def get_ai_response(question: str, language: str = "en", history: list[dict] | None = None) -> str:
    language_name = LANGUAGE_NAMES.get(language, "English")
    prompt = f"{AI_SYSTEM_PROMPT} Answer in {language_name}."
    conversation = list(history or [])
    conversation.append({"role": "user", "content": question})
    return await ask_gemini(prompt, conversation)


def get_ai_cancel_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("Cancel", callback_data="ai:cancel")]])


def get_course_menu(course_key: str) -> InlineKeyboardMarkup:
    course = COURSES[course_key]
    buttons = []
    for index, unit in enumerate(course["units"]):
        buttons.append([
            InlineKeyboardButton(f"Unit {index + 1}: {unit['title']}", callback_data=f"unit:{course_key}:{index}")
        ])
    buttons.append([InlineKeyboardButton("🏠 Main menu", callback_data="menu:main")])
    return InlineKeyboardMarkup(buttons)


def get_unit_nav(course_key: str, unit_index: int) -> InlineKeyboardMarkup:
    buttons = []
    course = COURSES[course_key]
    prev_index = unit_index - 1
    next_index = unit_index + 1

    row = []
    if prev_index >= 0:
        row.append(InlineKeyboardButton("⬅ Previous", callback_data=f"unit:{course_key}:{prev_index}"))
    if next_index < len(course["units"]):
        row.append(InlineKeyboardButton("Next ➡", callback_data=f"unit:{course_key}:{next_index}"))
    buttons.append(row)
    buttons.append([
        InlineKeyboardButton("📚 Course units", callback_data=f"course:{course_key}"),
        InlineKeyboardButton("🏠 Main menu", callback_data="menu:main")
    ])
    return InlineKeyboardMarkup(buttons)


async def send_main_menu(update: Update, context: CallbackContext):
    message = update.effective_message
    if message is None:
        return
    await message.reply_text(WELCOME_TEXT, reply_markup=get_main_menu())


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_main_menu(update, context)


async def handle_callback_query(update: Update, context: CallbackContext):
    await update.callback_query.answer()
    query = update.callback_query

    if query.data == "ai:ask":
        context.user_data["awaiting_ai"] = True
        language = context.user_data.get("language", "en")
        prompt = "Send your question and Hamvod's AI tutor will help." if language == "en" else "ጥያቄዎን ይላኩ፤ የሃምቮድ AI አስተማሪ ይረዳዎታል።"
        await query.edit_message_text(prompt, reply_markup=get_ai_cancel_menu())
        return

    if query.data == "ai:cancel":
        context.user_data["awaiting_ai"] = False
        language = context.user_data.get("language", "en")
        cancelled = "Ask AI cancelled." if language == "en" else "የAI ጥያቄ ተሰርዟል።"
        await query.edit_message_text(cancelled, reply_markup=get_main_menu())
        return

    if query.data == "menu:main":
        await query.edit_message_text(WELCOME_TEXT, reply_markup=get_main_menu())
        return

    if query.data.startswith("course:"):
        course_key = query.data.split(":", 1)[1]
        course = COURSES[course_key]
        summary = f"📚 {course['title']}\n\nChoose a lesson unit below."
        await query.edit_message_text(summary, reply_markup=get_course_menu(course_key))
        return

    if query.data.startswith("unit:"):
        _, course_key, unit_index = query.data.split(":")
        unit_index_int = int(unit_index)
        course = COURSES[course_key]
        unit = course["units"][unit_index_int]
        body = f"<b>{course['title']}</b>\n\n<b>Unit {unit_index_int + 1}: {unit['title']}</b>\n\n{unit['body']}"
        await query.edit_message_text(body, reply_markup=get_unit_nav(course_key, unit_index_int), parse_mode="HTML")
        return

    await query.edit_message_text(WELCOME_TEXT, reply_markup=get_main_menu())


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if message is None or not context.user_data.get("awaiting_ai"):
        return

    question = (message.text or "").strip()
    language = context.user_data.get("language", "en")
    if not question:
        prompt = "Please send a text question." if language == "en" else "እባክዎ የጽሑፍ ጥያቄ ይላኩ።"
        await message.reply_text(prompt)
        return

    context.user_data["awaiting_ai"] = False
    history = context.user_data.setdefault("ai_history", [])
    try:
        answer = await get_ai_response(question, language, list(history))
    except RuntimeError as error:
        if "GEMINI_API_KEY" in str(error):
            answer = (
                "Gemini AI is not configured yet. Please contact the bot administrator."
                if language == "en"
                else "Gemini AI አሁን ስላልተዋቀረ እባክዎ የቦቱን አስተዳዳሪ ያነጋግሩ።"
            )
        else:
            answer = (
                "The AI tutor could not answer right now. Please try again later."
                if language == "en"
                else "የAI አስተማሪው አሁን መመለስ አልቻለም። እባክዎ ቆይተው እንደገና ይሞክሩ።"
            )
            print(f"Gemini request failed: {error}")
    except Exception as error:
        answer = (
            "The AI tutor could not answer right now. Please try again later."
            if language == "en"
            else "የAI አስተማሪው አሁን መመለስ አልቻለም። እባክዎ ቆይተው እንደገና ይሞክሩ።"
        )
        print(f"Gemini request failed: {error}")
    else:
        history.extend([
            {"role": "user", "content": question},
            {"role": "assistant", "content": answer},
        ])

    await message.reply_text(answer)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Use /start to open the Hamvod course menu. Select a topic and then a unit to read the lesson content."
    )


async def error_handler(update: object, context: CallbackContext):
    print(f"Update {update} caused error {context.error}")


def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not set. Add it to your .env file or environment variables.")

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(handle_callback_query))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    app.add_error_handler(error_handler)
    print(f"{BOT_NAME} is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
