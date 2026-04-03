FROM python:3.9-slim
RUN pip install jinja2
WORKDIR /app
COPY . .
CMD ["python", "generate.py"]