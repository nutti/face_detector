import os.path
from face_detector import detector
import argparse
import sys

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', default="out")
    parser.add_argument('-f', '--face_type', default="frontal")
    parser.add_argument('-u', '--url', default=False)
    parser.add_argument('-p', '--path', default=False)
    args = parser.parse_args()
    url = args.url
    face_type = args.face_type
    output_dir = args.output
    path = args.path

    if url:
        detector.config_proxy('proxy.json')
        img = detector.get_image_from_url(url)
    elif path:
        img = detector.get_image_from_path(path)
    else:
        print "Must specify image source."
        sys.exit(1)

    faces = detector.detect_face(face_type, img['image'])
    if faces is None:
        print "No face is found"
        sys.exit(1)
    for i, f in enumerate(faces):
        base, ext = os.path.splitext(img['filename'])
        detector.output_image(output_dir + "/" + "processed_" + base + "_f" + str(i) + ext, img['image'], f)
