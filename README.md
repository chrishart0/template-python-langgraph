# Template Python FastAPI Llama-Index and LangChain Repo
[![CI](https://github.com/chrishart0/template-python-langgraph/actions/workflows/ci.yml/badge.svg)](https://github.com/chrishart0/template-python-langgraph/actions/workflows/ci.yml)

## Instructions

Follow these steps to set up the project:

1. **Set up Python version with pyenv:**
   *Install pyenv if you don't have it: <https://github.com/pyenv/pyenv>*

   ```bash
   # Install specific Python version
   pyenv install 3.12
   python --version 
   echo "Please make sure you really got python 3.12, if you don't you may need to check your pyenv installation then delete your .venv and try again."
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment:**
   - On macOS and Linux:
     ```bash
     source .venv/bin/activate
     ```
   - On Windows:
     ```
     .venv\Scripts\activate
     ```

4. **Install dependencies with Poetry:**
   Check if you have poetry by running `poetry --version`

   If you don't have poetry, go install it: <https://python-poetry.org/docs/>

   ```sh
   poetry install
   ```

5. **Setup your .env**
Copy the `.env.example` file to `.env` and update the values:

```bash
cp .env.example .env
```

6. **Optional: Setup pre-commit hook**
```bash
pre-commit install
```

### Setup Tracing
There are several tracing options built in, you can choose which one to use or compare them side-by-side. Phoenix will just work one you spin the container up, LangFuse will require more setup and configuration throughout the project where you want it tracing.

#### Spin up Phoenix and LangFuse tracing servers

If you don't have docker installed, here is the setup guide for Ubuntu: <https://docs.docker.com/engine/install/ubuntu/>
```bash
docker compose -f docker-compose.yml -f docker-compose.langfuse.yml up -d
```

View your traces at: <http://localhost:6006>

##### Langfuse setup

**1. Create a new organization and project in Langfuse**
Head to <http://localhost:3000> and create a new user, organization, and project.

**2. Add the secrets LangFuse shows you to your .env file Langfuse**
```bash
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_HOST=http://localhost:3000
```

## Run the langchain or llama index example scripts

```bash
python3 template_langgraph_project/examples/simple-langgraph-example.py
```


## Testing

This project includes code coverage requirements to ensure the quality of the code. To measure code coverage, we use `pytest-cov`.

### Running Tests with Code Coverage

To run the tests and measure code coverage, use the following command:
```sh
poetry run pytest --cov --cov-report=term-missing
```

## Linting

```bash
poetry run black .
poetry run flake8 .
```

## Environment Variables

This project uses environment variables to manage sensitive information and configuration settings. Follow these steps to set up and use the environment variables:

1. **Create a `.env` file:**
   Create a `.env` file in the root of the repository with the following content:
   ```sh
   API_KEY=your_api_key_here
   DATABASE_URL=your_database_url_here
   ```

## Updating Your Repository

If you have created a repository from this template and want to update it with the latest changes from the template, follow these steps:

1. **Add the template repository as a remote:**
   ```sh
   git remote add template https://github.com/chrishart0/template-python-langgraph-starter.git
   ```

2. **Fetch the latest changes from the template:**
   ```sh
   git fetch template
   ```

3. **Merge the changes into your main branch:**
   ```sh
   git checkout main
   git merge template/main
   ```

4. **Resolve any merge conflicts:**
   If there are any merge conflicts, resolve them in your code editor and commit the changes.

5. **Push the updates to your repository:**
   ```sh
   git push origin main
   ```

By following these steps, you can keep your project up-to-date with the latest improvements and features from the template repository.
