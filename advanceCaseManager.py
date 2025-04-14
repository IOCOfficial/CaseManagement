import re
import subprocess
import tiktoken
from colorama import init, Fore, Style
import markdown2
import time
from weasyprint import HTML
import os
from openai import OpenAI
import shutil
from datetime import datetime
from tabulate import tabulate
from tqdm import tqdm
from dotenv import load_dotenv, set_key, unset_key

BASE_DIR = os.path.expanduser("~/Investigations")

init(autoreset=True) 

SUBFOLDERS = [
    "0. Introduction",
    "1. Blockchain Analysis",
    "2. OSINT",
    "3. Evidence",
    "4. Report",
    "5. Strategic Priorities", 
    "99. Tasks"
]


def get_api_key():
    load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))
    return os.getenv("OPENAI_API_KEY")


def manage_api_key():
    env_path = os.path.join(BASE_DIR, ".env")
    load_dotenv(dotenv_path=env_path)

    current_key = os.getenv("OPENAI_API_KEY")
    masked_key = current_key[:4] + "*" * (len(current_key) - 8) + current_key[-4:] if current_key else "None"

    print("\n🔐 API Key Management")
    print(f"Current API Key: {Fore.YELLOW}{masked_key}{Fore.RESET}")
    print("\nOptions:")
    print("1. Update API Key")
    print("2. Clear API Key")
    print("3. Back to Menu")

    choice = input("Enter choice: ").strip()
    
    if choice == "1":
        new_key = input("Enter new OpenAI API Key: ").strip()
        if new_key.startswith("sk-") and len(new_key) > 20:
            set_key(env_path, "OPENAI_API_KEY", new_key)
            print("✅ API key updated.")
        else:
            print("❌ Invalid API key format.")
    elif choice == "2":
        unset_key(env_path, "OPENAI_API_KEY")
        print("✅ API key cleared.")
    elif choice == "3":
        return
    else:
        print("❌ Invalid choice.")

def create_case(case_id, status, description, payment_status="Not Paid"):
    case_folder = os.path.join(BASE_DIR, f"Case_{case_id}")
    if os.path.exists(case_folder):
        print(f"❌ Case {case_id} already exists.")
        return
    os.makedirs(case_folder)

    for sub in SUBFOLDERS:
        subfolder_path = os.path.join(case_folder, sub)
        os.makedirs(subfolder_path)
        md_path = os.path.join(subfolder_path, f"{sub}.md")
        with open(md_path, "w") as md_file:
            if sub == "5. Strategic Priorities":
                md_file.write(
                    "# Strategic Priorities\n\n"
                    
                    "This is where you set the priorities for when the AI generates your report. It will scan this section first and prioritize what you have listed. [Delete anything you don't use]"

                    "- Focus on laundering paths and addresses tied to services like WizardSwap, BC.Game, Cryptomus.\n"
                    "- Identify subpoena targets (services that require KYC).\n"
                    "- Prioritize wallet activity that *proves ownership* or *intent to obfuscate*.\n"
                    "- DO NOT overemphasize tweet volume or social chatter unless it links directly to transactions or compromise.\n"
                    "- Goal: Provide actionable insights for law enforcement and forensic follow-up.\n"
                )
            else:
                md_file.write(f"# {sub}\n")

    with open(os.path.join(case_folder, "notes.txt"), "w") as f:
        f.write(f"Case ID: {case_id}\n")
        f.write(f"Status: {status}\n")
        f.write(f"Description: {description}\n")
        f.write(f"Payment Status: {payment_status}\n")
        f.write(f"Created: {datetime.now()}\n")

    print(f"✅ Case {case_id} created successfully.")

    try:
        intro_md = os.path.join(case_folder, "0. Introduction", "0. Introduction.md")
        subprocess.run(["open", "-a", "Obsidian", intro_md])
        print(f"\n🚀 Obsidian has been opened.")
        print("📌 To begin working with this case as a vault:")
        print(f"1. In Obsidian, click 'Open folder as vault'")
        print(f"2. Select: {case_folder}")
        print(f"3. (Optional) Enable plugins or templates specific to this case.\n")
    except Exception as e:
        print(f"⚠️ Could not open in Obsidian: {e}")

    VAULT_TEMPLATE = os.path.expanduser("~/vault_template/.obsidian")

    if os.path.exists(VAULT_TEMPLATE):
        try:
            shutil.copytree(VAULT_TEMPLATE, os.path.join(case_folder, ".obsidian"))
            print("📦 Obsidian vault settings applied to new case.")
        except FileExistsError:
            print("⚠️ .obsidian folder already exists in this case. Skipping template.")


