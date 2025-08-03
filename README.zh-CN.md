# 漫画人下载器 (manhuaren2ebook)

[English](README.md)


这是一个 Python 脚本，可以从漫画人 (manhuaren.com) 网站下载指定漫画的所有章节，并将每个章节分别转换为 EPUB 格式的电子书。

## 功能

-   自动获取指定漫画主页下的所有章节链接。
-   模拟浏览器行为，逐页抓取每个章节的漫画图片。
-   将下载的图片打包成独立的 EPUB 文件，方便在电子阅读器上阅读。

## 使用方法

### 1. 环境准备

首先，确保你的系统已经安装了 Python 3。

**创建并激活虚拟环境 (推荐):**

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境 (macOS/Linux)
source venv/bin/activate

# 激活虚拟环境 (Windows)
.\venv\Scripts\activate
```

### 2. 安装依赖

在激活虚拟环境后，使用 pip 安装项目所需的依赖库：

```bash
pip install -r requirements.txt
```

### 3. 运行脚本

通过命令行参数指定要下载的漫画主页 URL 来运行脚本。

**语法:**

```bash
python comic2ebook.py <漫画主页URL>
```

**示例:**

```bash
python comic2ebook.py https://www.manhuaren.com/manhua-some-comic-name/
```

## 免责声明

本工具仅供个人学习和研究使用，下载内容的版权归原出版商及作者所有。请勿传播下载的文件，请尊重原始内容的版权，支持正版。

## 许可证

本项目采用 MIT 许可证 - 详情请见 [LICENSE](LICENSE) 文件。