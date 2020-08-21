from PIL import Image
import os


if __name__ == '__main__':
    dirs = os.listdir("./traindataset")
    if not os.path.isdir("./train_classify"):
        os.makedirs("./train_classify")
    dict = {}
    for f in dirs:
        crop_range = [(4, 0, 16, 22), (16, 0, 28, 22), (28, 0, 40, 22), (42, 0, 54, 22)]  # 分割范围
        captcha = f[:4]
        image = Image.open("./traindataset/" + f)
        image = image.convert('L')  # 灰度处理
        image = image.point(lambda x: 255 if x > 50 else 0)  # 二值化
        for i in range(4):
            image_t = image.crop(crop_range[i])  # 裁剪
            c = captcha[i]
            if not os.path.isdir("./train_classify/" + c):
                os.makedirs("./train_classify/" + c)
                dict[captcha[i]] = 1
            if c not in dict.keys():
                dict[c] = 1
            image_t.save("./train_classify/" + c + "/" + str(dict[c]) + ".png")
            dict[captcha[i]] += 1