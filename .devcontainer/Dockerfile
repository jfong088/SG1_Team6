#The base image for the container 
FROM python:3.12-slim 
 
# Keeps Python from generating .pyc files in the container 
ENV PYTHONDONTWRITEBYTECODE=1 
 
# Turns off buffering for easier container logging 
ENV PYTHONUNBUFFERED=1 

ARG USERNAME=com139-user
ARG USER_UID=1001
ARG USER_GID=$USER_UID

# Create the user
RUN apt-get update \
    && apt-get install -y --no-install-recommends sudo git \
    && groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME \
    && rm -rf /var/lib/apt/lists/* 

# ********************************************************
# * Anything else you want to do like clean up goes here *
# ********************************************************
# This snippet will save the bash history if we are not running with root user
RUN SNIPPET="export PROMPT_COMMAND='history -a' && export HISTFILE=/commandhistory/.bash_history" \
    && mkdir /commandhistory \
    && touch /commandhistory/.bash_history \
    && chown -R $USERNAME /commandhistory \
    && echo "$SNIPPET" >> "/home/$USERNAME/.bashrc"
    
# Copy python requirements to the docker container and install
# First the prerequisites for AIST++
# COPY .devcontainer/requirements.txt . 
# RUN python -m pip install -r requirements.txt 

# Then the project specific
COPY .devcontainer/requirements.txt . 
RUN python -m pip install -r requirements.txt
RUN sudo rm requirements.txt

ENV PATH="/home/${USERNAME}/.local/bin:${PATH}"

# [Optional] Set the default user. Omit if you want to keep the default as root.
USER $USERNAME
 
