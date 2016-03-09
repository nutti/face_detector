import cv2
import sys
import urllib2
import numpy as np
from math import ceil
import json

def config_proxy(proxy_file_path):
	f = open(proxy_file_path, 'r')
	data = json.load(f)
	f.close()
	print data['proxy_uri']
	proxy = urllib2.ProxyHandler({'http': data['proxy_uri']})
	auth = urllib2.HTTPBasicAuthHandler()
	opener = urllib2.build_opener(proxy, auth)
	urllib2.install_opener(opener)


def get_image(url):
	filename = url.split("/")[-1]
	data = urllib2.urlopen(url).read()
	buf = np.fromstring(data, dtype=np.uint8)
	img = cv2.imdecode(buf, cv2.IMREAD_COLOR)
	return {'filename': filename, 'image': img}
	

def detect_face(face_type, image):
	if face_type == "anime":
		cascade_f = cv2.CascadeClassifier('lbpcascade_animeface.xml')
	else:
		cascade_f = cv2.CascadeClassifier('/usr/share/OpenCV/haarcascades/haarcascade_frontalface_alt.xml')
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	orig_width = image.shape[1]
	orig_height = image.shape[0]
	orig_center = tuple(np.array([orig_width * 0.5, orig_height * 0.5]))

	interval = 5
	for j in range(0, int(360/5)):
		expanded_img = np.zeros((orig_height * 2, orig_width * 2, 3), np.uint8)
		expanded_img[ceil(orig_height / 2.0):ceil(orig_height / 2.0 * 3.0), ceil(orig_width / 2.0):ceil(orig_width / 2.0 * 3.0)] = image
		center = tuple(np.array([expanded_img.shape[1] * 0.5, expanded_img.shape[0] * 0.5]))
		size = tuple(np.array([expanded_img.shape[1], expanded_img.shape[0]]))
		angle = 5.0 * float(j)
		rot_mat = cv2.getRotationMatrix2D(center, angle, 1.0)
		rot_img = cv2.warpAffine(expanded_img, rot_mat, size, flags=cv2.INTER_CUBIC)
		rot_gray = cv2.cvtColor(rot_img, cv2.COLOR_BGR2GRAY)
		faces = cascade_f.detectMultiScale(rot_img, scaleFactor=1.2, minNeighbors=2, minSize=(50, 50))
		if len(faces) > 0:
			#faces = cascade_f.detectMultiScale(gray)
			for (x, y, w, h) in faces:
				cv2.rectangle(rot_img, (x, y), (x + w, y + h), (0, 0, 0), 2)
				print "(x0,y0,x1,y1) = (%d, %d, %d, %d)\n" % (x, y, x+w, y+h)
				offset_x = center[0] - orig_center[0]
				offset_y = center[1] - orig_center[1]
				print "ox:%d, oy:%d" % (offset_x, offset_y)
				return {
					'x': float(x) - float(offset_x),
					'y': float(y) - float(offset_y),
					'width': float(w),
					'height': float(h),
					'angle': float(angle)
				}
	return None


def output_image(filename, image, rect):
	cv2.imwrite(filename, image[rect['y']:(rect['y']+rect['height']), rect['x']:(rect['x']+rect['width'])])


#if __name__ == "__main__":
#	param = sys.argv
#	config_proxy()
#	detect_face(param[1])


