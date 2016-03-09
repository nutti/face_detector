from face_detector import detector
import sys

if __name__ == "__main__":
	url = sys.argv[1]
	face_type = sys.argv[2]
	output_dir = sys.argv[3]
	detector.config_proxy('proxy.json')
	img = detector.get_image(url)
	print img['filename']
	rect = detector.detect_face(face_type, img['image'])
	if rect is None:
		print "not found"
		sys.exit(1)
	print "x:%d, y:%d, w:%d, h:%d" % (rect['x'], rect['y'], rect['width'], rect['height'])
	detector.output_image(output_dir + "/" + "processed_" + img['filename'], img['image'], rect)
