.PHONY: tables figures

all: ; python3 runner.py demo-data/

clean: 
	- rm *.png
	- rm -rf 2021-*