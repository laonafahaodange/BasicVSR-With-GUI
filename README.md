# BasicVSR++ With GUI v0.1
## 简介
BasicVSR++视频超分应用程序。界面基于PyQt5设计，模型及推理等文件基于BasicVSR++官方源码。

### 功能
程序会将输入的视频切分成图片保存在代码目录下的`temp/`文件夹，4倍超分的图片及视频保存在代码目录下的`results/`文件夹。

### 参数说明
- FPS：生成超分视频的帧数，可输入小数，默认25.0
- MAX_SEQ_LEN：每次推理处理的图片数，仅可输入整数，默认None，即一次将所有图片输入网络进行推理
- GPU：使用GPU进行推理，请确保有足够的显存
- CPU：使用CPU进行推理

### 注
***`lr.mp4`仅供测试使用，不代表本人任何观点。***

## 安装环境
1. cd到代码目录
2. 执行`conda env create -f environment.yaml`
3. 为确保QT控件可以播放mp4格式的视频，请安装代码目录下的应用程序`K-Lite_Codec_Pack_1695_Basic.exe`
4. 下载预训练权重文件至文件夹 `checkpoints/`. ([Dropbox](https://www.dropbox.com/s/eufigxmmkv5woop/RealBasicVSR.pth?dl=0) / [Google Drive](https://drive.google.com/file/d/1OYR1J2GXE90Zu2gVU5xc0t0P_UmKH7ID/view) / [OneDrive](https://entuedu-my.sharepoint.com/:u:/g/personal/chan0899_e_ntu_edu_sg/EfMvf8H6Y45JiY0xsK4Wy-EB0kiGmuUbqKf0qsdoFU3Y-A?e=9p8ITR))

## 引用
[BasicVSR++官方源码](https://github.com/ckkelvinchan/RealBasicVSR)
```
@article{chan2022investigating,
  author = {Chan, Kelvin C.K. and Zhou, Shangchen and Xu, Xiangyu and Loy, Chen Change},
  title = {Investigating Tradeoffs in Real-World Video Super-Resolution},
  journal = {IEEE Conference on Computer Vision and Pattern Recognition},
  year = {2022}
}
```
