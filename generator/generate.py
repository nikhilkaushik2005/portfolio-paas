import json
import os
from jinja2 import Template

# 1. Read the JSON file sent from the frontend
with open('student_data.json', 'r') as f:
    data = json.load(f)

# 2. Read your beautiful new HTML template
with open('template.html', 'r', encoding='utf-8') as f:
    template = Template(f.read())

# 3. THE MAGIC FIX: The double asterisk (**data) tells Python to 
# unpack EVERY piece of data in the JSON and hand it to Jinja.
rendered_html = template.render(**data)

# 4. Save the final HTML to the dist folder for AWS
os.makedirs('dist', exist_ok=True)
with open('dist/index.html', 'w', encoding='utf-8') as f:
    f.write(rendered_html)

print("Website successfully generated!")