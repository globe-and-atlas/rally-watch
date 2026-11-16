.PHONY: test build verify
test:
	node watchface/settings.test.js
	python3 -m pytest tests/ -q
build:
	python3 execution/build.py
verify:
	python3 execution/verify.py
