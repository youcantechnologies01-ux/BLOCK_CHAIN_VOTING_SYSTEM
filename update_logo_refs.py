import os
import glob

directory = r'e:\varun projects\you_can_tech-voting\templates'

for filepath in glob.glob(os.path.join(directory, '*.html')):
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
    
    new_content = content.replace('logo.svg', 'logo.png')
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(new_content)
        print(f"Updated {filepath}")
