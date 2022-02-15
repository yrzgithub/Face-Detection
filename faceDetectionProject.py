from face_recognition import face_locations, face_encodings, compare_faces
import cv2
from pyttsx3 import init
from keyboard import is_pressed
from pickle import load, dump
from os import listdir, remove
from time import time
from easygui import enterbox

path_of_images = r"C:\Users\seenusanjay\PycharmProjects\pythonProject2\known\images"
path_of_face_encodings = r"C:\Users\seenusanjay\PycharmProjects\pythonProject2\known\face_encodings"
path_for_names = r"C:\Users\seenusanjay\PycharmProjects\pythonProject2\known\names"
path_for_non_coded_images = r"C:\Users\seenusanjay\PycharmProjects\pythonProject2\known\non coded images"
path_for_known = r"C:\Users\seenusanjay\PycharmProjects\pythonProject2\known"
win_name = "Division By Zero"

convertor = init()
voices = convertor.getProperty("voices")
convertor.setProperty("voice", voices[1].id)


def sayAndPrint(text):
    convertor.say(text)
    print(text)
    convertor.runAndWait()


def face_location_function(img):
    try:
        locations = face_locations(img)
    except TypeError:
        locations = [[]]
    return locations


def draw_rectangle(img):
    locations = face_location_function(img)
    for (a, b, c, d) in locations:
        cv2.rectangle(img, (d, a), (b, c), (250, 0, 250), thickness=2)  # doubt


def start_camera():
    cam = cv2.VideoCapture(0)
    img = None
    while not is_pressed("esc"):
        ret, img = cam.read()
        if not ret:
            continue
        draw_rectangle(img)
        cv2.imshow(win_name, img)
        cv2.waitKey(1)
    cam.release()
    cv2.destroyAllWindows()
    return img


def add_image(img):
    location = face_location_function(img)
    length = len(location)
    if length != 1:
        sayAndPrint("Number of people in the image is not 1...\nPlease try again...")
        return False
    msg = "Enter their name:"
    sayAndPrint(msg)
    cv2.imshow(win_name, img)
    cv2.waitKey(1)
    name = enterbox(msg=msg, title=win_name)
    if name in ["", None]:
        sayAndPrint("Given name is invalid...Can't add this image..")
        cv2.destroyAllWindows()
        return False
    try:
        known = load(open(path_for_names, "rb"))
    except FileNotFoundError:
        known = []
    img_path = r"{path}\{count}.{name}.jpg".format(path=path_of_images, count=len(known) + 1, name=name)
    known += [name]
    dump(known, open(path_for_names, "wb"))
    cv2.imwrite(img_path, img)
    encodings = face_encodings(img, model="large")
    try:
        old_encoding = load(open(path_of_face_encodings, "rb"))
    except FileNotFoundError:
        dump(encodings, open(path_of_face_encodings, "wb"))
    else:
        new_encodings = old_encoding + [encodings]
        dump(new_encodings, open(path_of_face_encodings, "wb"))
    sayAndPrint("Image saved")
    cv2.destroyAllWindows()
    return True


def add_images_from_folder():
    files = listdir(path_for_non_coded_images)
    for i in files:
        path = path_for_non_coded_images + "\\" + i
        img = cv2.imread(path)
        if add_image(img):
            remove(path)


def detect_live():
    try:
        known_face_encodings = load(file=open(path_of_face_encodings, "rb"))
    except FileNotFoundError:
        sayAndPrint("Please add images and try again...")
        return None
    known_people = load(open(path_for_names, "rb"))
    detected_people_before_5min = []
    start_time = time()
    camera = cv2.VideoCapture(0)
    while not is_pressed("esc"):
        ret, img = camera.read()
        if not ret:
            return None
        draw_rectangle(img)
        cv2.imshow(win_name, img)
        cv2.waitKey(1)
        face_encodings_cam = face_encodings(img, model="large")
        for i in face_encodings_cam:
            comparison = compare_faces(known_face_encodings, i, tolerance=0.5)
            print(comparison)
            if comparison.count(True) > 1:
                continue
            if time() - start_time > 300:
                start_time = time()
                detected_people_before_5min = []
            try:
                result = comparison.index(True)
                detected_person = known_people[result]
                assert detected_person not in detected_people_before_5min, "same person"  # get minutes from user
                sayAndPrint(detected_person)
                detected_people_before_5min.append(detected_person)
            except ValueError:
                pass
            except AssertionError as e:
                print(e)
    camera.release()
    cv2.destroyAllWindows()


def detect_for_now():
    try:
        known_face_encodings = load(file=open(path_of_face_encodings, "rb"))
    except FileNotFoundError:
        sayAndPrint("Please add images and try again...")
        return None
    img = start_camera()
    face_encodings_cam = face_encodings(img, model="large")
    known_people = load(open(path_for_names, "rb"))
    for i in face_encodings_cam:
        comparison = compare_faces(known_face_encodings, i, tolerance=0.5)
        print(comparison)
        if comparison.count(True) > 1:
            detect_for_now()
        try:
            result = comparison.index(True)
            sayAndPrint(known_people[result])
        except ValueError:
            sayAndPrint("unknown..")
            pass


def reset():  # deletes all the files
    try:
        remove(path_for_names)
        remove(path_of_face_encodings)
    except FileNotFoundError:
        pass
    for i in listdir(path_of_images):
        path = path_of_images + "\\" + i
        remove(path)
    sayAndPrint("successfully reseted...")