#!/bin/bash

# 批量重命名脚本：去掉所有文件名中的 (1) 后缀
# 使用方法: bash rename_files.sh

echo "开始批量重命名文件..."
echo "========================================"

count=0

# 查找所有带 (1) 的文件
find . -depth -name "*(1)*" -type f | while read file; do
    # 获取目录和文件名
    dir=$(dirname "$file")
    filename=$(basename "$file")

    # 去掉 (1) 生成新文件名
    newname=$(echo "$filename" | sed 's/(1)//g')

    # 构建完整路径
    newfile="$dir/$newname"

    # 如果新文件名和旧文件名不同，则重命名
    if [ "$file" != "$newfile" ]; then
        # 检查目标文件是否已存在
        if [ -e "$newfile" ]; then
            echo "⚠️  跳过（目标已存在）: $file -> $newfile"
        else
            mv "$file" "$newfile"
            echo "✓ 重命名: $filename -> $newname"
            ((count++))
        fi
    fi
done

echo "========================================"
echo "重命名完成！共处理 $count 个文件"
