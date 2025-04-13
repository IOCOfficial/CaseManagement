import os
import shutil
from datetime import datetime

BASE_DIR = os.path.expanduser("~/Investigations")

def create_case(case_id, status):
    case_folder = os.path.join(BASE_DIR, f"Case_{case_id}")
    if os.path.exists(case_folder):
        print(f"❌ Case {case_id} already exists.")
        return
    os.makedirs(os.path.join(case_folder, "evidence"))
    os.makedirs(os.path.join(case_folder, "reports"))
    with open(os.path.join(case_folder, "notes.txt"), "w") as f:
        f.write(f"Case ID: {case_id}\nStatus: {status}\nCreated: {datetime.now()}\n")
    print(f"✅ Case {case_id} created successfully.")

def list_cases():
    if not os.path.exists(BASE_DIR):
        print("📁 No cases found.")
        return
    for folder in os.listdir(BASE_DIR):
        print(f"- {folder}")

def view_case(case_id):
    case_folder = os.path.join(BASE_DIR, f"Case_{case_id}")
    notes_file = os.path.join(case_folder, "notes.txt")
    if not os.path.exists(notes_file):
        print(f"❌ Case {case_id} not found.")
        return
    with open(notes_file, "r") as f:
        print(f.read())

def update_status(case_id, new_status):
    case_folder = os.path.join(BASE_DIR, f"Case_{case_id}")
    notes_file = os.path.join(case_folder, "notes.txt")
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
        print("\n--- Investigation Case Manager ---")
        print("1. Create Case")
        print("2. List Cases")
        print("3. View Case")
        print("4. Update Case Status")
        print("5. Delete Case")
        print("6. Exit")
        choice = input("Enter choice: ")

        if choice == "1":
            case_id = input("Enter Case ID: ")
            status = input("Enter Case Status (e.g., Open, Closed): ")
            create_case(case_id, status)
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
