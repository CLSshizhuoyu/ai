import mistune
import webbrowser
import os
from tempfile import NamedTemporaryFile
import time


def render_markdown_to_html(markdown_text):
    """将 Markdown 文本转换为 HTML (兼容 mistune 2.x)"""
    # 创建自定义渲染器，添加复制按钮到代码块
    class CustomRenderer(mistune.Renderer):
        def block_code(self, code, lang=None):
            # 为代码块添加复制按钮
            button = f'''
            <div class="code-block">
                <div class="code-header">
                    <span class="code-lang">{lang or 'code'}</span>
                    <button class="copy-btn" 
                            data-code="{code.replace('"', '&quot;')}" 
                            aria-label="复制代码">
                        <i class="fa fa-copy"></i> 复制
                    </button>
                </div>
                <pre><code class="{'language-' + lang if lang else ''}">{self.escape(code)}</code></pre>
            </div>
            '''
            return button
    
    # 创建 Markdown 解析器实例
    renderer = CustomRenderer(escape=False)
    markdown = mistune.Markdown(renderer=renderer)
    
    # 渲染 Markdown 为 HTML
    return markdown(markdown_text)


def create_html_document(html_content, title="对话展示"):
    #获取icon
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, 'mdHTMLreader', 'favicon.png')
    #创建时间戳
    specific_time = time.strptime("2025-07-05 13:26:27", "%Y-%m-%d %H:%M:%S")
    title = time.mktime(specific_time)
    #创建html
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <link rel="icon" href={file_path} type="image/png">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdn.jsdelivr.net/npm/font-awesome@4.7.0/css/font-awesome.min.css" rel="stylesheet">
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    colors: {{
                        primary: '#3B82F6',
                        secondary: '#10B981',
                        neutral: '#F3F4F6',
                    }},
                    fontFamily: {{
                        sans: ['Inter', 'system-ui', 'sans-serif'],
                    }},
                }}
            }}
        }}
    </script>
    <style type="text/tailwindcss">
        @layer utilities {{
            .content-auto {{
                content-visibility: auto;
            }}
            .code-block {{
                @apply relative rounded-lg overflow-hidden shadow-md mb-6;
            }}
            .code-header {{
                @apply flex justify-between items-center bg-gray-800 text-white px-4 py-2;
            }}
            .copy-btn {{
                @apply flex items-center gap-1 bg-primary hover:bg-primary/90 text-white px-3 py-1 rounded transition-all duration-200;
            }}
            .copy-btn:hover {{
                @apply shadow-md transform scale-105;
            }}
            .copy-success {{
                @apply bg-secondary !important;
            }}
        }}
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <div class="container mx-auto px-4 py-8 max-w-4xl">
        <header class="mb-8">
            <h1 class="text-[clamp(1.8rem,3vw,2.5rem)] font-bold text-gray-800 mb-2">Utalk ai对话内容</h1>
            <p class="text-gray-600">本对话使用 <a href="https://clsshizhuoyu.github.io/" class="text-primary hover:underline">Utalk软件</a> 生成</p>
        </header>
        
        <main class="bg-white rounded-xl shadow-lg p-6 md:p-8 mb-8">
            {html_content}
        </main>
        
        <footer class="text-center text-gray-500 text-sm py-4">
            <p>内容由ai生成，不能作为专业依据</p>
        </footer>
    </div>

    <script>
        // 复制按钮功能
        document.addEventListener('DOMContentLoaded', function() {{
            document.querySelectorAll('.copy-btn').forEach(button => {{
                button.addEventListener('click', function() {{
                    const code = this.getAttribute('data-code');
                    
                    // 复制到剪贴板
                    navigator.clipboard.writeText(code).then(() => {{
                        // 更改按钮文本和颜色表示成功
                        const originalHTML = this.innerHTML;
                        this.innerHTML = '<i class="fa fa-check"></i> 已复制';
                        this.classList.add('copy-success');
                        
                        // 3秒后恢复原状
                        setTimeout(() => {{
                            this.innerHTML = originalHTML;
                            this.classList.remove('copy-success');
                        }}, 3000);
                    }}).catch(err => {{
                        console.error('复制失败: ', err);
                        alert('复制失败，请手动复制。');
                    }});
                }});
            }});
        }});
    </script>
</body>
</html>
"""


def main(file_path):
    """打开 Markdown 文件并在浏览器中显示"""
    try:
        # 读取 Markdown 文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        # 转换为 HTML
        html_content = render_markdown_to_html(markdown_content)
        # 创建完整的 HTML 文档
        full_html = create_html_document(
            html_content)
        # 创建临时 HTML 文件
        with NamedTemporaryFile('w', delete=False, suffix='.html', encoding='utf-8') as f:
            temp_html_path = f.name
            f.write(full_html)
        # 在浏览器中打开
        webbrowser.open('file://' + os.path.realpath(temp_html_path))
    except Exception as e:
        print(f"处理文件时出错: {e}")
