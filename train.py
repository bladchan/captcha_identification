import os
import joblib
from PIL import Image
import numpy as np
from sklearn.ensemble import RandomForestClassifier


def extract_characters(image):
    img = np.asarray(image)
    characters = []
    for i in range(image.height):
        total = 0
        for j in range(image.width):
            if img[i][j] == 0:
                total += 1
        characters.append(total)
    for i in range(image.width):
        total = 0
        for j in range(image.height):
            if img[j][i] == 0:
                total += 1
        characters.append(total)
    return characters


def train_captcha():
    list1 = list(range(48, 57))
    list1 = list1 + list(range(97, 122))
    list1.remove(ord('o'))  # 'o'没有出现
    train_x = []
    train_y = []
    for i in range(len(list1)):
        work_dir = "./train_classify/" + chr(list1[i]) + "/"
        for f in os.listdir(work_dir):
            filepath = work_dir + f
            train_x.append(extract_characters(Image.open(filepath)))
            train_y.append(list1[i])
    train_x = np.array(train_x)
    train_y = np.array(train_y)
    rf = RandomForestClassifier(n_estimators=45, max_features='sqrt', oob_score=True)
    rf.fit(train_x, train_y)
    joblib.dump(rf, './randomforest.m')


if __name__ == "__main__":
    train_captcha()
