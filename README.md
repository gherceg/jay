# Overview

This repository contains the server for managing an online game of Literature.
Users can create new games, or join existing games and play with friends. 

# Project Setup

### Using venv

The venv module is used to create a virtual environment, and comes prepackaged with Python versions >=3.3

### Create virtual environment

To create a virtual environment, in the project root directory run:

`python -m venv jay-env`

### Activate the virtual environment

You can activate the python environment by running the following command:
Mac OS / Linux

`source jay-env/bin/activate`

Windows

`jay-env\Scripts\activate`

You should see the name of your virtual environment in parenthesis on your terminal line e.g. (jay-env).

### Deactivate the virtual environment

To deactivate the virtual environment and use your original Python environment, simply type ‘deactivate’.

`deactivate`

### Install Dependencies
Once your virtual environment is setup and activated, install dependencies using pip:

`pip install -r requirements.txt`

### Run Server
From the root directory:

`uvicorn main:app --reload`

### Testing

pytest is used to handle testing.

Running `pytest` will search and run all tests found beneath the current directory.

Run `pytest /path/to/file` to run a specific test file
