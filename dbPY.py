import csv
import os
import shutil
import tkinter as tk
from tkinter import ttk, messagebox
import openpyxl
import json


MAIN_FILE = "database.csv"
BACKUP_FILE = "backup.csv"
TEMP_FILE = "temp.csv"
FIELD_NAMES = ["name", "surname", "phone_number", "date_of_birth"]
PK = "phone_number"
index = {}


def display_database_contents():
    print(f"Trying to show database from {MAIN_FILE}")
    file_list.delete(0, tk.END)
    try:
        with open(MAIN_FILE, "r", newline="") as f:
            reader = csv.reader(f, delimiter=";", quotechar='"')
            for row in reader:
                file_list.insert(tk.END, "   ".join(row))
    except FileNotFoundError:
        messagebox.showerror("Error", f"File {MAIN_FILE} not found.")

def create_database():
    with open(MAIN_FILE, "w", newline='') as f:
        writer = csv.DictWriter(f, delimiter=";", quotechar='"', fieldnames=FIELD_NAMES)
        writer.writeheader()
    messagebox.showinfo("Success", "Database created.")
    refresh_file_list()

def delete_database():
    try:
        os.remove(MAIN_FILE)
        messagebox.showinfo("Success", "Database deleted.")
        refresh_file_list()
        with open("index.json", 'w', newline='') as i:
            pass
        index = {}
    except FileNotFoundError:
        messagebox.showerror("Error", "Database file not found.")

def clear_database():
    with open(MAIN_FILE, "w", newline='') as f, open("index.json", 'w', newline='') as i:
        writer = csv.DictWriter(f, delimiter=";", quotechar='"', fieldnames=FIELD_NAMES)
        writer.writeheader()
        index = {}
    messagebox.showinfo("Success", "Database cleared.")

def create_backup():
    try:
        shutil.copy(MAIN_FILE, BACKUP_FILE)
        messagebox.showinfo("Success", "Backup created.")
    except FileNotFoundError:
        messagebox.showerror("Error", "Database file not found. Cannot create backup.")

def restore_backup():
    try:
        shutil.copy(BACKUP_FILE, MAIN_FILE)
        messagebox.showinfo("Success", "Database restored from backup.")
    except FileNotFoundError:
        messagebox.showerror("Error", "Backup file not found. Cannot restore database.")

def add_record(csv_string):
    if csv_string[2] in index:
        messagebox.showerror("Error", "Record with this primary key already exists.")
        return
    with open(MAIN_FILE, "a+", newline='', encoding="utf-8") as f:
        f.seek(0, 2)
        writer = csv.writer(f, delimiter=";", quotechar='"')
        position = f.tell()
        writer.writerow(csv_string)
        f.flush()
        index[csv_string[2]] = position
    print("NOT GUI")
    messagebox.showinfo("Success", "Record added successfully.")

def delete_record_by_field(field, value):
    found = False
    with open(MAIN_FILE, 'r+', newline='') as f, open(TEMP_FILE, 'w', newline='') as tf:
        reader = csv.DictReader(f, delimiter=";", quotechar='"', fieldnames=FIELD_NAMES)
        writer = csv.DictWriter(tf, delimiter=";", quotechar='"', fieldnames=FIELD_NAMES)
        for row in reader:
            if row[field] != value:
                writer.writerow(row)
            else:
                del index[row["phone_number"]]
                f.write("DELETED\n")
                found = True
    if found:
        os.replace(TEMP_FILE, MAIN_FILE)
        messagebox.showinfo("Success", f"Records matching {field} = {value} were deleted.")
    else:
        os.remove(TEMP_FILE)
        messagebox.showerror("Error", f"No records found with {field} = {value}.")

def search_record(field, value):
    results = []
    with open(MAIN_FILE, 'r', newline='', encoding='utf-8') as f:
        if field == PK:
            if value in index:
                f.seek(index[value]-1)
                reader = csv.DictReader(f, delimiter=";", quotechar='"', fieldnames=FIELD_NAMES)
                row = next(reader)
                print(row)
                return [row]
            else:
                return -1
        else:
            reader = csv.DictReader(f, delimiter=";", quotechar='"')
            for row in reader:
                print(row)
                if row[field] == value:
                    results.append(row)
            return results if results else -1

