import json
import os
from jinja2 import Template 

# Read the data that will be passed in
with open('student_data.json', 'r') as f:
    data = json.load(f)

# Read our HTML skeleton
with open('template.html', 'r') as f:
    template = Template(f.read())

# Inject the data into the HTML
output = template.render(name=data['name'], bio=data['bio'], skills=data['skills'])

# Save the finished product
os.makedirs('dist', exist_ok=True)
with open('dist/index.html', 'w') as f:
    f.write(output)