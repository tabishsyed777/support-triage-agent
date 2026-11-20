DESCRIPTION = 'Route customer support tickets and recommend a response priority.'

import argparse
import json
from pathlib import Path

from .agent import AgentError, controller_for, run
from .policy import POLICY, assess, validate


def main():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("case", type=Path, help="Path to the case JSON file")
    parser.add_argument("--model", help="OpenAI model that supports JSON mode")
    args = parser.parse_args()

    def load_case():
        return validate(json.loads(args.case.read_text(encoding="utf-8")))

    try:
        report = run(load_case, POLICY, assess, controller_for(args.model))
    except (OSError, ValueError, AgentError) as exc:
        parser.exit(1, f"Error: {exc}\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
