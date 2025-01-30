def convert_file_size(size: int) -> str:
    sizes = ["Б", "КБ", "МБ", "ГБ", "ТБ"]
    res_size_index = 0

    while size // 1024:
        size /= 1024
        res_size_index += 1

    return str(round(size, 2)) + sizes[res_size_index]
