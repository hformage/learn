import os
import shutil
from datetime import datetime

def _months_diff(date1, date2):
    """计算 date1 相对于 date2 的月份差（date1 - date2，以整月计）"""
    return (date1.year - date2.year) * 12 + (date1.month - date2.month)


def move_pic_order(path, path2, max_month=2):
    """
    类似 move_pic，但在移动到 YYYYMM 文件夹后，
    对该文件夹内的内容再按 tag_name 首字母分 0/a/g/m/s/y 六组。
    tag_name 是第一个下划线后第一个字母（文件名格式：{number}_{tag_name}_{date}）。
    数字归 0 文件夹，字母按 a,b,c,d,e,f->a，g,h,i,j,k,l->g，m,n,o,p,q,r->m，s,t,u,v,w,x->s，y,z->y。
    """
    if not os.path.isdir(path):
        raise ValueError(f"路径 {path} 不是一个有效目录")

    now = datetime.today()
    folder_counts = {}
    folder_sizes = {}
    yyyymm_files = {}  # 记录每个 yyyymm 文件夹下要二次分类的文件
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if not os.path.isfile(item_path):
            continue

        filename, ext = os.path.splitext(item)
        parts = filename.split('_')
        if len(parts) < 3:
            print(f"跳过文件（格式不符）: {item}")
            continue

        time_str = parts[-2]
        try:
            file_date = datetime.strptime(time_str, "%Y-%m-%d")
        except ValueError:
            print(f"跳过文件（时间格式错误）: {item}，时间字段为 '{time_str}'")
            continue

        month_diff = _months_diff(file_date, now)

        if month_diff < -max_month:
            folder_name = str(file_date.year)
        else:
            folder_name = file_date.strftime("%Y%m")

        target_dir = os.path.join(path2, folder_name)
        os.makedirs(target_dir, exist_ok=True)

        dest_path = os.path.join(target_dir, item)
        if os.path.exists(dest_path):
            print(f"跳过（目标已存在）: {item}")
            continue

        file_size = os.path.getsize(item_path)
        shutil.move(item_path, dest_path)
        folder_counts[folder_name] = folder_counts.get(folder_name, 0) + 1
        folder_sizes[folder_name] = folder_sizes.get(folder_name, 0) + file_size
        # 记录需要二次分类的文件
        if month_diff >= -max_month:
            yyyymm_files.setdefault(folder_name, []).append(item)


    def get_group_folder(first_char):
        c = first_char.lower()
        if c.isdigit():
            return '0'
        elif c in 'abc':
            return 'a'
        elif c in 'def':
            return 'd'
        elif c in 'ghi':
            return 'g'
        elif c in 'jkl':
            return 'j'
        elif c in 'mno':
            return 'm'
        elif c in 'pqr':
            return 'p'
        elif c in 'tuv':
            return 't'
        elif c in 'wxyz':
            return 'w'
        else:
            return '0'

    # 对所有 YYYYMM 文件夹下的所有文件（包括原有和新移动的）都进行二次分类
    for yyyymm in yyyymm_files.keys():
        yyyymm_dir = os.path.join(path2, yyyymm)
        # 只处理文件（不递归子目录）
        for fname in os.listdir(yyyymm_dir):
            src = os.path.join(yyyymm_dir, fname)
            if not os.path.isfile(src):
                continue
            filename, ext = os.path.splitext(fname)
            parts = filename.split('_')
            if len(parts) < 3:
                continue
            tag_name = parts[1]
            if not tag_name:
                continue
            group = get_group_folder(tag_name[0])
            if group == 'other':
                continue
            group_dir = os.path.join(yyyymm_dir, group)
            os.makedirs(group_dir, exist_ok=True)
            dst = os.path.join(group_dir, fname)
            if os.path.exists(dst):
                print(f"跳过（目标已存在）: {fname}")
                continue
            shutil.move(src, dst)

    def format_size(size):
        if size >= 1024 ** 3:
            return f"{size / (1024 ** 3):.2f} GB"
        elif size >= 1024 ** 2:
            return f"{size / (1024 ** 2):.2f} MB"
        elif size >= 1024:
            return f"{size / 1024:.2f} KB"
        else:
            return f"{size} B"

    if folder_counts:
        for folder, count in sorted(folder_counts.items()):
            total_size = folder_sizes.get(folder, 0)
            print(f"{folder}: {count} | {format_size(total_size)}")

    folder_counts = {}
    folder_sizes = {}
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if not os.path.isfile(item_path):
            continue

        filename, ext = os.path.splitext(item)
        parts = filename.split('_')
        if len(parts) < 3:
            print(f"跳过文件（格式不符）: {item}")
            continue

        time_str = parts[-2]
        try:
            file_date = datetime.strptime(time_str, "%Y-%m-%d")
        except ValueError:
            print(f"跳过文件（时间格式错误）: {item}，时间字段为 '{time_str}'")
            continue

        # 计算月份差：file_date 距离 now 有多少个月（负数表示过去）
        month_diff = _months_diff(file_date, now)  # 例如：-7 表示 7 个月前

        if month_diff < -max_month:
            # 7个月前或更早 → 按年归档
            folder_name = str(file_date.year)
        else:
            # 最近7个月内（不含7个月整）→ 按年月归档
            folder_name = file_date.strftime("%Y%m")

        target_dir = os.path.join(path2, folder_name)
        os.makedirs(target_dir, exist_ok=True)

        dest_path = os.path.join(target_dir, item)
        if os.path.exists(dest_path):
            print(f"跳过（目标已存在）: {item}")
            continue

        file_size = os.path.getsize(item_path)
        shutil.move(item_path, dest_path)
        # 汇总每个 folder_name 的移动数量和总大小
        folder_counts[folder_name] = folder_counts.get(folder_name, 0) + 1
        folder_sizes[folder_name] = folder_sizes.get(folder_name, 0) + file_size
    # 打印汇总结果（按 folder_name 排序）
    def format_size(size):
        if size >= 1024 ** 3:
            return f"{size / (1024 ** 3):.2f} GB"
        elif size >= 1024 ** 2:
            return f"{size / (1024 ** 2):.2f} MB"
        elif size >= 1024:
            return f"{size / 1024:.2f} KB"
        else:
            return f"{size} B"

    if folder_counts:
        for folder, count in sorted(folder_counts.items()):
            total_size = folder_sizes.get(folder, 0)
            print(f"{folder}: {count} | {format_size(total_size)}")

