#Dockerrfile for watchdogits

                           ### Build Stage ###
ARG PYTHON_VERSION=3.12.2
FROM python:${PYTHON_VERSION}-slim as build

# Prevents Python from writing pyc files.
# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

#Setting the working directory 
WORKDIR /watchdogit

# Install system dependencies, including git
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    gcc \
    libc-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

#Create a virtual environment in the container
RUN python3 -m venv /opt/venv

#Copying the requirements first
COPY requirements.txt .

#Install the dependencies
RUN /opt/venv/bin/pip install pip --upgrade \
    && /opt/venv/bin/pip install -r requirements.txt 

#Copy the rest of the project and run through entry point
COPY . .


                            ### Final Stage ###
FROM python:${PYTHON_VERSION}-slim as final

# Prevents Python from writing pyc files.
# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Setting the working directory 
WORKDIR /watchdogit

# Install git in the final stage
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment from the build stage
COPY --from=build /opt/venv /opt/venv

# Copy the application files from the build stage
COPY --from=build /watchdogit /watchdogit

RUN chmod +x /watchdogit/entrypoint.sh

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Change ownership of the database file and directory to the non-privileged user
RUN chown -R appuser:appuser db.sqlite3 /watchdogit

# Switch to the non-privileged user to run the application.
USER appuser

# Run the application.
CMD ["/watchdogit/entrypoint.sh"]