def list_cases(return_data=False):
    if not os.path.exists(BASE_DIR):
        print("📁 No cases found.")
        return [] if return_data else None

    # Get terminal width
    term_width = shutil.get_terminal_size((120, 20)).columns
    desc_max_width = max(30, min(90, term_width - 80))  # dynamic but capped

    table = []
    case_data = []

    for folder in os.listdir(BASE_DIR):
        case_path = os.path.join(BASE_DIR, folder)
        notes_file = os.path.join(case_path, "notes.txt")
        if os.path.exists(notes_file):
            with open(notes_file, "r") as f:
                lines = f.readlines()
                status = next((line.split(":")[1].strip() for line in lines if line.startswith("Status:")), "")
                description = next((line.split(":")[1].strip() for line in lines if line.startswith("Description:")), "")
                case_id = folder.replace("Case_", "")
                payment_status = next((line.split(":")[1].strip() for line in lines if line.startswith("Payment Status:")), "")

                # Truncate long descriptions
                if len(description) > desc_max_width:
                    description = description[:desc_max_width - 3] + "..."

                table.append([len(case_data)+1, case_id, status, description, payment_status])
                case_data.append(case_id)

    print(tabulate(
        table,
        headers=["#", "Case ID", "Status", "Description", "Payment Status"],
        tablefmt="fancy_grid"
    ))

    return case_data if return_data else None

def view_case(case_id):
    case_path = os.path.join(BASE_DIR, f"Case_{case_id}")
    notes_file = os.path.join(case_path, "notes.txt")

    if not os.path.exists(notes_file):
        print(f"❌ Case {case_id} not found.")
        return

    # Read and print case notes
    print("\n📝 " + Style.BRIGHT + "Case Notes:")
    with open(notes_file, "r") as f:
        print(Fore.LIGHTWHITE_EX + f.read())

    # Folder summary
    print(Style.BRIGHT + "\n📂 Folder Summary:")
    total_folders = len(SUBFOLDERS)
    folders_with_files = 0

    folder_map = {}  # to store files for deep dive

    for sub in SUBFOLDERS:
        sub_path = os.path.join(case_path, sub)
        if not os.path.exists(sub_path):
            print(f"❌ Missing: {sub}")
            continue

        files = [
            f for f in os.listdir(sub_path)
            if os.path.isfile(os.path.join(sub_path, f))
        ]
        num_files = len(files)
        last_mod = datetime.fromtimestamp(os.path.getmtime(sub_path)).strftime("%Y-%m-%d %H:%M")

        if num_files > 0:
            folders_with_files += 1
            preview = ""
            for file in files:
                if file.endswith(".md"):
                    md_path = os.path.join(sub_path, file)
                    with open(md_path, "r") as md_file:
                        first_line = md_file.readline().strip()
                        if first_line:
                            # 🔗 Shorten URLs in preview line
                            urls = re.findall(r'(https?://[^\s)]+)', first_line)
                            for url in urls:
                                if len(url) > 30:
                                    short_url = url[:30] + "..."
                                    first_line = first_line.replace(url, short_url)
                            preview = f" - 📝 {first_line}"
                            break
            print(f"📁 {sub:<25} {num_files} file{'s' if num_files != 1 else ''} | Last Modified: {last_mod}{preview}")
            folder_map[sub] = [os.path.join(sub_path, f) for f in files if f.endswith(".md")]
        else:
            print(f"📁 {sub:<25} ❗ Empty | Last Modified: {last_mod}")

    # Deep dive prompt
    dive = input("\n🔍 Would you like to deep dive into the case contents? (y/n): ").strip().lower()
    if dive != "y":
        print("↩️ Returning to main menu.")
        return

    print("\n💡 " + Style.BRIGHT + "Deep Dive Into Case Notes:\n")

    for folder, md_files in folder_map.items():
        print(Fore.CYAN + Style.BRIGHT + f"=== {folder} ===")
        for md_file in md_files:
            print(Fore.YELLOW + f"\n📄 {os.path.basename(md_file)}")
            with open(md_file, "r") as f:
                for line in f:
                    line = line.rstrip()
                    if line.startswith("#"):
                        print(Fore.GREEN + Style.BRIGHT + line)
                    elif line.strip():
                        # 🔗 Truncate URLs in the line
                        urls = re.findall(r'(https?://[^\s)]+)', line)
                        for url in urls:
                            if len(url) > 30:
                                short_url = url[:30] + "..."
                                line = line.replace(url, short_url)
                        print(Fore.WHITE + line)
            print("\n" + "-" * 40)

    print("\n✅ Deep dive complete.")


