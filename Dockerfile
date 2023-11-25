FROM python:3.10

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libsoup2.4-dev \
    libjavascriptcoregtk-4.0-dev \
    libgtk-3-dev \
    libwebkit2gtk-4.0-dev

COPY . /app

RUN pip install --upgrade pip wheel setuptools
RUN pip install --no-cache-dir -r  requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
