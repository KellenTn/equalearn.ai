# equalearn.ai. - 使用指南

## 🎉 当前完全可用的功能

### 1. 文本输入数学问题

- ✅ 直接在文本框中输入数学问题
- ✅ 支持复杂的数学公式和 LaTeX 语法
- ✅ 获得详细的步骤解答

### 2. 生成 PDF 练习册

- ✅ 基于你的问题生成 20 道练习题
- ✅ 包含 10 道选择题、5 道判断题、5 道解答题
- ✅ 自动下载 PDF 文件
- ✅ 包含完整答案解析

### 3. 语音输入

- ✅ 点击麦克风按钮进行语音输入
- ✅ 浏览器原生支持，无需额外安装
- ✅ 支持英语语音识别

### 4. 数学公式渲染

- ✅ 支持 LaTeX 数学公式
- ✅ 美观的数学符号显示
- ✅ 支持复杂公式和符号

## 🔧 需要额外安装的功能

### 图片/视频/音频上传

这些功能需要安装系统依赖：

- **Tesseract OCR** - 用于图片和视频文字识别
- **FFmpeg** - 用于音频和视频处理

**安装方法：**

```bash
# 方法1：使用Homebrew（推荐）
brew install tesseract ffmpeg

# 方法2：手动下载安装
# 访问 https://github.com/tesseract-ocr/tesseract
# 访问 https://ffmpeg.org/download.html
```

## 🚀 快速开始

1. **启动应用：**

   ```bash
   python3 app.py
   ```

2. **访问应用：**

   - 主页面：http://localhost:8080
   - PDF 演示：http://localhost:8080/pdf_demo

3. **使用步骤：**
   - 输入数学问题（如：Find the derivative of x^2）
   - 点击"Solve Problem"获得解答
   - 点击"Generate 10 Calculation Problems"生成计算题练习册

## 💡 使用技巧

### 数学问题示例

```
基础运算：2 + 2 = ?
代数：Solve for x: 2x + 5 = 13
微积分：Find the derivative of x^2
几何：Find the area of a circle with radius 5
统计：Calculate the mean of [1, 2, 3, 4, 5]
```

### PDF 练习册特点

- 自动生成相关练习题
- 包含多种题型
- 提供完整解答
- 专业格式排版

## 🆘 常见问题

**Q: 为什么图片上传不工作？**
A: 需要安装 Tesseract OCR。可以先使用文本输入功能。

**Q: 为什么音频上传不工作？**
A: 需要安装 FFmpeg。可以使用浏览器内置的语音输入功能。

**Q: PDF 下载失败？**
A: 检查浏览器是否阻止了下载，或尝试刷新页面。

**Q: 服务器启动失败？**
A: 检查端口 8080 是否被占用，或使用其他端口。

## 📞 技术支持

如果遇到问题：

1. 检查服务器是否正常运行
2. 查看浏览器控制台错误信息
3. 尝试刷新页面
4. 重启应用程序

---

**注意：** 即使没有安装 Tesseract 和 FFmpeg，核心的数学求解和 PDF 生成功能完全正常！
