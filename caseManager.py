import os
import shutil
from datetime import datetime
from tabulate import tabulate

BASE_DIR = os.path.expanduser("~/Investigations")

SUBFOLDERS = [
    "0. Introduction",
    "1. Blockchain Analysis",
    "2. OSINT",
    "3. Evidence",
    "4. Report",
    "99. Tasks"
]

def create_case(case_id, status, description):
    case_folder = os.path.join(BASE_DIR, f"Case_{case_id}")
    if os.path.exists(case_folder):
        print(f"❌ Case {case_id} already exists.")
        return
    os.makedirs(case_folder)
    for sub in SUBFOLDERS:
        os.makedirs(os.path.join(case_folder, sub))
    with open(os.path.join(case_folder, "notes.txt"), "w") as f:
        f.write(f"Case ID: {case_id}\nStatus: {status}\nDescription: {description}\nCreated: {datetime.now()}\n")
    print(f"✅ Case {case_id} created successfully.")

def list_cases():
    if not os.path.exists(BASE_DIR):
        print("📁 No cases found.")
        return
    table = []
    for folder in os.listdir(BASE_DIR):
        case_path = os.path.join(BASE_DIR, folder)
        notes_file = os.path.join(case_path, "notes.txt")
        if os.path.exists(notes_file):
            with open(notes_file, "r") as f:
                lines = f.readlines()
                status = next((line.split(":")[1].strip() for line in lines if line.startswith("Status:")), "")
                description = next((line.split(":")[1].strip() for line in lines if line.startswith("Description:")), "")
                table.append([folder.replace("Case_", ""), status, description])
    print(tabulate(table, headers=["Case ID", "Status", "Description"], tablefmt="fancy_grid"))

def view_case(case_id):
    notes_file = os.path.join(BASE_DIR, f"Case_{case_id}", "notes.txt")
    if not os.path.exists(notes_file):
        print(f"❌ Case {case_id} not found.")
        return
    with open(notes_file, "r") as f:
        print(f.read())

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

def delete_case(case_id):
    case_folder = os.path.join(BASE_DIR, f"Case_{case_id}")
    if os.path.exists(case_folder):
        confirm = input(f"⚠️ Are you sure you want to delete Case {case_id}? (yes/no): ")
        if confirm.lower() == "yes":
            shutil.rmtree(case_folder)
            print(f"🗑️ Case {case_id} deleted.")
    else:
        print(f"❌ Case {case_id} not found.")

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
            ["6", "Exit"]
        ], headers=["Option", "Action"], tablefmt="grid"))

        choice = input("Enter choice: ")

        if choice == "1":
            case_id = input("Enter Case ID: ")
            status = input("Enter Case Status (e.g., Open, Closed): ")
            description = input("Enter Case Description: ")
            create_case(case_id, status, description)
        elif choice == "2":
            list_cases()
        elif choice == "3":
            case_id = input("Enter Case ID to view: ")
            view_case(case_id)
        elif choice == "4":
            case_id = input("Enter Case ID to update: ")
            new_status = input("Enter new status: ")
            update_status(case_id, new_status)
        elif choice == "5":
            case_id = input("Enter Case ID to delete: ")
            delete_case(case_id)
        elif choice == "6":
            print("👋 Exiting.")
            break
        else:
            print("❓ Invalid choice. Try again.")

if __name__ == "__main__":
    menu()
