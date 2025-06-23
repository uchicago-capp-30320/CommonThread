## Backend Setup

1. **Install UV**: If you haven't already, install UV
2. **Sync the Environment**: After installing UV, you need to sync the environment. This will set up the necessary configurations and dependencies for your project. Run the following command from this directory (the one with uv.lock):
```bash
$ uv sync
```
3. **To add a new package**: If you need to add a new package, you can do so by running:
```bash
$ uv add <package_name>
``` 
4. **Start your virtual environment** [uv venv documentation](https://docs.astral.sh/uv/pip/environments/#creating-a-virtual-environment)

5. Start the local development server by running the following command:
```bash
$ python manage.py runserver
```

6. You can also start the machine learning queue by running:
```bash
$ python ct_application/cloud/consumer_service.py
```

7. In order to run all tests for the backend, you can run:

```bash
$ pytest
```

From the current directory, or you can run specific tests by pointing at the specific filepath:test_example.py