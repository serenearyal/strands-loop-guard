# Contributing

Bug reports, questions and pull requests are welcome.

## Report a bug

Open an issue at https://github.com/serenearyal/strands-loop-guard/issues.
Give the `strands-agents` version, the `strands-loop-guard` version, and the smallest agent setup that shows the problem.

## Make a change

1. Fork the repository and create a branch from `main`.
2. Install the tools: `pip install hatch`.
3. Make the change and add a test for it.
   Tests drive a real `strands.Agent` with the scripted model in `tests/scripted_model.py`.
4. Run all checks: `hatch run prepare` (format, lint, type check, tests).
5. Open a pull request with a short description of the change and why it is needed.
   Use a conventional commit title, for example `fix: count a split batch once`.

## Security

Do not open a public issue for a security problem.
Use the private vulnerability report at https://github.com/serenearyal/strands-loop-guard/security/advisories/new.

## License

By contributing, you agree that your contributions are licensed under the Apache License 2.0 (see `LICENSE`).
