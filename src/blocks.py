from src.mathUtils import PAC

def blockSplitTimeIndexedData(data):
	sorted_data = sorted(data, key=lambda d : d.stamp)
	blocks = [[sorted_data[0]]]
	data_length = len(data)
	for j in range(1, data_length):
		
		if ((sorted_data[j    ].stamp - \
			 sorted_data[j - 1].stamp).total_seconds() / 60) > 10:

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

			mintime = radar_block[ 0].stamp
			maxtime = radar_block[-1].stamp

			truth_block = [
				p for p in truth_data
				if ((mintime <= p.stamp) and (p.stamp <= maxtime))
			]

			BLOCKS.append((radar_block, truth_block))

	return BLOCKS


def flattenedRadarTruthBlock(radar_truth_block):

	(radar_block, truth_block) = radar_truth_block

	flattened_block = [
		(point.stamp, 
		 point.confidence, 
		 point.latitude, 
		 point.longitude, 
		 point.altitude, 
		 point.distance, 
		 PAC(point.stamp, 
			 point.latitude, 
			 point.longitude, 
			 point.altitude, 
			 truth_block))
	    for point in radar_block
	]

	return flattened_block


def flattenedRadarTruthBlocks(BLOCKS):

	return [flattenedRadarTruthBlock(B) for B in BLOCKS]