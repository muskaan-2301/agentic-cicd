# agentic-cicd

Agentic AI for CI/CD pipelines on Google Cloud: predict build failures,
diagnose them with an LLM, and self-heal. (College project.)

This repo's `app/` is the **sample application** that the pipeline builds.
It is a small task-manager REST API with 47 tests, so we have something
realistic to build, break on purpose (fault injection) and learn from.

## Run locally

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
pytest -q                        # all tests should pass
flask --app app.main:create_app run --debug   # http://127.0.0.1:5000/health
```

## Layout

```
app/         Flask app (the thing being built)
tests/       pytest suite
telemetry/   CPU/RAM sampler (Day 2)
requirements.txt
```

Later days add: `functions/` (Cloud Run functions), `ml/`, `data/`, `eval/`.