def unmove(path):
    """
    将 path 目录下的所有一级子文件夹中的文件移回 path 根目录，
    然后删除这些子文件夹。
    
    注意：
      - 只处理直接子文件夹（不递归深层目录）
      - 如果根目录已存在同名文件，则跳过该文件（避免覆盖）
      - 删除文件夹前确保其为空（只含文件，且文件已移走）
    """
    if not os.path.isdir(path):
        raise ValueError(f"路径 {path} 不是一个有效目录")

    # 获取 path 下所有直接子项
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        
        # 只处理子文件夹
        if not os.path.isdir(item_path):
            continue

        print(f"正在处理文件夹: {item}")
        # 遍历该文件夹内的所有内容
        for filename in os.listdir(item_path):
            src_file = os.path.join(item_path, filename)
            dest_file = os.path.join(path, filename)

            # 只移动文件（防止嵌套目录问题）
            if not os.path.isfile(src_file):
                print(f"  跳过非文件项: {filename}")
                continue

            # 检查目标是否已存在
            if os.path.exists(dest_file):
                print(f"  跳过（目标已存在）: {filename}")
                continue

            # 移动文件
            shutil.move(src_file, dest_file)
            print(f"  已移动: {filename}")

        # 尝试删除现在应为空的文件夹
        try:
            os.rmdir(item_path)  # 仅删除空目录
            print(f"已删除空文件夹: {item}")
        except OSError:
            print(f"警告：文件夹 {item} 非空，未删除（可能包含隐藏文件或子目录）")


# 示例用法（取消注释以测试）
if __name__ == "__main__":
    source = r'F:\Pic\Gelbooru\new\1'
    target = r'F:\Pic\Gelbooru\new\pending'
    move_pic_order(source, target)
    #unmove(r'F:\Pic\Gelbooru\new\pending')
    source = r'F:\copyandsend'
    target = r'F:\copyandsend2'
    #move_pic(source, target)