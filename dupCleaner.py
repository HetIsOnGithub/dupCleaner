import os
import hashlib
import questionary
import time
from collections import defaultdict
from tqdm import tqdm
from pyfiglet import Figlet

def type_out(text, delay=0.005):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()


fig = Figlet(font='slant')  
ascii_banner = fig.renderText('Dup Cleaner')
type_out(ascii_banner)
type_out('By Het\n')
print('-' * 60)

def calculate_file_hash(file_path):

    hash_obj = hashlib.sha256()
    try:
        with open(file_path, "rb") as file:
            while chunk := file.read(8192):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except Exception:
        return None 

def get_scan_type():
    choice = questionary.select(
        "Choose scan type:",
        choices=[
            "🔍 Full PC Scan (All Disk Included)",
            "📂 Specific Folder Scan (Select Folder)"
        ]).ask()

    if choice == "🔍 Full PC Scan (All Disk Included)":
        drives = ["C:\\", "D:\\", "E:\\", "F:\\", "G:\\"] 
        return [d for d in drives if os.path.exists(d)]

    elif choice == "📂 Specific Folder Scan (Select Folder)":
        custom_path = questionary.path("Enter PATH to scan:").ask()
        if os.path.exists(custom_path):
            return [custom_path]
        else:
            print("❌ Invalid path. Try again.")
            return get_scan_type()
    else:
        print("❌ Invalid choice.")
        return get_scan_type()

def find_all_files(paths):

    all_files = []
    for root_path in paths:
        for root, _, files in os.walk(root_path):
            for file in files:
                full_path = os.path.join(root, file)
                all_files.append(full_path)
    return all_files

def detect_duplicates(files):

    hash_map = defaultdict(list)
    print("\n🔎 Scanning files and calculating content hashes...\n")
    for file in tqdm(files, desc="Progress", unit="file"):
        file_hash = calculate_file_hash(file)
        if file_hash:
            hash_map[file_hash].append(file)

    
    duplicates = {h: paths for h, paths in hash_map.items() if len(paths) > 1}
    return duplicates

def show_progress_bar(index, total, filename):
    percent = int((index / total) * 100)
    bar = "█" * (percent // 10) + "▒" * (10 - percent // 10)
    print(f"[{bar}] {percent}% - {filename}")

def preview_duplicates(dupes):
    if not dupes:
        print("\n✅ No duplicate files found.")
        return

    print("\n📁 Duplicate Files Found:\n")
    for i, (hash_val, paths) in enumerate(dupes.items(), 1):
        print(f"🔁 Duplicate Group {i}:")
        for p in paths:
            print(f"   {p}")
        print()

    delete_choice = questionary.confirm("Do you want to delete duplicates (keep only one file from each group)?").ask()

    if delete_choice:
        delete_duplicates(dupes)

def delete_duplicates(duplicates):
    print("\n⚠️ Deleting duplicates...\n")
    total_groups = len(duplicates)
    for idx, (hash_val, paths) in enumerate(duplicates.items(), 1):
        original = paths[0]  
        duplicates_to_delete = paths[1:] 

        for file_path in duplicates_to_delete:
            try:
                os.remove(file_path)
                print(f"🗑️ Deleted: {file_path}")
            except Exception as e:
                print(f"❌ Failed to delete {file_path}: {e}")
        show_progress_bar(idx, total_groups, f"Group {idx} done")

    print("\n✅ All selected duplicates deleted.")


if __name__ == "__main__":
    scan_paths = get_scan_type()
    all_files = find_all_files(scan_paths)
    duplicates = detect_duplicates(all_files)
    preview_duplicates(duplicates)
