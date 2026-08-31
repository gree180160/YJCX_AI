import os
from PIL import Image
import sys
import io


def get_image_size(img, format):
    """获取图片在特定格式和质量下的大小（字节）"""
    buffer = io.BytesIO()
    img.save(buffer, format=format)
    return buffer.tell()


def compress_image_to_target_size(file_path, target_size=80 * 1024):
    """将图片压缩至目标大小（字节），保持长宽比"""
    try:
        # 获取文件当前大小
        current_size = os.path.getsize(file_path)

        # 如果当前大小已经小于等于目标大小，无需处理
        if current_size <= target_size:
            return f"无需压缩: {os.path.basename(file_path)} ({current_size / 1024:.1f}KB ≤ {target_size / 1024}KB)"

        # 打开图片
        with Image.open(file_path) as img:
            # 获取图片格式
            img_format = img.format if img.format else 'JPEG'
            filename = os.path.basename(file_path).lower()

            # 根据文件扩展名确定格式（PIL可能识别不准确）
            if filename.endswith(('.png', '.PNG')):
                img_format = 'PNG'
            elif filename.endswith(('.jpg', '.jpeg', '.JPG', '.JPEG')):
                img_format = 'JPEG'

            # 初始质量参数
            if img_format == 'JPEG':
                quality = 85  # JPEG使用质量参数
            else:
                quality = 6  # PNG使用压缩级别

            # 先尝试调整质量参数来压缩
            temp_img = img.copy()
            current_test_size = get_image_size(temp_img, img_format)

            # 如果调整质量仍无法达到目标，再考虑缩小尺寸
            if current_test_size > target_size:
                # 计算需要缩小的比例
                scale_factor = (target_size / current_test_size) ** 0.5
                # 额外减小一点比例以确保能达到目标
                scale_factor *= 0.9

                # 计算新尺寸
                new_width = int(img.width * scale_factor)
                new_height = int(img.height * scale_factor)

                # 确保新尺寸不小于1x1
                new_width = max(1, new_width)
                new_height = max(1, new_height)

                # 调整图片大小
                temp_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                current_test_size = get_image_size(temp_img, img_format)

            # 对于JPEG，进一步微调质量参数以接近目标大小
            if img_format == 'JPEG':
                # 二分法寻找最佳质量参数
                low, high = 1, 100
                best_quality = quality
                best_size = current_test_size

                while high - low > 5:
                    mid = (low + high) // 2
                    test_size = get_image_size(temp_img, img_format, quality=mid)

                    if abs(test_size - target_size) < abs(best_size - target_size):
                        best_size = test_size
                        best_quality = mid

                    if test_size > target_size:
                        high = mid
                    else:
                        low = mid

                quality = best_quality

            # 保存压缩后的图片
            if img_format == 'JPEG':
                temp_img.save(file_path, format=img_format, quality=quality, optimize=True)
            elif img_format == 'PNG':
                temp_img.save(file_path, format=img_format, optimize=True, compress_level=quality)
            else:
                temp_img.save(file_path, format=img_format)

            # 计算最终大小
            final_size = os.path.getsize(file_path)

            return f"已压缩: {os.path.basename(file_path)} ({current_size / 1024:.1f}KB → {final_size / 1024:.1f}KB) 尺寸: {img.width}x{img.height} → {temp_img.width}x{temp_img.height}"

    except Exception as e:
        return f"处理出错: {os.path.basename(file_path)} - {str(e)}"


def process_folder(folder_path):
    """递归处理文件夹及其子文件夹中的所有图片"""
    # 支持的图片格式
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff')

    # 遍历当前文件夹中的所有项目
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)

        # 如果是文件夹，则递归处理
        if os.path.isdir(item_path):
            print(f"\n处理子文件夹: {item_path}")
            process_folder(item_path)
        # 如果是图片文件，则进行压缩
        elif os.path.isfile(item_path) and item.lower().endswith(image_extensions):
            result = compress_image_to_target_size(item_path)
            print(result)


if __name__ == "__main__":

    root_folder = "/Users/liuhe/Desktop/京创智通/website/calcitrapa_en/images"

    # 检查文件夹是否存在
    if not os.path.isdir(root_folder):
        print(f"错误: 文件夹 '{root_folder}' 不存在")
        sys.exit(1)

    # 执行压缩操作
    print(f"开始处理文件夹 '{root_folder}' 及其子文件夹中的图片...")
    print(f"规则: 大于80KB的图片将被压缩至约80KB")
    process_folder(root_folder)
    print("\n所有文件夹处理完成!")

