# Support Triage Agent

Route customer support tickets and recommend a response priority.

The controller chooses tools in a bounded loop. It loads a case and a decision
policy, runs the assessment, and returns a JSON decision with its tool trace.
The policy code evaluates the case and the controller decides which tool to
call next. The CLI produces recommendations for human review.

## Run the example

Requires Python 3.11 or later. Run from the repository root.

```sh
python -m support_triage_agent examples/case.json
```

The default controller runs locally with the Python standard library.
To try model-directed tool selection, set `OPENAI_API_KEY` in your
environment and add `--model gpt-4.1-mini`. Model mode sends the case,
policy, and tool results to OpenAI. Use sample or approved data.

## Decision rules

Route billing to accounts, access to identity, and product to product support. Other categories go to general support. A workaround keeps priority normal. Without a workaround, priority is elevated, or urgent for 10 or more affected users.

## Tests

```sh
python -m unittest discover -s tests -p 'test_unit_*.py' -v
python -m unittest discover -s tests -p 'test_integration_*.py' -v
```

Unit tests cover tool prerequisites, recovery, step limits, model response
handling, and policy decisions. Integration tests invoke the CLI in a
subprocess and check the JSON report, invalid input, and missing API key.
GitHub Actions runs both suites on Python 3.11, 3.12, and 3.13.
