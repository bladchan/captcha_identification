# python机器学习识别正方教务系统验证码 V 1.0

### 环境

python 3.7.3

Pycharm

### 依赖库

requests库

Pillow库

sklearn库

其他库应为python自带库，若无法运行，请安装对应的库

### 步骤

##### 1.验证码图片预处理与分割

图片预处理：主要消除验证码图片的噪点，让图片的验证码清晰地显示以便提取相关特征。而正方教务系统的验证码主要包括一些噪点，没有其他曲线，而且字母和数字为深蓝色，并且没有很严重的变形，如下图所示。

![](https://www.bladchan.ml/assets/img/captcha1.jpg)

预处理与分割操作主要包括**灰度处理、二值化和裁剪**

灰度处理：主要将彩色图片变为灰度图片。彩色图片每个像素点包括rgb三层颜色，而灰度图片每个像素点只有一层颜色。直接使用Pillow库的相关函数即可将彩色图片变为灰度图片，代码如下：

```python
from PIL import Image
...
image = Image.open("./traindataset/" + f)
image = image.convert('L')  # 灰度处理
...
```

![](https://www.bladchan.ml/assets/img/captcha2.png)

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

![](https://www.bladchan.ml/assets/img/captcha3.png)

##### 2.机器学习训练验证码

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

##### 3.测试结果

对测试集200个验证码进行测试，得到的正确率如下：

> Total: 200
> correct 194
> Accuracy: 0.97