def update_status(case_id, new_status):
    notes_file = os.path.join(BASE_DIR, f"Case_{case_id}", "notes.txt")
    if not os.path.exists(notes_file):
        print(f"❌ Case {case_id} not found.")
        return
    with open(notes_file, "r") as f:
        lines = f.readlines()
    with open(notes_file, "w") as f:
        for line in lines:
            if line.startswith("Status:"):
                f.write(f"Status: {new_status}\n")
            else:
                f.write(line)
    print(f"✅ Status updated for Case {case_id}.")

def update_status_and_payment(case_id, new_status, new_payment_status):
    notes_file = os.path.join(BASE_DIR, f"Case_{case_id}", "notes.txt")
    if not os.path.exists(notes_file):
        print(f"❌ Case {case_id} not found.")
        return
    with open(notes_file, "r") as f:
        lines = f.readlines()
    with open(notes_file, "w") as f:
        for line in lines:
            if line.startswith("Status:"):
                f.write(f"Status: {new_status}\n")
            elif line.startswith("Payment Status:"):
                f.write(f"Payment Status: {new_payment_status}\n")
            else:
                f.write(line)
    print(f"✅ Status and payment updated for Case {case_id}.")

def open_case_in_obsidian(case_id):
    case_path = os.path.join(BASE_DIR, f"Case_{case_id}")
    if not os.path.exists(case_path):
        print(f"❌ Case '{case_id}' does not exist.")
        return

    try:
        subprocess.run(["open", "-a", "Obsidian", case_path])
        print(f"🚀 Opened Case '{case_id}' in Obsidian.")
    except Exception as e:
        print(f"⚠️ Could not open Obsidian: {e}")

def select_case():
    case_list = list_cases(return_data=True)
    if not case_list:
        return None
    try:
        choice = int(input("Select case by number: "))
        if 1 <= choice <= len(case_list):
            return case_list[choice - 1]
        else:
            print("❌ Invalid selection.")
            return None
    except ValueError:
        print("❌ Invalid input. Please enter a number.")
        return None

def delete_case(case_id):
    case_folder = os.path.join(BASE_DIR, f"Case_{case_id}")
    if os.path.exists(case_folder):
        confirm = input(f"⚠️ Are you sure you want to delete Case {case_id}? (yes/no): ")
        if confirm.lower() == "yes":
            shutil.rmtree(case_folder)
            print(f"🗑️ Case {case_id} deleted.")
    else:
        print(f"❌ Case {case_id} not found.")

def num_tokens_from_string(string, model="gpt-4"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(string))

def chunk_content_map(content_map, max_tokens=3000):
    current_chunk = []
    current_tokens = 0
    chunks = []

    for item in content_map:
        path = item["path"]
        content = item["content"][:5000]  # optional safety trim
        tokens = num_tokens_from_string(content)

        if current_tokens + tokens > max_tokens:
            chunks.append(current_chunk)
            current_chunk = []
            current_tokens = 0

        current_chunk.append((path, content))
        current_tokens += tokens

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

def estimate_total_time(chunks, delay=10, per_chunk_estimate=15):
    total_secs = len(chunks) * (delay + per_chunk_estimate)
    return str(datetime.utcfromtimestamp(total_secs).strftime('%H:%M:%S'))


