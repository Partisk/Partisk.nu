FROM python:3.6
WORKDIR /app

# Prevent caching git repo
ADD https://api.github.com/repos/Partisk/Partisk.nu/git/refs/heads/master version.json
RUN git clone https://github.com/Partisk/Partisk.nu.git
RUN mv Partisk.nu/* .
ADD . /app
ENV PYTHONUNBUFFERED 1

ENV DJANGO_SETTINGS_MODULE app.settings.prod
ENV DATABASE_HOST db
ENV ADMIN_ENABLED False
ENV COMPRESS False
ENV DEBUG True

RUN pip install --trusted-host pypi.python.org -r python_requirements.txt
ENV NAME Partisk
