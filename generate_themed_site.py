import json
import os
import shutil
from pathlib import Path
import html

# --- SCRIPT CONFIGURATION ---
RCLONE_SERVE_URL = "https://a.111477.xyz"
# Points to the plain text JSON file
JSON_INPUT_FILE = "files.json"
OUTPUT_DIR = "static_site"
# --- END CONFIGURATION ---


def create_directory_listing_page(current_path, items):
    """Creates a browsable index.html for a directory with the new dark theme."""
    folders = sorted([item for item in items if item['IsDir']], key=lambda x: x['Name'])
    files = sorted([item for item in items if not item['IsDir']], key=lambda x: x['Name'])
    safe_current_path = html.escape(str(current_path))

    table_rows = ''
    if current_path != Path("."):
        table_rows += '<tr><td><a href="../">Parent Directory</a></td><td>-</td></tr>'
    for folder in folders:
        folder_name_safe = html.escape(folder["Name"])
        table_rows += f'<tr><td><a href="{folder_name_safe}/">{folder_name_safe}/</a></td><td class="filesize">-1</td></tr>'
    for file in files:
        file_name_safe = html.escape(file["Name"])
        # MODIFIED: The href now points directly to the rclone serve URL for the file.
        direct_url = f"{RCLONE_SERVE_URL.rstrip('/')}/{html.escape(file['Path'])}"
        table_rows += f'<tr><td><a href="{direct_url}">{file_name_safe}</a></td><td class="filesize">{file["Size"]}</td></tr>'

    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8"><title>Directory listing of /{safe_current_path}</title>
    <style>body{{font-family:monospace;padding:20px;background:#121212;color:#ffffff;}}h1{{margin-bottom:20px;}}a{{text-decoration:none;color:#4da6ff;}}input{{margin-bottom:10px;padding:5px;width:100%;box-sizing:border-box;background:#1e1e1e;border:1px solid #333;color:#ffffff;border-radius:4px;}}table{{width:100%;border-collapse:collapse;}}th,td{{text-align:left;padding:8px;border-bottom:1px solid #2a2a2a;}}th{{background:#1e1e1e;cursor:pointer;}}tr:hover td{{background-color:#2c2c2c;}}</style>
    <script>
        function formatSize(bytes){{if(bytes<0)return"-";if(bytes===0)return"0 B";const sizes=["B","KB","MB","GB","TB"];const i=Math.floor(Math.log(bytes)/Math.log(1024));return parseFloat((bytes/Math.pow(1024,i)).toFixed(2))+" "+sizes[i]}}
        function sortTable(n,isNumeric){{let table=document.getElementById("fileTable");let rows=Array.from(table.rows).slice(1);let asc=table.dataset.sortOrder!=="asc";table.dataset.sortOrder=asc?"asc":"desc";let ascVal=asc?1:-1;rows.sort((a,b)=>{{let x=a.cells[n].getAttribute('data-sort')||a.cells[n].textContent.trim().toLowerCase();let y=b.cells[n].getAttribute('data-sort')||b.cells[n].textContent.trim().toLowerCase();if(isNumeric){{return(parseFloat(x)-parseFloat(y))*ascVal}}return x.localeCompare(y)*ascVal}});rows.forEach(row=>table.appendChild(row))}}
        function filterTable(){{let input=document.getElementById("search").value.toLowerCase();document.querySelectorAll("#fileTable tr").forEach((row,index)=>{{if(index===0||row.classList.contains('parent-dir'))return;let nameCell=row.cells[0].textContent.toLowerCase();row.style.display=nameCell.includes(input)?"":"none"}})}};
        window.onload=function(){{document.querySelectorAll(".filesize").forEach(function(td){{let size=parseInt(td.textContent,10);td.setAttribute('data-sort',size);td.textContent=formatSize(size)}});const parentRow=Array.from(document.querySelectorAll("#fileTable tr td a")).find(a=>a.textContent==="Parent Directory");if(parentRow)parentRow.closest('tr').classList.add('parent-dir')}};
    </script>
</head>
<body>
    <h1>Index of /{safe_current_path}</h1>
    <input type="text" id="search" onkeyup="filterTable()" placeholder="Search files and folders...">
    <table id="fileTable"><thead><tr><th onclick="sortTable(0, false)">Name</th><th onclick="sortTable(1, true)">Size</th></tr></thead><tbody>{table_rows}</tbody></table>
</body>
</html>"""
    output_path = Path(OUTPUT_DIR) / current_path / "index.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(html_template)


def main():
    """Main execution function."""
    print("Starting themed site generation...")
    try:
        # Uses the standard 'open' to read the plain text JSON file
        with open(JSON_INPUT_FILE, 'r', encoding='utf-8') as f:
            all_items = json.load(f)
    except (IOError, FileNotFoundError, json.JSONDecodeError):
        print(f"Error: {JSON_INPUT_FILE} is missing or invalid. Please run 'rclone lsjson' command first.")
        return

    dir_tree = {}
    for item in all_items:
        p = Path(item['Path'])
        parent_dir = str(p.parent)
        if parent_dir not in dir_tree: dir_tree[parent_dir] = []
        dir_tree[parent_dir].append(item)

    print(f"Generating {len(dir_tree)} directory listing pages...")
    for dir_path, items_in_dir in dir_tree.items():
        create_directory_listing_page(Path(dir_path), items_in_dir)

    print(f"\n✅ Site generation complete in the '{OUTPUT_DIR}' directory.")

    print("Zipping the output directory...")
    shutil.make_archive(OUTPUT_DIR, 'zip', OUTPUT_DIR)
    print(f"✅ Successfully created zip file: {OUTPUT_DIR}.zip")


if __name__ == "__main__":
    main()