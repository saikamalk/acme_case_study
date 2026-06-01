FROM python:3.11
WORKDIR /app
COPY mcp_server/requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8100
CMD ["uvicorn", "mcp_server.server:app", "--host", "0.0.0.0", "--port", "8100"]
