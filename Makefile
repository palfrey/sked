requirements.txt: requirements.in
	./uv pip compile --python-version 3.12.2 --no-strip-extras requirements.in -o requirements.txt

.venv/bin/activate:
	./uv venv

.PHONY: sync
sync: requirements.txt .venv/bin/activate
	./uv pip sync requirements.txt

.PHONY: pre-commit
pre-commit: sync
	./uv run pre-commit run -a