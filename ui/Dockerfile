FROM python:3.11-slim
WORKDIR /app
COPY ../requirements.txt .
RUN pip install pandas requests streamlit
COPY .. .
EXPOSE 8501
CMD ["streamlit", "run", "ui/app.py", "--server.address=0.0.0.0", "--server.port", "8501"]