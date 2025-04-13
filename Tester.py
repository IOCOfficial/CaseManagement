import re
import subprocess
from colorama import init, Fore, Style
import markdown2
from weasyprint import HTML
import os
from openai import OpenAI
import shutil
from datetime import datetime
from tabulate import tabulate

init(autoreset=True) 

BASE_DIR = os.path.expanduser("~/Investigations")

SUBFOLDERS = [
    "0. Introduction",
    "1. Blockchain Analysis",
    "2. OSINT",
    "3. Evidence",
    "4. Report",
    "99. Tasks"
]

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
            md_file.write(f"# {sub}\n")

    with open(os.path.join(case_folder, "notes.txt"), "w") as f:
        f.write(f"Case ID: {case_id}\n")
        f.write(f"Status: {status}\n")
        f.write(f"Description: {description}\n")
        f.write(f"Payment Status: {payment_status}\n")
        f.write(f"Created: {datetime.now()}\n")

    print(f"✅ Case {case_id} created successfully.")

    try:
        # ✅ Open directly to '0. Introduction.md' using Obsidian
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
                table.append([len(case_data)+1, case_id, status, description, payment_status])
                case_data.append(case_id)

    print(tabulate(table, headers=["#", "Case ID", "Status", "Description", "Payment Status"], tablefmt="fancy_grid"))
    return case_data if return_data else None

import os
from datetime import datetime

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
        # 🔑 Ensure your API key is set in environment variable
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

def generate_case_report(case_id, use_ai=False):
    case_path = os.path.join(BASE_DIR, f"Case_{case_id}")
    notes_file = os.path.join(case_path, "notes.txt")
    report_md = f"# 🕵️‍♂️ INVESTIGATION REPORT: Case {case_id}\n"
    report_md += f"**Date Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    report_md += "**Generated by**: Investigation Case Manager (Automated System)\n\n---\n"

    # Add Case Notes section
    if os.path.exists(notes_file):
        with open(notes_file, "r") as f:
            notes = f.read()
            report_md += "## 📋 Case Notes (from notes.txt)\n"
            report_md += f"```\n{notes.strip()}\n```\n\n---\n"

    # Build section content
    all_section_text = ""
    for sub in SUBFOLDERS:
        sub_path = os.path.join(case_path, sub)
        md_files = [
            f for f in os.listdir(sub_path)
            if f.endswith(".md")
        ] if os.path.exists(sub_path) else []

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

    # Full case summary (AI or fallback)
    case_summary = generate_summary_for_section("Case Overview", all_section_text.strip(), use_ai=use_ai)
    report_md = report_md.replace("## 📋", "## 📝 Summary\n" + case_summary + "\n\n---\n## 📋")

    # Add disclaimer
    report_md += "## 🛑 Disclaimer\n"
    report_md += "This report was generated automatically using investigative data provided by the user. All content should be verified for accuracy before official submission.\n"

    # Save to file inside 4. Report
    report_folder = os.path.join(case_path, "4. Report")
    os.makedirs(report_folder, exist_ok=True)
    md_output_path = os.path.join(report_folder, f"Case_{case_id}_Report.md")
    with open(md_output_path, "w") as f:
        f.write(report_md)

    print(f"\n✅ Report generated successfully:")
    print(f"📄 {md_output_path}")


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
                api_key = os.getenv("OPENAI_API_KEY")
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

        elif choice == "99":
            print("👋 Exiting.")
            break
        else:
            print("❓ Invalid choice. Try again.")

if __name__ == "__main__":
    menu()
