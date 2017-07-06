.PHONY: all init run clean


all: run


build/env:
	@rm -rf build/env
	@mkdir -p build/env
	@virtualenv -p python3 build/env
	@build/env/bin/python3 setup.py install


init: build/env *
	@build/env/bin/python3 -m telegramschoolbot init


initdb: build/env *
	@build/env/bin/python3 -m telegramschoolbot initdb


run: build/env *
	@build/env/bin/python3 -m telegramschoolbot run


clean:
	@rm -rf build
