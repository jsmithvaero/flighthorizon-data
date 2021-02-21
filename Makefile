.PHONY: tables figures

clean: ; - rm *.png

tables:
	echo "----------- RADAR -----------"
	python3 tables/numberTracksRadar.py
	echo "----------- MavLink -----------"
	python3 tables/numberTracksMavlink.py
	echo "----------- ADSB -----------"
	python3 tables/numberTracksADSB.py

figures:
	python3 figures/radarFigs.py ../build/logs/alaska/