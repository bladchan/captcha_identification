# python机器学习识别正方教务系统验证码 V 2.0

### 起因

教务系统网站的验证码升级，此次验证码链接包含有SafeKey标识码，并且与cookie想绑定，而且验证码链接地址只能打开一次，第二次打开默认返回空白。此外，验证码图像也进行了升级，噪点数目明显变多，虽然用上个版本的模型依旧能够识别，但准确率相对较低，因此重新抓取数据集并进行训练。

如果验证码形下图左，则使用Version 1.0目录下的模型，否则使用本目录下的模型。



![](https://www.bladchan.ml/assets/img/captcha1.jpg)![](https://www.bladchan.ml/assets/img/captcha4.png)

### 环境

python 3.7.3

Pycharm

### 依赖库

requests库

Pillow库

sklearn库

其他库应为python自带库，若无法运行，请安装对应的库

### 步骤

#### 1.验证码图片预处理与分割

图片预处理：主要消除验证码图片的噪点，让图片的验证码清晰地显示以便提取相关特征。而正方教务系统的验证码主要包括一些噪点，没有其他曲线，而且字母和数字为深蓝色，并且没有很严重的变形，如下图所示。

![](https://www.bladchan.ml/assets/img/captcha4.png)

预处理与分割操作主要包括**灰度处理、二值化、去噪和裁剪**（相较于V1.0版本多了一个噪的环节）

灰度处理：主要将彩色图片变为灰度图片。彩色图片每个像素点包括rgb三层颜色，而灰度图片每个像素点只有一层颜色。直接使用Pillow库的相关函数即可将彩色图片变为灰度图片，代码如下：

```python
from PIL import Image
...
image = Image.open("./traindataset/" + f)
image = image.convert('L')  # 灰度处理
...
```

![](https://www.bladchan.ml/assets/img/captcha5.png)

二值化：将灰度图片的每个像素点设置为0（黑）或者255（白）。此步骤主要是消除噪点，由上图的灰度图可以看到数字与字母部分颜色较深，其像素值更接近与0，而噪点的像素值与255更接近，因此存在一个阈值，用以划分该像素是噪点还是数字与字母部分。经过反复的测试，尽可能使得噪点变少，得到阈值为50。即将像素值大于50的直接设置为255（白），而小于等于50的直接设置为0（黑色），此所谓二值化（二值：0/255）。代码如下：

```python
...
image = image.point(lambda x: 255 if x > 50 else 0)  # 二值化
...
```

裁剪：即进行分割，将每个数字/字符分割开来以便于特征提取。通过比较不同的验证码，最终确定提取的大小为12*22。代码如下：

```python
...
crop_range = [(4, 0, 16, 22), (16, 0, 28, 22), (28, 0, 40, 22), (42, 0, 54, 22)]  # 分割范围
for i in range(4):
	image_t = image.crop(crop_range[i])  # 裁剪
...
```

![](https://www.bladchan.ml/assets/img/captcha6.png)

去噪：将验证码字符外围孤立的点删除，唯一的不足是对边界处理的较为粗糙，并且对成块的噪点也没法剔除。

```python
def RemoveNoise(img):
    width = img.width
    height = img.height
    for i in range(width):
        for j in range(height):
            pixel = img.getpixel((i, j))
            if pixel == 255:
                continue
            else:
                if img.getpixel(((i-1) % width, j)) == 255 and img.getpixel((i, (j-1) % height)) == 255 and \
                        img.getpixel(((i+1) % width, j)) == 255 and img.getpixel((i, (j+1) % height)) == 255:
                    img.putpixel((i, j), 255)
    return img
```

#### 2.机器学习训练验证码

该步骤最重要的就是**特征提取**

特征提取就是将图片的特征提取出来，而不是将整个图片都作为数组放入训练。如果将整个图片作为数组进行训练，则feature包括12*22=264，特征数过多，不利于机器学习的训练，因此采用特征提取的办法来降低feature。而常用的算法是提取每一行、每一列的黑色，也就是像素值为0的个数，然后作为feature，则需要的特征数为12+22=34，特征数大大降低。具体代码如下：

```python
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
    return characters  # 返回特征向量
```

然后用机器学习的方法训练训练集，这里采用的是随机森林的方法，代码如下：

```python
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
```

#### 3.测试结果

对测试集200个验证码进行测试，得到的正确率如下：

(1).不去除噪点

> Total: 200
>
> correct 164
>
> Accuracy: 0.82

(2).去除噪点

>Total: 200
>
>correct 170
>
>Accuracy: 0.85

由上述结果可以看出，孤立噪点的剔除有利于验证码的识别，噪点对于特征提取是不利的，因为噪点会使得不同的字符存在相同特征的可能，这对于最后的识别是不利的，因此尽可能的对验证码图片进行处理是很有必要的。

当然，该测试结果相较于V1.0的模型来说，准确率方面不占优势，因为验证码图像升级了，因此识别难度加大了，但对于自动化的应用来说影响不大，因为验证码出错可以继续获取新的验证码并识别，直到验证码正确为止。

### 食用方法

目录下的randomforest.m文件为训练的模型文件，使用joblib库（较老版本的sklearn可能带有该库，目前该库是分离出sklearn的），使用函数将joblib导入，代码如下：

```python
import joblib
...
rf = joblib.load(model_path)  # 导入模型
...
result = rf.predict(characters_vector)  # 预测：输入为特征向量，输出为字符的ASCII码
```

使用前需要对验证码预处理，对验证码图像切割的每一个字符提取特征，然后用模型进行预测，得到预测的字符的ASCII码。循环四次，对验证码图像的每个字符进行预测，得到整个验证码的值。整体流程参考predict.py文件中的`predict_online`函数，函数部分如下：

```python
def predict_online(filepath):  # filepath: the path of captcha
    model_path = "./randomforest.m"  # model path
    rf = joblib.load(model_path)  # load model
    crop_range = [(4, 0, 16, 22), (16, 0, 28, 22), (28, 0, 40, 22), (42, 0, 54, 22)]  # crop range
    data = []  # characters vector
    for i in range(4):  # captcha contains four chars
        image = Image.open(filepath)  # open captcha image info
        image = image.convert('L')  # 灰度处理
        image = image.point(lambda x: 255 if x > 60 else 0)  # 二值化
        image = image.crop(crop_range[i])  # 裁剪
        image = RemoveNoise(image)  # 去噪
        data.append(extract_characters(image)) # extract characters
    data = np.array(data)  # list to np.array
    result = rf.predict(data)  # predict
    captcha_pre = ""
    for i in range(4):
        captcha_pre += chr(result[i])
    return captcha_pre
```
### 写在最后

学校教务系统验证码莫名其妙的升级了，该不会是我前期打码过于频繁导致的吧:(，新的验证码数据集也是经典打码，还好有之前的模型，能在一定程度上自动识别一部分的验证码，不过人工打码确实挺累的...
