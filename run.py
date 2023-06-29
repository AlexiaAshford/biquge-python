import sys

import cmd
import argparse
from instance import *


def agreed_read_readme():
    if Vars.cfg.data.get('Disclaimers') != 'yes':
        print(Msg.msg_agree_terms)
        confirm = input_str('>').strip()
        if confirm == 'yes' or confirm == '同意':
            Vars.cfg.data['Disclaimers'] = 'yes'
            Vars.cfg.save()
        else:
            sys.exit()


def main():
    parser = argparse.ArgumentParser(description="cmdline tool for BiquPavilion")
    parser.add_argument("-e", "--epub", required=False, default=True, action="store_false", help="if download epub")

    subparsers = parser.add_subparsers(dest="subcommand", help="subcommands")

    download_parser = subparsers.add_parser("download", help="download book to local directory")
    download_parser.add_argument("-id", "--book-id", required=True, help="download book by book id")

    update_parser = subparsers.add_parser("update", help="update book list, and download book to local directory")
    update_parser.add_argument("-l", "--limit", required=False, help="update book list by limit", default=10)
    update_parser.add_argument("-f", "--filename", required=True, help="update book list by filename")

    search_parser = subparsers.add_parser("search", help="search book by keyword")
    search_parser.add_argument("-p", "--page", type=int, default=1, help="the page of search result")
    search_parser.add_argument("-q", "--query", required=True, help="keyword of search")
    args = parser.parse_args()

    command_map = {
        "download": cmd.Command.download,
        "update": cmd.Command.update,
        "search": cmd.Command.search
    }

    command = command_map.get(args.subcommand)
    if command:
        if args.subcommand == "update":
            command(args.limit, args.filename, args.epub)
        elif args.subcommand == "search":
            command(args.query, args.page, args.epub)
        elif args.subcommand == "download":
            command(args.book_id, args.epub)
    else:
        parser.print_help()


if __name__ == '__main__':
    setup_config()
    agreed_read_readme()
    main()
