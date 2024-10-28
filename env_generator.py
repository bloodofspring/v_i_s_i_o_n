import argparse
import os.path

from colorama import Fore


def write_env(args):
    if os.path.exists(".env"):
        a = input(
            Fore.LIGHTYELLOW_EX + "[!] Файл .env уже существует. Вы уверены, что хотите перезаписать его? (Y/n): ")
        if a != "Y":
            return

    if os.path.exists(".gitignore"):
        with open(".gitignore", "a") as gitignore_f:
            gitignore_f.write("\n.env\n")

    with open(".env", "w") as env_f:
        env_f.write((
            "name = '{}'\n"
            "api_id = {}\n"
            "api_hash = '{}'\n"
            "bot_token = '{}'\n"
            "yadisk_token = '{}'\n"
            "yandex_disk_folder_name = '{}'\n"
            "owner_id = {}\n".format(
                args.name, args.api_id, args.api_hash,
                args.bot_token, args.yadisk_token, args.yandex_disk_folder_name, args.owner_id
            )
        ))


def main():
    parser = argparse.ArgumentParser()

    required = parser.add_argument_group("Обязательные аргументы")
    optional = parser.add_argument_group("Опциональные аргументы")

    required.add_argument("-ai", "--api_id", help="API_ID клиента (бота)", type=int)
    required.add_argument("-ah", "--api_hash", help="API_HASH клиента (бота)", type=str)
    required.add_argument("-bt", "--bot_token", help="Токен клиента (бота)", type=str)
    required.add_argument(
        "-yt", "--yadisk_token",
        help="Ключ доступа к яндекс диску (ПРОВЕРЬТЕ ВЫДАННЫЕ ПРАВА!)",
        type=str
    )
    required.add_argument(
        "-oi", "--owner_id",
        help="Telegram ID владельца (Получить можно в @LeadConverterToolKitBot)",
        type=int
    )

    optional.add_argument(
        "-ydfn", "--yandex_disk_folder_name",
        help="Имя папки, которая будет создана на яндекс диске",
        type=str, default="v_i_s_i_o_n (your photos)"
    )
    optional.add_argument("-n", "--name", help="Имя бота", type=str, default="v_i_s_i_o_n")

    args = parser.parse_args()
    write_env(args=args)


if __name__ == "__main__":
    main()
