FROM python:3
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y texlive-latex-extra texlive-fonts-recommended dvipng cm-super
