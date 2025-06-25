import time
import random
import string

def generate_random_value():
    # 随机生成一个长度为8的字符串
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

def main():
    # 步骤 1: 创建包含 50000 个键值对的字典
    print("Generating dictionary...")
    start_time = time.perf_counter()
    my_dict = {f'key_{i}': generate_random_value() for i in range(50000)}
    gen_time = time.perf_counter()
    print(f"Step 1: Dictionary created in {gen_time - start_time:.6f} seconds")

    # 步骤 2: 去掉 key，只保留 value，放入 list
    print("Extracting values into list...")
    values_list = list(my_dict.values())
    extract_time = time.perf_counter()
    print(f"Step 2: Values extracted in {extract_time - gen_time:.6f} seconds")

    total_time = extract_time - start_time
    print(f"Total elapsed time: {total_time:.6f} seconds")

    # 可选验证：打印前5个值
    print("First 5 values:", values_list[:5])

if __name__ == "__main__":
    main()
