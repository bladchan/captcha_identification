import os
import requests as r
from PIL import ImageTk
import tkinter as tk
from predict import predict_online
import re

domain = "jwxt1.ahu.edu.cn"
image_file = None


def Init():
    url = 'https://%s' % domain
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/78.0.3904.108 Safari/537.36'}
    # url = 'https://' + domain + '/CheckCode.aspx'
    response = r.get(url, headers=headers)
    headers['Cookie'] = response.headers.get('Set-Cookie')[0:42]
    captcha_url = re.search('title="看不清换一张" alt="看不清换一张" src="(.*)" style="border-width', response.text).group(1)
    captcha_url = 'https://{0}{1}'.format(domain, captcha_url)
    response = r.get(captcha_url, headers=headers)
    png = response.content
    with open('./traindataset/tmp.png', 'wb') as f:
        f.write(png)
    # 开启自动打码
    entry.insert(0, predict_online('./traindataset/tmp.png'))


def get_captcha():
    url = 'https://%s' % domain
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/78.0.3904.108 Safari/537.36'}
    # url = 'https://' + domain + '/CheckCode.aspx'
    response = r.get(url, headers=headers)
    headers['Cookie'] = response.headers.get('Set-Cookie')[0:42]
    captcha_url = re.search('title="看不清换一张" alt="看不清换一张" src="(.*)" style="border-width', response.text).group(1)
    captcha_url = 'https://{0}{1}'.format(domain, captcha_url)
    response = r.get(captcha_url, headers=headers)
    png = response.content
    with open('./traindataset/tmp.png', 'wb') as f:
        f.write(png)
    # 开启自动打码
    entry.insert(0, predict_online('./traindataset/tmp.png'))


if __name__ == '__main__':
    root = tk.Tk()
    root.title('打码器')
    root.geometry('400x220')
    entry = tk.Entry(root)
    entry.place(x=140, y=82, width=200, height=24)
    Init()
    canvas = tk.Canvas(root, height=50, width=100)
    image_file = ImageTk.PhotoImage(file='./traindataset/tmp.png')
    canvas.create_image(20, 20, anchor='nw', image=image_file)
    canvas.pack(side='top')
    lb = tk.Label(root, text='请输入验证码：')
    lb.place(x=40, y=80, width=100, height=30)


    def button_action(ev = None):
        os.rename('./traindataset/tmp.png', './traindataset/' + entry.get() + '.png')
        entry.delete(0, 4)
        Init()
        global image_file
        image_file = ImageTk.PhotoImage(file='./traindataset/tmp.png')
        canvas.create_image(20, 20, anchor='nw', image=image_file)

    def on_closing():
        if os.path.isfile('./traindataset/tmp.png'):
            os.remove('./traindataset/tmp.png')
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    button = tk.Button(root, text='提交', command=button_action)
    button.place(x=160, y=140, width=80, height=30)
    entry.bind("<Return>", button_action)
    root.mainloop()

