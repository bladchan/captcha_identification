import joblib
import os
import numpy as np
from PIL import Image
from train import extract_characters


def predict_captcha():
    model_path = "./randomforest.m"
    rf = joblib.load(model_path)
    correct = 0
    total = 0
    for f in os.listdir("./testdataset"):
        total += 1
        crop_range = [(4, 0, 16, 22), (16, 0, 28, 22), (28, 0, 40, 22), (42, 0, 54, 22)]
        captcha = f[:4]
        data = []
        for i in range(4):
            image = Image.open("./testdataset/" + f)
            image = image.convert('L')  # 灰度处理
            image = image.point(lambda x: 255 if x > 50 else 0)  # 二值化
            image = image.crop(crop_range[i])  # 裁剪
            data.append(extract_characters(image))
        data = np.array(data)
        result = rf.predict(data)
        captcha_pre = ""
        for i in range(4):
            captcha_pre += chr(result[i])
        # print(captcha, "|", captcha_pre, "Yes" if captcha == captcha_pre else "No")
        if captcha == captcha_pre:
            correct += 1
    print("Total:", total)
    print("correct", correct)
    print("Accuracy:", correct/total)


def predict_online(filepath):
    model_path = "./randomforest.m"
    rf = joblib.load(model_path)
    crop_range = [(4, 0, 16, 22), (16, 0, 28, 22), (28, 0, 40, 22), (42, 0, 54, 22)]
    data = []
    for i in range(4):
        image = Image.open(filepath)
        image = image.convert('L')  # 灰度处理
        image = image.point(lambda x: 255 if x > 50 else 0)  # 二值化
        image = image.crop(crop_range[i])  # 裁剪
        data.append(extract_characters(image))
    data = np.array(data)
    result = rf.predict(data)
    captcha_pre = ""
    for i in range(4):
        captcha_pre += chr(result[i])
    return captcha_pre


if __name__ == "__main__":
    predict_captcha()
