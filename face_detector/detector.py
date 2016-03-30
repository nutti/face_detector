import cv2
import sys
import urllib2
import numpy as np
from math import ceil
import json
import os.path

def config_proxy(proxy_file_path):
    f = open(proxy_file_path, 'r')
    data = json.load(f)
    f.close()
    proxy = urllib2.ProxyHandler({'http': data['proxy_uri']})
    auth = urllib2.HTTPBasicAuthHandler()
    opener = urllib2.build_opener(proxy, auth)
    urllib2.install_opener(opener)


def get_image_from_url(url):
    filename = url.split("/")[-1]
    data = urllib2.urlopen(url).read()
    buf = np.fromstring(data, dtype=np.uint8)
    img = cv2.imdecode(buf, cv2.IMREAD_COLOR)
    return {'filename': filename, 'image': img}


def get_image_from_path(path):
    filename = os.path.basename(path)
    fd = open(path)
    data = fd.read()
    fd.close()
    buf = np.fromstring(data, dtype=np.uint8)
    img = cv2.imdecode(buf, cv2.IMREAD_COLOR)
    return {'filename': filename, 'image': img}


def detect_anime_face(image):
    CASCADE_FILE = 'face_detector/lbpcascade_animeface.xml'
    if not os.path.isfile(CASCADE_FILE):
        print "Cascade file %s not found" % (CASCADE_FILE)
        return None
    cascade_f = cv2.CascadeClassifier(CASCADE_FILE)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    orig_width = image.shape[1]
    orig_height = image.shape[0]
    orig_center = tuple(np.array([orig_width * 0.5, orig_height * 0.5]))
    print "Image info: (width, height, center) = (%d, %d, (%f, %f))" % (orig_width, orig_height, orig_center[0], orig_center[1])

    eq = cv2.equalizeHist(gray)
    faces = cascade_f.detectMultiScale(eq, scaleFactor=1.1, minNeighbors=5, minSize=(24, 24))
    if len(faces) > 0:
        print "%d faces are found" % len(faces)
        faces_info = []
        for i, (x, y, w, h) in enumerate(faces):
            print "face[%d] : (x0, y0, x1, y1) = (%d, %d, %d, %d)" % (i, x, y, x+w, y+h)
            faces_info.append({
                'x': float(x),
                'y': float(y),
                'width': float(w),
                'height': float(h)
            })
        return faces_info

    return None


def detect_frontal_face(image):
    cascade_f = cv2.CascadeClassifier('/usr/share/OpenCV/haarcascades/haarcascade_frontalface_alt.xml')
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    orig_width = image.shape[1]
    orig_height = image.shape[0]
    orig_center = tuple(np.array([orig_width * 0.5, orig_height * 0.5]))
    print "image info: (width, height, center) = (%d, %d, (%f, %f))" % (orig_width, orig_height, orig_center[0], orig_center[1])

    interval = 5
    for j in range(0, int(360/5)):
        angle = 5.0 * float(j)
        print "--- rotation=%d ---" % angle
        expanded_img = np.zeros((orig_height * 2, orig_width * 2, 3), np.uint8)
        expanded_img[ceil(orig_height / 2.0):ceil(orig_height / 2.0 * 3.0), ceil(orig_width / 2.0):ceil(orig_width / 2.0 * 3.0)] = image
        center = tuple(np.array([expanded_img.shape[1] * 0.5, expanded_img.shape[0] * 0.5]))
        size = tuple(np.array([expanded_img.shape[1], expanded_img.shape[0]]))
        rot_mat = cv2.getRotationMatrix2D(center, angle, 1.0)
        rot_img = cv2.warpAffine(expanded_img, rot_mat, size, flags=cv2.INTER_CUBIC)
        rot_gray = cv2.cvtColor(rot_img, cv2.COLOR_BGR2GRAY)
        faces = cascade_f.detectMultiScale(rot_img, scaleFactor=1.2, minNeighbors=2, minSize=(50, 50))
        if len(faces) > 0:
            print "found %d faces" % len(faces)
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


def detect_face(face_type, image):
    if face_type == "anime":
        print "detecting anime face..."
        return detect_anime_face(image)
    else:
        print "detecting frontal face..."
        return detect_frontal_face(image)
    

def output_image(filename, image, rect):
    cv2.imwrite(filename, image[rect['y']:(rect['y']+rect['height']), rect['x']:(rect['x']+rect['width'])])