def generate_full_ai_report_from_structure(content_map, case_id):
    try:
        client = OpenAI(api_key=get_api_key())
        chunks = chunk_content_map(content_map, max_tokens=3000)

        # Extract strategic priorities if present
        priorities = next((item["content"] for item in content_map if item.get("is_priority")), None)

        final_report_parts = []

        print(f"🧠 Preparing {len(chunks)} chunks to send to GPT-4...")
        est_time = estimate_total_time(chunks)
        print(f"⏳ Estimated total time: {est_time} (with {len(chunks)} chunks)\n")

        for i, chunk in enumerate(tqdm(chunks, desc="📡 Sending to GPT-4", ncols=80)):
            compiled_text = ""
            for path, content in chunk:
                compiled_text += f"\n\n---\n📄 Path: {path}\n\n{content}\n"

            try:
                system_prompt = (
                    "You are an expert investigator building a professional report from case material. "
                    "Prioritize evidence and clarity. Summarize only the most relevant and actionable content.\n\n"
                )
                if priorities:
                    system_prompt += (
                        "⚠️ Strategic Priorities for this case:\n"
                        f"{priorities}\n\n"
                        "↳ Always align your analysis with the above goals.\n"
                    )

                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {
                            "role": "user",
                            "content": compiled_text
                        }
                    ],
                    temperature=0.2
                )

                part = response.choices[0].message.content.strip()
                final_report_parts.append(part)

            except Exception as e:
                final_report_parts.append(f"_Error in chunk {i+1}: {e}_")

            time.sleep(10)  # 💤 Cooldown to avoid rate limits

        # Combine all parts
        full_report = (
            "# 🧠 AI-GENERATED REPORT\n\n" +
            "\n\n---\n".join(final_report_parts) +
            "\n\n---\n_Disclaimer: This report was generated by AI based on the case file structure and contents._"
        )

        return full_report

    except Exception as e:
        return f"_AI report generation failed: {e}_"

def collect_case_content(case_path):
    content_map = []

    # First, look for Strategic Priorities
    priors_path = os.path.join(case_path, "5. Strategic Priorities", "5. Strategic Priorities.md")
    if os.path.exists(priors_path):
        with open(priors_path, "r") as f:
            text = f.read().strip()
            if text:
                content_map.append({
                    "path": "5. Strategic Priorities/5. Strategic Priorities.md",
                    "content": text,
                    "is_priority": True  # mark for special treatment
                })

    # Then collect the rest
    for root, dirs, files in os.walk(case_path):
        for file in files:
            if file.endswith(".md"):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, case_path)
                if rel_path == "5. Strategic Priorities/5. Strategic Priorities.md":
                    continue  # already added
                try:
                    with open(full_path, "r") as f:
                        text = f.read().strip()
                        if text:
                            content_map.append({
                                "path": rel_path,
                                "content": text,
                                "is_priority": False
                            })
                except Exception as e:
                    print(f"⚠️ Failed to read {file}: {e}")

    return content_map

