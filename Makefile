.PHONY: tables figures

clean: ; - rm *.png

deps:
	sudo apt-get install -y libproj-dev
	pip3 install -r requirements.txt

# In order for this to work you'll need to change the
# argument to point to somewhere where you have logs.
tables:
	echo "----------- RADAR -----------"
	python3 tables/numberTracksRadar.py "../build/logs/alaska/"
	echo "----------- MavLink -----------"
	python3 tables/numberTracksMavlink.py "../build/logs/alaska/"
	echo "----------- ADSB -----------"
	python3 tables/numberTracksADSB.py "../build/logs/alaska/"

figures:
	python3 figures/radarFigs.py demo-data/