def update_record(pk_value, updated_values):
    found = False
    with open(MAIN_FILE, 'r', newline='') as f, open(TEMP_FILE, 'w', newline='') as tf:
        reader = csv.DictReader(f, delimiter=";", quotechar='"')
        writer = csv.DictWriter(tf, delimiter=";", quotechar='"', fieldnames=FIELD_NAMES)
        writer.writeheader()
        for row in reader:
            if row[PK] == pk_value:
                writer.writerow(updated_values)
                found = True
            else:
                writer.writerow(row)
    if found:
        os.replace(TEMP_FILE, MAIN_FILE)
        messagebox.showinfo("Success", "Record updated successfully.")
    else:
        os.remove(TEMP_FILE)
        messagebox.showerror("Error", f"No record found with {PK} = {pk_value}.")

def export_to_excel():
    try:
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Database"
        with open(MAIN_FILE, 'r', newline='') as f:
            reader = csv.reader(f, delimiter=";", quotechar='"')
            for row in reader:
                sheet.append(row)
        workbook.save("database.xlsx")
        messagebox.showinfo("Success", "Database exported to Excel.")
    except FileNotFoundError:
        messagebox.showerror("Error", "Database file not found. Cannot export to Excel.")

def refresh_file_list():
    files = [f for f in os.listdir(".") if os.path.isfile(f)]
    file_list.delete(0, tk.END)
    for file in files:
        file_list.insert(tk.END, file)


def add_record_gui():
    def save_record():
        name = entry_name.get()
        surname = entry_surname.get()
        phone = entry_phone.get()
        dob = entry_dob.get()
        if not name or not surname or not phone or not dob:
            messagebox.showerror("Error", "All fields must be filled.")
            return
        add_record([name, surname, phone, dob])
        add_record_window.destroy()

    add_record_window = tk.Toplevel()
    add_record_window.title("Add Record")
    tk.Label(add_record_window, text="Name").grid(row=0, column=0)
    tk.Label(add_record_window, text="Surname").grid(row=1, column=0)
    tk.Label(add_record_window, text="Phone").grid(row=2, column=0)
    tk.Label(add_record_window, text="Date of Birth").grid(row=3, column=0)

    entry_name = tk.Entry(add_record_window)
    entry_surname = tk.Entry(add_record_window)
    entry_phone = tk.Entry(add_record_window)
    entry_dob = tk.Entry(add_record_window)

    entry_name.grid(row=0, column=1)
    entry_surname.grid(row=1, column=1)
    entry_phone.grid(row=2, column=1)
    entry_dob.grid(row=3, column=1)

    tk.Button(add_record_window, text="Save", command=save_record).grid(row=4, column=0, columnspan=2)

def delete_record_gui():
    def perform_delete():
        field = field_entry.get()
        value = value_entry.get()
        if not field or not value:
            messagebox.showerror("Error", "Please provide both field and value.")
            return
        delete_record_by_field(field, value)
        delete_window.destroy()

    delete_window = tk.Toplevel()
    delete_window.title("Delete Record")
    ttk.Label(delete_window, text="Field").grid(row=0, column=0, padx=5, pady=5)
    field_entry = ttk.Entry(delete_window)
    field_entry.grid(row=0, column=1, padx=5, pady=5)
    ttk.Label(delete_window, text="Value").grid(row=1, column=0, padx=5, pady=5)
    value_entry = ttk.Entry(delete_window)
    value_entry.grid(row=1, column=1, padx=5, pady=5)
    ttk.Button(delete_window, text="Delete", command=perform_delete).grid(row=2, column=0, columnspan=2, pady=10)

def update_record_gui():
    def perform_update():
        pk_value = pk_entry.get()
        new_values = {
            FIELD_NAMES[0]: name_entry.get(),
            FIELD_NAMES[1]: surname_entry.get(),
            FIELD_NAMES[2]: phone_entry.get(),
            FIELD_NAMES[3]: dob_entry.get()
        }
        if not pk_value or any(not v for v in new_values.values()):
            messagebox.showerror("Error", "Please fill in all fields.")
            return
        update_record(pk_value, new_values)
        update_window.destroy()

    update_window = tk.Toplevel()
    update_window.title("Update Record")
    ttk.Label(update_window, text="Primary Key (Phone Number)").grid(row=0, column=0, padx=5, pady=5)
    pk_entry = ttk.Entry(update_window)
    pk_entry.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(update_window, text="Name").grid(row=1, column=0, padx=5, pady=5)
    name_entry = ttk.Entry(update_window)
    name_entry.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(update_window, text="Surname").grid(row=2, column=0, padx=5, pady=5)
    surname_entry = ttk.Entry(update_window)
    surname_entry.grid(row=2, column=1, padx=5, pady=5)

    ttk.Label(update_window, text="Phone Number").grid(row=3, column=0, padx=5, pady=5)
    phone_entry = ttk.Entry(update_window)
    phone_entry.grid(row=3, column=1, padx=5, pady=5)

    ttk.Label(update_window, text="Date of Birth").grid(row=4, column=0, padx=5, pady=5)
    dob_entry = ttk.Entry(update_window)
    dob_entry.grid(row=4, column=1, padx=5, pady=5)

    ttk.Button(update_window, text="Update", command=perform_update).grid(row=5, column=0, columnspan=2, pady=10)


