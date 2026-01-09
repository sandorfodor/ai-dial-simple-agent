FROM python:3.11
ADD . .
RUN pip install requests pydantic python-dotenv
CMD ["python", "./run.py"] 