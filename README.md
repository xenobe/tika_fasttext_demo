# Tika + FastText 语言检测项目

这个项目结合了 Apache Tika 和 FastText 来实现文档内容提取和语言检测功能。

## 功能特性

- 使用 Apache Tika 从各种格式的文档中提取文本内容
- 使用 FastText 进行高精度的语言检测（支持176种语言）
- 自动下载和管理 FastText 语言识别模型
- 提供详细的检测结果，包括置信度和备选语言
- 支持批量处理多个文档

## 环境要求

- Python 3.8+
- Apache Tika 服务器运行在 localhost:9998

## 安装步骤

### 1. 克隆项目并创建虚拟环境

```bash
git clone <your-repo-url>
cd tika_fasttext_test

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
source .venv/bin/activate  # macOS/Linux
# 或
.venv\Scripts\activate     # Windows
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 启动 Tika 服务器

下载并启动 Tika 服务器：

```bash
# 下载 Tika 服务器 JAR 文件
wget https://archive.apache.org/dist/tika/2.7.0/tika-server-standard-2.7.0.jar

# 启动服务器（在后台运行）
java -jar tika-server-standard-2.7.0.jar --port 9998 &
```

或者使用 Docker 运行 Tika 服务器：

```bash
docker run -d -p 9998:9998 apache/tika:2.7.0
```

## 使用方法

### 作为模块使用

```python
from app import extract_content, detect_language

# 提取文档内容
text = extract_content("your_document.docx")

# 检测语言
result = detect_language(text)
print(f"检测语言: {result['language']}")
print(f"置信度: {result['confidence']:.4f}")

# 查看备选语言
if result.get('alternatives'):
    print("备选语言:")
    for alt in result['alternatives']:
        print(f"  {alt['language']}: {alt['confidence']:.4f}")
```

### 批量处理文档

修改 `main()` 函数中的 `test_files` 列表来处理你的文档：

```python
def main():
    # 修改这里的文件列表
    test_files = ["document1.pdf", "document2.docx", "document3.txt"]
    
    for file_path in test_files:
        # ... 处理逻辑
```

然后运行：

```bash
python app.py
```

### 单个文件处理示例

```python
# 处理单个文件
if __name__ == "__main__":
    file_path = "your_document.pdf"  # 替换为你的文件路径
    
    # 提取内容
    text_content = extract_content(file_path)
    
    if not text_content.startswith("Error"):
        # 检测语言
        result = detect_language(text_content)
        
        if "error" not in result:
            print(f"文件: {file_path}")
            print(f"检测语言: {result['language']}")
            print(f"置信度: {result['confidence']:.4f}")
        else:
            print(f"检测失败: {result['error']}")
    else:
        print(f"内容提取失败: {text_content}")
```

## 输出示例

```
=== Tika + FastText 语言检测测试 ===

处理文件: document.docx
----------------------------------------
正在提取文件内容: document.docx
成功提取内容，长度: 5420 字符

语言检测结果:
  检测语言: en
  置信度: 0.9234
  备选语言:
    de: 0.0156
    fr: 0.0089

==================================================
```

## 支持的文档格式

通过 Apache Tika，支持以下格式：

- **Microsoft Office**: .docx, .xlsx, .pptx, .doc, .xls, .ppt
- **PDF**: .pdf
- **文本文件**: .txt, .rtf
- **网页文件**: .html, .htm
- **电子书**: .epub
- **压缩文件**: .zip, .tar, .gz（提取其中的文档）
- **图像文件**: .jpg, .png, .tiff（OCR文本提取）
- **其他格式**: 更多格式请参考 [Apache Tika 支持的格式](https://tika.apache.org/2.7.0/formats.html)

## 支持的语言

FastText 模型支持176种语言的检测，包括但不限于：

| 语言 | 代码 | 语言 | 代码 | 语言 | 代码 |
|------|------|------|------|------|------|
| 中文 | zh | 英文 | en | 日文 | ja |
| 韩文 | ko | 德文 | de | 法文 | fr |
| 西班牙文 | es | 俄文 | ru | 阿拉伯文 | ar |
| 意大利文 | it | 葡萄牙文 | pt | 荷兰文 | nl |

完整的语言列表请参考 [FastText 语言检测模型](https://dl.fbaipublicfiles.com/fasttext/supervised-models/)。

## API 参考

### `extract_content(file_path)`

从文档中提取文本内容。

**参数:**
- `file_path` (str): 文档文件路径

**返回:**
- `str`: 提取的文本内容，如果失败则返回错误信息

### `detect_language(text, model_path="lid.176.bin")`

检测文本的语言。

**参数:**
- `text` (str): 要检测的文本
- `model_path` (str): FastText 模型文件路径（可选）

**返回:**
- `dict`: 包含以下字段的字典
  - `language` (str): 检测到的语言代码
  - `confidence` (float): 置信度 (0-1)
  - `alternatives` (list): 备选语言列表
  - `warning` (str): 警告信息（如果有）
  - `error` (str): 错误信息（如果有）

## 配置选项

### 环境变量

- `TIKA_CLIENT_ONLY`: 设置为 'True' 使用外部 Tika 服务器
- `TIKA_SERVER_ENDPOINT`: Tika 服务器地址（默认: http://localhost:9998）

### 模型配置

- 模型文件: `lid.176.bin` (约125MB)
- 自动下载: 首次运行时自动下载
- 手动下载: `wget https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin`

## 注意事项

1. **Tika 服务器**: 确保 Tika 服务器在运行代码前已启动
2. **模型下载**: 首次运行时会自动下载 FastText 模型文件（约125MB）
3. **短文本检测**: 对于少于20个字符的文本，检测结果可能不够可靠
4. **NumPy 版本**: 使用 NumPy 1.26.4 版本以确保与 FastText 的兼容性
5. **内存使用**: 模型加载后会占用一定内存，建议在处理大量文件时重用模型实例

## 故障排除

### Tika 连接错误

检查 Tika 服务器是否正在运行：

```bash
curl http://localhost:9998/tika
# 应该返回: This is Tika Server (Apache Tika 2.7.0). Please PUT
```

如果服务器未运行，请启动 Tika 服务器：

```bash
java -jar tika-server-standard-2.7.0.jar --port 9998
```

### NumPy 兼容性问题

如果遇到 NumPy 相关错误，请确保使用兼容版本：

```bash
pip install "numpy<2.0"
```

### 模型下载失败

如果自动下载失败，可以手动下载模型：

```bash
wget https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin
```

### 内存不足

如果处理大文件时遇到内存问题：

1. 增加系统内存
2. 分批处理文件
3. 清理不必要的变量

### 文件编码问题

如果遇到编码错误，确保文件编码正确：

```python
# 对于特殊编码的文本文件
with open('file.txt', 'r', encoding='utf-8') as f:
    text = f.read()
result = detect_language(text)
```

## 性能优化

1. **模型重用**: 模型只加载一次，后续调用会重用已加载的模型
2. **批量处理**: 一次性处理多个文件比单独处理更高效
3. **文本预处理**: 移除不必要的空白字符和格式
4. **缓存结果**: 对于相同内容的文档，可以缓存检测结果

## 许可证

本项目使用的开源组件：

- Apache Tika: Apache License 2.0
- FastText: MIT License
- 其他依赖: 请查看各自的许可证

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目。

## 更新日志

- v1.0.0: 初始版本，支持基本的文档内容提取和语言检测
- v1.1.0: 修复 NumPy 兼容性问题，改进错误处理
- v1.2.0: 优化输出格式，添加批量处理支持
