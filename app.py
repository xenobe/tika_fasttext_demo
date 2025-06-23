import os
import urllib.request
import warnings


#第一步,本地现在tika服务器: https://archive.apache.org/dist/tika/2.7.0/tika-server-standard-2.7.0.jar
#然后运行 java -jar tika-server-standard-2.7.0.jar

# 忽略 NumPy 兼容性警告
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)

import fasttext
from tika import parser

# 设置环境变量，指示 tika-python 不要启动服务器
os.environ['TIKA_CLIENT_ONLY'] = 'True'
# 指定 Tika 服务器位置
os.environ['TIKA_SERVER_ENDPOINT'] = 'http://localhost:9998'

def extract_content(file_path):
    try:
        print(f"正在提取文件内容: {file_path}")
        parsed = parser.from_file(file_path)
        content = parsed["content"]
        if content:
            print(f"成功提取内容，长度: {len(content)} 字符")
            return content.strip()
        else:
            print("未提取到内容")
            return "No content extracted"
    except Exception as e:
        error_msg = f"Error extracting content: {str(e)}"
        print(error_msg)
        return error_msg


def download_lid_model(model_path="lid.176.bin"):
    """下载 FastText 语言识别模型（如果不存在）"""
    if not os.path.exists(model_path):
        print(f"正在下载 FastText 语言识别模型到 {model_path}...")
        url = "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin"
        try:
            urllib.request.urlretrieve(url, model_path)
            print("模型下载完成！")
        except Exception as e:
            print(f"模型下载失败: {e}")
            return None
    else:
        print(f"模型文件已存在: {model_path}")
    return model_path

# 下载模型
model_path = download_lid_model()


def detect_language(text, model_path="lid.176.bin"):
    """
    使用 FastText 检测文本的语言

    参数:
        text (str): 要检测的文本
        model_path (str): FastText 语言模型的路径

    返回:
        dict: 包含语言代码和置信度的字典
    """
    try:
        # 检查模型文件是否存在
        if not os.path.exists(model_path):
            return {"error": f"Model file not found: {model_path}", "language": "unknown", "confidence": 0.0}
        
        # 加载模型（使用单例模式避免重复加载）
        if not hasattr(detect_language, "model"):
            print(f"正在加载 FastText 模型: {model_path}")
            # 临时抑制 NumPy 警告
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                detect_language.model = fasttext.load_model(model_path)
            print("模型加载完成！")

        # 确保文本非空并是字符串
        if not text or not isinstance(text, str):
            return {"language": "unknown", "confidence": 0.0}

        # 清理文本（移除过多的空白字符）
        text = " ".join(text.split())
        
        if not text:
            return {"language": "unknown", "confidence": 0.0}

        # 如果文本太短，可能不可靠
        if len(text) < 20:
            # 尝试检测但添加警告
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                predictions = detect_language.model.predict(text, k=1)
            lang = predictions[0][0].replace('__label__', '')
            conf = float(predictions[1][0])
            return {"language": lang, "confidence": conf, "warning": "Text too short, result may be unreliable"}

        # 正常检测
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            predictions = detect_language.model.predict(text, k=3)  # 获取前3个可能的语言

        # 解析结果
        languages = [lang.replace('__label__', '') for lang in predictions[0]]
        confidences = [float(conf) for conf in predictions[1]]

        # 返回结果字典
        result = {
            "language": languages[0],  # 最可能的语言
            "confidence": confidences[0],  # 置信度
            "alternatives": []
        }
        
        # 添加备选语言（如果有的话）
        if len(languages) > 1:
            result["alternatives"] = [
                {"language": lang, "confidence": conf}
                for lang, conf in zip(languages[1:], confidences[1:])
            ]

        return result

    except Exception as e:
        return {"error": str(e), "language": "unknown", "confidence": 0.0}


def main():
    """主函数，测试两个文档"""
    print("=== Tika + FastText 语言检测测试 ===\n")

    # 测试文件列表
    test_files = ["en.docx", "cn.docx"]

    for file_path in test_files:
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            continue

        print(f"处理文件: {file_path}")
        print("-" * 40)

        # 提取内容
        text_content = extract_content(file_path)

        if text_content.startswith("Error"):
            print(f"内容提取失败: {text_content}")
            continue

        # 显示文本预览
        preview = text_content[:200] + "..." if len(text_content) > 200 else text_content
        # print(f"文本预览: {preview}")
        print()
        
        # 语言检测
        result = detect_language(text_content)
        
        print("语言检测结果:")
        if "error" in result:
            print(f"  错误: {result['error']}")
        else:
            print(f"  检测语言: {result['language']}")
            print(f"  置信度: {result['confidence']:.4f}")
            
            if "warning" in result:
                print(f"  警告: {result['warning']}")
            
            if result.get('alternatives'):
                print("  备选语言:")
                for alt in result['alternatives']:
                    print(f"    {alt['language']}: {alt['confidence']:.4f}")
        
        print("\n" + "="*50 + "\n")


# 使用示例
if __name__ == "__main__":
    main()