def generate_case_report(case_id, use_ai=False):
    case_path = os.path.join(BASE_DIR, f"Case_{case_id}")
    notes_file = os.path.join(case_path, "notes.txt")
    report_folder = os.path.join(case_path, "4. Report")
    os.makedirs(report_folder, exist_ok=True)
    default_filename = f"Case_{case_id}_Report.md"
    md_output_path = os.path.join(report_folder, default_filename)

    # 📌 Check strategic priorities early if using AI
    if use_ai:
        strategic_dir = os.path.join(case_path, "5. Strategic Priorities")
        strategic_path = os.path.join(strategic_dir, "5. Strategic Priorities.md")

        if not os.path.exists(strategic_path):
            print(Fore.YELLOW + "\n⚠️ 'Strategic Priorities.md' not found. Creating from template...")

            os.makedirs(strategic_dir, exist_ok=True)
            with open(strategic_path, "w") as md_file:
                md_file.write(
                    "# Strategic Priorities\n\n"
                    "This is where you set the priorities for when the AI generates your report. "
                    "It will scan this section first and prioritize what you have listed [Delete anything you don't use]\n\n"
                    "- Focus on laundering paths and addresses tied to services like WizardSwap, BC.Game, Cryptomus.\n"
                    "- Identify subpoena targets (services that require KYC).\n"
                    "- Prioritize wallet activity that *proves ownership* or *intent to obfuscate*.\n"
                    "- DO NOT overemphasize tweet volume or social chatter unless it links directly to transactions or compromise.\n"
                    "- Goal: Provide actionable insights for law enforcement and forensic follow-up.\n"
                )
            print("✅ Template created successfully.\n")

        # Prompt user before proceeding
        print("\n📌 Strategic Priorities Check:")
        print(f"📄 {strategic_path}")
        print("➡️  Make sure your strategic goals are up to date and relevant before proceeding.\n")
        with open(strategic_path, "r") as f:
            print(Fore.CYAN + f.read())

        print(Fore.YELLOW + "\n⚠️  Do you want to update strategic priorities before continuing?")
        print("1. Yes, open in Obsidian")
        print("2. No, proceed with AI report generation")
        print("3. Cancel")

        choice = input("Enter your choice (1/2/3): ").strip()
        if choice == "1":
            try:
                subprocess.run(["open", "-a", "Obsidian", strategic_path])
                print("📝 Obsidian opened to Strategic Priorities. Re-run the report when you're ready.")
            except Exception as e:
                print(f"⚠️ Failed to open Obsidian: {e}")
            return
        elif choice == "2":
            print("✅ Proceeding with AI report generation...\n")
        elif choice == "3":
            print("❌ Cancelled by user.")
            return
        else:
            print("❌ Invalid selection. Cancelling.")
            return

    # 🧾 Handle existing report
    if os.path.exists(md_output_path):
        print(f"⚠️ A report already exists for Case {case_id}: {default_filename}")
        choice = input("Do you want to overwrite (o) or save as a new version (n)? [o/n]: ").strip().lower()
        if choice == "n":
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            md_output_path = os.path.join(report_folder, f"Case_{case_id}_Report_{timestamp}.md")
        elif choice != "o":
            print("❌ Invalid input. Cancelling report generation.")
            return

    # 📄 Begin building the report content
    report_md = f"# 🕵️‍♂️ INVESTIGATION REPORT: Case {case_id}\n"
    report_md += f"**Date Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    report_md += "**Generated by**: Investigation Case Manager (Automated System)\n\n---\n"

    # 📋 Include case notes
    if os.path.exists(notes_file):
        with open(notes_file, "r") as f:
            notes = f.read()
            report_md += "## 📋 Case Notes (from notes.txt)\n"
            report_md += f"```\n{notes.strip()}\n```\n\n---\n"

    # 📦 Add each folder's content
    print("\n⏳ Generating report. Please wait...\n")
    all_section_text = ""
    for sub in tqdm(SUBFOLDERS, desc="📊 Building Sections", ncols=80):
        time.sleep(0.1)
        sub_path = os.path.join(case_path, sub)
        md_files = [f for f in os.listdir(sub_path) if f.endswith(".md")] if os.path.exists(sub_path) else []

        full_text = ""
        for md_file in md_files:
            with open(os.path.join(sub_path, md_file), "r") as f:
                full_text += f.read().strip() + "\n\n"

        if full_text.strip():
            summary = generate_summary_for_section(sub, full_text, use_ai=use_ai)
            report_md += f"## {sub}\n"
            report_md += f"**Summary**:\n{summary}\n\n"
            report_md += "**Details**:\n"
            report_md += f"```\n{full_text.strip()}\n```\n\n---\n"
            all_section_text += full_text + "\n"

    # 🤖 Final case summary via AI or fallback
    if use_ai:
        print("🧠 Mapping and reasoning through all folders...")
        content_map = collect_case_content(case_path)
        ai_report = generate_full_ai_report_from_structure(content_map, case_id)
        report_md = f"# 🧠 AI-GENERATED REPORT\n\n{ai_report}\n\n---\n" + report_md
    else:
        case_summary = generate_summary_for_section("Case Overview", all_section_text.strip(), use_ai=False)
        report_md = report_md.replace("## 📋", "## 📝 Summary\n" + case_summary + "\n\n---\n## 📋")

    # 🚨 Add disclaimer
    report_md += "## 🛑 Disclaimer\n"
    report_md += "This report was generated automatically using investigative data provided by the user. "
    report_md += "All content should be verified for accuracy before official submission.\n"

    # 💾 Save the report
    with open(md_output_path, "w") as f:
        f.write(report_md)

    print(f"\n✅ Report generated successfully:")
    print(f"📄 {md_output_path}")

def generate_summary_for_section(section_name, text, use_ai=False):
    if not text.strip():
        return "_No content available._"

    if not use_ai:
        # Traditional fallback
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        bullet_points = []
        for line in lines:
            if line.startswith("#"):
                bullet_points.append(f"- {line.lstrip('#').strip()}")
            elif len(line.split()) >= 6:
                bullet_points.append(f"- {line[:100]}..." if len(line) > 100 else f"- {line}")
            if len(bullet_points) >= 4:
                break
        return "\n".join(bullet_points) if bullet_points else "_No summary available._"

    try:
        client = OpenAI(api_key=get_api_key())
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": (
                    "You are an AI assistant helping generate a formal investigation report for law enforcement. "
                    f"Summarize this section: '{section_name}' with professionalism and clarity. "
                    "Use bullet points or a short summary paragraph. Avoid speculation."
                )},
                {"role": "user", "content": text}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"_AI summary failed: {e}_"

