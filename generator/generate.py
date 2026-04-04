import json
import os
from jinja2 import Template

# 1. Read the JSON file
with open('student_data.json', 'r') as f:
    data = json.load(f)

# 2. THE UPGRADE: Find out which template they picked (default to 1 if missing)
template_choice = data.get('template_id', '1')
template_filename = f"template_{template_choice}.html"

# 3. Read the specific template file they asked for
with open(template_filename, 'r', encoding='utf-8') as f:
    template = Template(f.read())

# 4. Render and Save
rendered_html = template.render(**data)

os.makedirs('dist', exist_ok=True)
with open('dist/index.html', 'w', encoding='utf-8') as f:
    f.write(rendered_html)

print(f"Successfully generated using {template_filename}!")