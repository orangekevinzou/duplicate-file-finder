#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
目录重复文件查找工具
对比两个目录，找出相同的文件，支持导出结果
"""

import os
import hashlib
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
from collections import defaultdict


class DuplicateFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("目录重复文件查找工具")
        self.root.geometry("680x650")
        self.root.resizable(False, False)

        # 变量
        self.path1_var = tk.StringVar()
        self.path2_var = tk.StringVar()
        self.method_var = tk.StringVar(value="name_size")  # name_only / name_size / hash
        self.output_var = tk.StringVar()
        self.include_subdirs_var = tk.BooleanVar(value=True)
        self.same_dir_var = tk.BooleanVar(value=False)

        self.create_widgets()

    def create_widgets(self):
        # 目录选择
        dir_frame = ttk.LabelFrame(self.root, text="选择两个要对比的目录", padding=10)
        dir_frame.pack(fill="x", padx=10, pady=5)

        # 目录1
        row1 = ttk.Frame(dir_frame)
        row1.pack(fill="x", pady=2)
        ttk.Label(row1, text="目录 1:", width=8).pack(side="left")
        ttk.Entry(row1, textvariable=self.path1_var, width=50).pack(side="left", padx=(0, 5))
        ttk.Button(row1, text="浏览...", command=lambda: self.browse_directory(self.path1_var)).pack(side="left")

        # 目录2
        row2 = ttk.Frame(dir_frame)
        row2.pack(fill="x", pady=2)
        ttk.Label(row2, text="目录 2:", width=8).pack(side="left")
        ttk.Entry(row2, textvariable=self.path2_var, width=50).pack(side="left", padx=(0, 5))
        ttk.Button(row2, text="浏览...", command=lambda: self.browse_directory(self.path2_var)).pack(side="left")

        # 对比选项
        opt_frame = ttk.LabelFrame(self.root, text="对比方式", padding=10)
        opt_frame.pack(fill="x", padx=10, pady=5)

        ttk.Radiobutton(opt_frame, text="文件名（最快）", variable=self.method_var, value="name_only").pack(anchor="w")
        ttk.Radiobutton(opt_frame, text="文件名 + 文件大小", variable=self.method_var, value="name_size").pack(anchor="w")
        ttk.Radiobutton(opt_frame, text="文件名 + 文件大小 + MD5哈希（最准确）", variable=self.method_var, value="hash").pack(anchor="w")

        ttk.Checkbutton(opt_frame, text="包含子目录", variable=self.include_subdirs_var).pack(anchor="w", pady=(5, 0))
        ttk.Checkbutton(opt_frame, text="要求相对目录名也相同", variable=self.same_dir_var).pack(anchor="w", pady=(0, 0))

        # 输出路径
        out_frame = ttk.LabelFrame(self.root, text="导出设置", padding=10)
        out_frame.pack(fill="x", padx=10, pady=5)

        ttk.Checkbutton(out_frame, text="导出结果到文本文件", variable=tk.BooleanVar(value=True),
                        command=self.toggle_output).pack(anchor="w")

        self.out_row = ttk.Frame(out_frame)
        self.out_row.pack(fill="x", pady=(5, 0))
        ttk.Entry(self.out_row, textvariable=self.output_var, width=50).pack(side="left", padx=(0, 5))
        ttk.Button(self.out_row, text="浏览...", command=self.browse_output).pack(side="left")

        # 操作按钮
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(btn_frame, text="开始查找", command=self.find_duplicates).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="清空结果", command=self.clear_results).pack(side="right", padx=5)

        # 进度条
        self.progress = ttk.Progressbar(self.root, mode="determinate", maximum=100)
        self.progress.pack(fill="x", padx=10, pady=(0, 5))

        # 结果区域
        result_frame = ttk.LabelFrame(self.root, text="查找结果", padding=5)
        result_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # 结果文本框 + 滚动条
        text_frame = ttk.Frame(result_frame)
        text_frame.pack(fill="both", expand=True)

        self.result_text = tk.Text(text_frame, wrap="none", font=("Consolas", 9), height=15)
        self.result_text.pack(side="left", fill="both", expand=True)

        scrollbar_y = ttk.Scrollbar(text_frame, orient="vertical", command=self.result_text.yview)
        scrollbar_y.pack(side="right", fill="y")
        self.result_text.configure(yscrollcommand=scrollbar_y.set)

        scrollbar_x = ttk.Scrollbar(result_frame, orient="horizontal", command=self.result_text.xview)
        scrollbar_x.pack(fill="x")
        self.result_text.configure(xscrollcommand=scrollbar_x.set)

        self.result_text.config(state="disabled")

    def toggle_output(self):
        pass

    def browse_directory(self, var):
        directory = filedialog.askdirectory(title="选择目录")
        if directory:
            var.set(directory)

    def browse_output(self):
        filepath = filedialog.asksaveasfilename(
            title="保存导出文件",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if filepath:
            self.output_var.set(filepath)

    def clear_results(self):
        self.result_text.config(state="normal")
        self.result_text.delete("1.0", "end")
        self.result_text.config(state="disabled")

    def log(self, message):
        self.result_text.config(state="normal")
        self.result_text.insert("end", message + "\n")
        self.result_text.see("end")
        self.result_text.config(state="disabled")
        self.root.update()

    def update_progress(self, value):
        """更新进度条"""
        self.progress["value"] = value
        self.root.update()

    def find_duplicates(self):
        path1 = self.path1_var.get().strip()
        path2 = self.path2_var.get().strip()
        method = self.method_var.get()
        include_subdirs = self.include_subdirs_var.get()
        same_dir = self.same_dir_var.get()

        if not path1 or not os.path.isdir(path1):
            messagebox.showerror("错误", "请选择有效的目录 1！")
            return
        if not path2 or not os.path.isdir(path2):
            messagebox.showerror("错误", "请选择有效的目录 2！")
            return

        self.clear_results()
        self.progress["value"] = 0

        self.log(f"正在扫描目录 1: {path1}")
        self.log(f"正在扫描目录 2: {path2}")
        self.log(f"对比方式: {self._method_name(method)}")
        self.log(f"包含子目录: {'是' if include_subdirs else '否'}")
        self.log(f"要求相同相对目录名: {'是' if same_dir else '否'}")
        self.log("-" * 60)

        try:
            # 扫描两个目录
            self.update_progress(10)
            files1 = self._scan_directory(path1, include_subdirs)
            self.update_progress(30)
            files2 = self._scan_directory(path2, include_subdirs)
            self.update_progress(50)

            self.log(f"目录 1 文件数: {len(files1)}")
            self.log(f"目录 2 文件数: {len(files2)}")
            self.log("-" * 60)

            # 查找重复
            duplicates = self._find_duplicates(files1, files2, method, same_dir)
            self.update_progress(90)

            if not duplicates:
                self.log("未找到相同文件！")
                self.update_progress(100)
                return

            # 显示结果
            self._display_results(duplicates, path1, path2)
            self.update_progress(100)

            # 导出
            output = self.output_var.get().strip()
            if output:
                self._export_results(duplicates, output, path1, path2, method, include_subdirs, same_dir)

        except Exception as e:
            self.log(f"错误: {str(e)}")
            messagebox.showerror("错误", f"查找失败: {str(e)}")
        finally:
            self.update_progress(100)

    def _scan_directory(self, root_path, include_subdirs):
        """扫描目录，返回文件信息列表"""
        files = []
        if include_subdirs:
            for dirpath, dirnames, filenames in os.walk(root_path):
                # 排序以保证稳定输出
                dirnames.sort()
                filenames.sort()
                rel_dir = os.path.relpath(dirpath, root_path)
                if rel_dir == '.':
                    rel_dir = ''
                for filename in filenames:
                    full_path = os.path.join(dirpath, filename)
                    try:
                        stat = os.stat(full_path)
                        files.append({
                            'filename': filename,
                            'path': full_path,
                            'rel_path': os.path.relpath(full_path, root_path),
                            'rel_dir': rel_dir,
                            'size': stat.st_size
                        })
                    except (OSError, PermissionError):
                        pass
        else:
            # 仅当前目录
            for entry in sorted(os.scandir(root_path), key=lambda e: e.name.lower()):
                if entry.is_file(follow_symlinks=False):
                    try:
                        stat = entry.stat()
                        files.append({
                            'filename': entry.name,
                            'path': entry.path,
                            'rel_path': entry.name,
                            'rel_dir': '',
                            'size': stat.st_size
                        })
                    except (OSError, PermissionError):
                        pass
        return files

    def _find_duplicates(self, files1, files2, method, same_dir=False):
        """查找重复文件"""
        duplicates = []

        # 为目录2建立索引
        index2 = defaultdict(list)
        for f in files2:
            key = self._make_key(f, method)
            index2[key].append(f)

        # 检查目录1的文件
        for f1 in files1:
            key = self._make_key(f1, method)
            if key in index2:
                for f2 in index2[key]:
                    # 如果要求相对目录名也相同
                    if same_dir and f1['rel_dir'] != f2['rel_dir']:
                        continue
                    # 如果是hash模式，需要实际计算比较
                    if method == "hash":
                        hash1 = self._calculate_md5(f1['path'])
                        hash2 = self._calculate_md5(f2['path'])
                        if hash1 and hash2 and hash1 == hash2:
                            duplicates.append({
                                'file1': f1,
                                'file2': f2,
                                'hash': hash1,
                                'size': f1['size']
                            })
                    else:
                        duplicates.append({
                            'file1': f1,
                            'file2': f2,
                            'hash': None,
                            'size': f1['size']
                        })

        return duplicates

    def _make_key(self, file_info, method):
        """生成索引键"""
        if method == "name_only":
            return file_info['filename'].lower()
        elif method == "name_size":
            return (file_info['filename'].lower(), file_info['size'])
        elif method == "hash":
            # 用文件名+大小作为初步筛选，再计算hash
            return (file_info['filename'].lower(), file_info['size'])

    def _calculate_md5(self, filepath, chunk_size=8192):
        """计算文件MD5"""
        md5 = hashlib.md5()
        try:
            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    md5.update(chunk)
            return md5.hexdigest()
        except (OSError, PermissionError):
            return None

    def _method_name(self, method):
        names = {
            "name_only": "文件名",
            "name_size": "文件名 + 文件大小",
            "hash": "文件名 + 文件大小 + MD5哈希"
        }
        return names.get(method, method)

    def _format_size(self, size):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"

    def _build_tree(self, duplicates):
        """将重复文件列表构建为树状字典"""
        tree = {}
        for dup in duplicates:
            # 使用目录1的相对路径作为树的路径
            rel_path = dup['file1']['rel_path']
            parts = rel_path.replace('\\', '/').split('/')
            node = tree
            for part in parts[:-1]:
                node = node.setdefault(part, {})
            # 叶子节点存储文件信息
            node[parts[-1]] = {
                'size': dup['size'],
                'path1': dup['file1']['path'],
                'path2': dup['file2']['path'],
                'hash': dup.get('hash'),
            }
        return tree

    def _render_tree(self, node, prefix="", lines=None):
        """将树状字典渲染为文本行"""
        if lines is None:
            lines = []

        # 排序：目录在前，文件在后，同类按名称排序
        items = sorted(node.items(), key=lambda x: (not isinstance(x[1], dict), x[0].lower()))

        for i, (name, child) in enumerate(items):
            is_last = (i == len(items) - 1)
            connector = "└── " if is_last else "├── "

            if isinstance(child, dict):
                # 目录
                lines.append(f"{prefix}{connector}{name}/")
                extension = "    " if is_last else "│   "
                self._render_tree(child, prefix + extension, lines)
            else:
                # 文件
                size_str = self._format_size(child['size'])
                lines.append(f"{prefix}{connector}{name}  ({size_str})")

        return lines

    def _display_results(self, duplicates, path1, path2):
        """显示结果 - 树状格式"""
        self.log(f"目录 1: {path1}")
        self.log(f"目录 2: {path2}")
        self.log("")

        # 构建树
        tree = self._build_tree(duplicates)
        lines = self._render_tree(tree)

        for line in lines:
            self.log(line)

        total_size = sum(d['size'] for d in duplicates)
        self.log("")
        self.log("-" * 60)
        self.log(f"共 {len(duplicates)} 个相同文件，总大小: {self._format_size(total_size)}")

    def _export_results(self, duplicates, output, path1, path2, method, include_subdirs, same_dir):
        """导出结果到文本文件"""
        with open(output, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("目录重复文件查找结果\n")
            f.write("=" * 60 + "\n\n")

            f.write(f"目录 1: {path1}\n")
            f.write(f"目录 2: {path2}\n")
            f.write(f"对比方式: {self._method_name(method)}\n")
            f.write(f"包含子目录: {'是' if include_subdirs else '否'}\n")
            f.write(f"要求相同相对目录名: {'是' if same_dir else '否'}\n")
            f.write(f"查找时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("-" * 60 + "\n\n")

            # 构建并写入树
            tree = self._build_tree(duplicates)
            lines = self._render_tree(tree)
            for line in lines:
                f.write(line + "\n")

            total_size = sum(d['size'] for d in duplicates)
            f.write("\n" + "-" * 60 + "\n")
            f.write(f"共 {len(duplicates)} 个相同文件，总大小: {self._format_size(total_size)}\n")

        self.log(f"\n结果已导出到: {output}")
        messagebox.showinfo("导出完成", f"结果已导出到:\n{output}")


def main():
    root = tk.Tk()
    app = DuplicateFinder(root)
    root.mainloop()


if __name__ == "__main__":
    main()
