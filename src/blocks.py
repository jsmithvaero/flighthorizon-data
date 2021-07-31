from src.mathUtils import PAC

def blockSplitTimeIndexedData(data):
	sorted_data = sorted(data, key=lambda d : d[0])
	blocks = [[sorted_data[0]]]
	data_length = len(data)
	for j in range(1, data_length):
		
		if ((sorted_data[j][0] - \
			 sorted_data[j - 1][0]).total_seconds() / 60) > 10:

			blocks.append([sorted_data[j]])
		else:
			blocks[-1].append(sorted_data[j])
	return blocks

def radarTruthBlocks(radar_data, truth_data):

	BLOCKS = []

	for radar_file_name in radar_data:

		radar_file_blocks = blockSplitTimeIndexedData(radar_data[radar_file_name])
		truth_file_blocks = []

		for radar_block in radar_file_blocks:

			mintime = radar_block[ 0][0]
			maxtime = radar_block[-1][0]

			truth_block = [
				(file, time, lat, lon, alt) for
				(file, time, lat, lon, alt) in truth_data
				if ((mintime <= time) and (time <= maxtime))
			]

			BLOCKS.append((radar_block, truth_block))

	return BLOCKS


def flattenedRadarTruthBlock(radar_truth_block):

	(radar_block, truth_block) = radar_truth_block

	flattened_block = [
		(time, conf, lat, lon, alt, dist, PAC(time, 
			                                  lat, 
			                                  lon, 
			                                  alt, 
			                                  truth_block))
	    for (time, conf, lat, lon, alt, dist)
	    in radar_block
	]

	return flattened_block


def flattenedRadarTruthBlocks(BLOCKS):

	return [flattenedRadarTruthBlock(B) for B in BLOCKS]