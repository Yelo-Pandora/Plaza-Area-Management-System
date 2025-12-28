import os

# --- 配置项 ---
# 要遍历的目录 (通常是当前脚本所在的目录，即项目根目录)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__)) 
# 输出的文本文档名称
OUTPUT_FILE = "project_code_output.txt"
# 需要排除的目录（例如虚拟环境、PyCharm配置、Git文件等）
EXCLUDE_DIRS = ['venv', '.idea', '__pycache__', '.git', 'node_modules', 'dist', 'build'] 
# 排除当前脚本文件本身
EXCLUDE_FILES = [OUTPUT_FILE, os.path.basename(__file__)] 
# 要包含的文件类型
FILE_EXTENSIONS = ['.py', '.html', '.css', '.js', '.json', '.txt', '.xml'] # 你可以根据需要添加更多文件类型
# --- 配置项结束 ---

def export_project_code_to_single_file():
    """遍历项目目录，将所有指定类型文件的内容合并到单个文本文件中。"""
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as outfile:
        print(f"开始扫描项目目录：{PROJECT_ROOT}")
        
        # os.walk() 会遍历目录树
        for root, dirs, files in os.walk(PROJECT_ROOT, topdown=True):
            
            # 排除不需要的目录，修改 dirs 列表可以影响 os.walk 的后续行为
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith('.')]
            
            # 遍历当前目录下的文件
            for file_name in files:
                
                # 检查文件名是否需要排除
                if file_name in EXCLUDE_FILES:
                    continue
                    
                # 检查文件扩展名是否在包含列表中
                if any(file_name.endswith(ext) for ext in FILE_EXTENSIONS):
                    
                    file_path = os.path.join(root, file_name)
                    # 获取相对路径，使输出文件中的路径更清晰
                    relative_path = os.path.relpath(file_path, PROJECT_ROOT)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            content = infile.read()
                            
                            # 添加分隔符和文件路径，方便区分不同的代码文件
                            outfile.write(f"\n{'='*80}\n")
                            outfile.write(f"文件路径: {relative_path}\n")
                            outfile.write(f"{'-'*80}\n\n")
                            outfile.write(content)
                            outfile.write("\n\n")
                            print(f"  [√] 已添加文件: {relative_path}")
                            
                    except Exception as e:
                        print(f"  [X] 无法读取文件 {relative_path}: {e}")

    print(f"\n{'#'*80}")
    print(f"🎉 代码提取完成！所有代码已保存到项目根目录下的: {OUTPUT_FILE}")
    print(f"{'#'*80}")

if __name__ == "__main__":
    export_project_code_to_single_file()