def menu():
    os.makedirs(BASE_DIR, exist_ok=True)
    while True:
        print("\n📂 Investigation Case Manager")
        print(tabulate([
            ["1", "Create Case"],
            ["2", "List Cases"],
            ["3", "View Case"],
            ["4", "Update Case Status"],
            ["5", "Delete Case"],
            ["6", "Generate Case Report"],
            ["7", "Open Case in Obsidian"],
            ["8", "Manage API Key"],
            ["99", "Exit"]
        ], headers=["Option", "Action"], tablefmt="grid"))



        choice = input("Enter choice: ")

        if choice == "1":
            while True:
                case_id = input("Enter Case ID: ").strip()
                case_folder = os.path.join(BASE_DIR, f"Case_{case_id}")
                if os.path.exists(case_folder):
                    print(f"❌ Case '{case_id}' already exists. Please choose a different ID.")
                elif not case_id:
                    print("❌ Case ID cannot be empty.")
                else:
                    break

            
            print("Select Case Status:")
            print("1. Open")
            print("2. Closed")
            status_choice = input("Enter choice (1 or 2): ")

            if status_choice == "1":
                status = "Open"
            elif status_choice == "2":
                status = "Closed"
            else:
                print("❌ Invalid status selection.")
                return

            description = input("Enter Case Description: ")
            
            print("Select Payment Status:")
            print("1. Not Paid")
            print("2. Partial Payment")
            print("3. Paid")
            pay_choice = input("Enter choice (1/2/3): ")

            payment_status_map = {"1": "Not Paid", "2": "Partial Payment", "3": "Paid"}
            payment_status = payment_status_map.get(pay_choice, "Not Paid")

            create_case(case_id, status, description, payment_status)


        elif choice == "2":
            list_cases()
        elif choice == "3":
            case_id = select_case()
            if case_id:
               view_case(case_id)
        elif choice == "4":
            case_id = select_case()
            if case_id:
                # Select new case status
                print("Select new case status:")
                print("1. Open")
                print("2. Closed")
                status_choice = input("Enter choice (1 or 2): ")

                if status_choice == "1":
                    new_status = "Open"
                elif status_choice == "2":
                    new_status = "Closed"
                else:
                    print("❌ Invalid status selection.")
                    return

                # Select new payment status
                print("Select new payment status:")
                print("1. Not Paid")
                print("2. Paid")
                print("3. Partial Payment")
                pay_choice = input("Enter choice (1/2/3): ")
                payment_status_map = {"1": "Not Paid", "2": "Paid", "3": "Partial Payment"}
                new_payment_status = payment_status_map.get(pay_choice)

                if not new_payment_status:
                    print("❌ Invalid payment status selection.")
                    return

                update_status_and_payment(case_id, new_status, new_payment_status)


        elif choice == "5":
            case_id = select_case()
            if case_id:
                delete_case(case_id)
        elif choice == "6":
            case_id = select_case()
            if not case_id:
                continue

            print("\n📝 How would you like to generate the report?")
            print("1. Traditional method (no AI)")
            print("2. Use ChatGPT (AI-powered summaries)")
            method_choice = input("Enter choice (1 or 2): ").strip()

            if method_choice == "1":
                generate_case_report(case_id, use_ai=False)
            elif method_choice == "2":
                api_key = get_api_key()
                if not api_key:
                    print("\n⚠️ No OpenAI API key found.")
                    print("To use AI-powered summaries, please:")
                    print("1. Go to https://platform.openai.com/account/api-keys")
                    print("2. Copy your API key")
                    print("3. Run this in your terminal to set it:\n")
                    print('   export OPENAI_API_KEY="sk-..."')
                    print("4. Restart this script after setting the key.\n")
                else:
                    generate_case_report(case_id, use_ai=True)
            else:
                print("❌ Invalid choice.")


        elif choice == "7":
            case_id = select_case()
            if case_id:
                open_case_in_obsidian(case_id)
        elif choice == "8":
            manage_api_key()

        elif choice == "99":
            print("👋 Exiting.")
            break
        else:
            print("❓ Invalid choice. Try again.")

if __name__ == "__main__":
    menu()
