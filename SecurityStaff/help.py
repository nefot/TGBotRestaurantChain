import os
import pyperclip

def print_tree(directory, prefix="", is_last=True):
    """
    Рекурсивно выводит дерево файлов и папок.
    """
    tree_str = prefix + ("└── " if is_last else "├── ") + os.path.basename(directory) + "\n"

    if os.path.isdir(directory):
        # Получаем список всех элементов в директории
        items = os.listdir(directory)
        # Фильтруем только Python-файлы и папки
        items = [item for item in items if item.endswith(".py") or os.path.isdir(os.path.join(directory, item))]
        # Рекурсивно обходим каждый элемент
        for i, item in enumerate(items):
            is_last_item = (i == len(items) - 1)
            new_prefix = prefix + ("    " if is_last else "│   ")
            tree_str += print_tree(os.path.join(directory, item), new_prefix, is_last_item)

    return tree_str

def get_file_content(filepath):
    """
    Возвращает содержимое Python-файла в виде строки.
    """
    content = ""
    with open(filepath, "r", encoding="utf-8") as file:
        content += "```python\n"
        for line in file:
            content += line.rstrip() + "\n"
        content += "```\n"
    return content

def main():
    # Укажите путь к директории, которую нужно просканировать
    root_directory = "."  # Текущая директория
    root_directory_name = os.path.basename(os.path.abspath(root_directory))  # Имя корневой папки

    # Формируем вывод
    output = f"Дерево файлов Python в директории '{root_directory_name}':\n"
    output += print_tree(root_directory)

    # Добавляем содержимое всех Python-файлов
    for root, _, files in os.walk(root_directory):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                output += f"\nСодержимое файла '{filepath}':\n"
                output += get_file_content(filepath)

    # Копируем вывод в буфер обмена
    pyperclip.copy(output)
    print("Вывод скопирован в буфер обмена!")

if __name__ == "__main__":
    main()