def search_record_gui():
    def perform_search():
        field = field_entry.get()
        value = value_entry.get()
        if not field or not value:
            messagebox.showerror("Error", "Please provide both field and value.")
            return

        results = search_record(field, value)
        if results == -1:
            messagebox.showinfo("Search Results", "No records found.")
        else:
            result_text.delete(1.0, tk.END)
            for record in (results if isinstance(results, list) else [results]):
                result_text.insert(tk.END, "  ".join(record.values()) + "\n")

    search_window = tk.Toplevel()
    search_window.title("Search Record")
    search_window.geometry("400x300")

    ttk.Label(search_window, text="Field").grid(row=0, column=0, padx=5, pady=5)
    field_entry = ttk.Entry(search_window)
    field_entry.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(search_window, text="Value").grid(row=1, column=0, padx=5, pady=5)
    value_entry = ttk.Entry(search_window)
    value_entry.grid(row=1, column=1, padx=5, pady=5)

    ttk.Button(search_window, text="Search", command=perform_search).grid(row=2, column=0, columnspan=2, pady=10)

    ttk.Label(search_window, text="Results").grid(row=3, column=0, columnspan=2, pady=5)
    result_text = tk.Text(search_window, width=50, height=10, wrap="word")
    result_text.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

def gui_main():
    def quitt():
        with open("index.json", 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=4)
            f.flush()
        root.quit()

    root = tk.Tk()
    root.title("File Database GUI")

    frame_center = ttk.Frame(root, padding="5")
    frame_center.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    ttk.Label(frame_center, text="Project Files", font=("Arial", 14)).pack(pady=5)
    global file_list
    file_list = tk.Listbox(frame_center, width=50, height=25, selectmode=tk.SINGLE)
    file_list.pack(pady=5, fill=tk.BOTH, expand=True)

    frame_right = ttk.Frame(root, padding="5")
    frame_right.pack(side=tk.RIGHT, fill=tk.Y)

    ttk.Label(frame_right, text="Database Operations", font=("Arial", 14)).pack(pady=5)
    ttk.Button(frame_right, text="Open Database", command=display_database_contents ).pack(fill=tk.X, pady=2)
    ttk.Button(frame_right, text="Create Database", command=create_database).pack(fill=tk.X, pady=2)
    ttk.Button(frame_right, text="Add Record", command=lambda: add_record_gui()).pack(fill=tk.X, pady=2)
    ttk.Button(frame_right, text="Search Record", command=lambda: search_record_gui()).pack(fill=tk.X, pady=2)
    ttk.Button(frame_right, text="Delete Record", command=lambda: delete_record_gui()).pack(fill=tk.X, pady=2)
    ttk.Button(frame_right, text="Update Record", command=lambda: update_record_gui()).pack(fill=tk.X, pady=2)
    ttk.Button(frame_right, text="Clear Database", command=clear_database).pack(fill=tk.X, pady=2)
    ttk.Button(frame_right, text="Create Backup", command=create_backup).pack(fill=tk.X, pady=2)
    ttk.Button(frame_right, text="Restore Backup", command=restore_backup).pack(fill=tk.X, pady=2)
    ttk.Button(frame_right, text="Export to Excel", command=export_to_excel).pack(fill=tk.X, pady=2)
    ttk.Button(frame_right, text="Delete Database", command=delete_database).pack(fill=tk.X, pady=2)
    ttk.Button(frame_right, text="Exit", command=quitt).pack(fill=tk.X, pady=2)

    root.mainloop()


if __name__ == "__main__":
    if not os.path.exists("index.json"):
        with open("index.json", "a") as file:
            pass
    if os.path.getsize("index.json") != 0:
        with open ("index.json", 'r', encoding='utf-8') as f:
            index = json.load(f)
    gui_main()

