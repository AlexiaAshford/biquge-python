import cmd
import argparse
from instance import *


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

    if args.subcommand == "download":
        cmd.download_book(args.book_id, args.epub)
    elif args.subcommand == "update":
        cmd.update_book_list(args.limit, args.filename, args.epub)
    elif args.subcommand == "search":
        cmd.search_book(args.query, args.page, args.epub)
    else:
        parser.print_help()


if __name__ == '__main__':
    setup_config()
    cmd.agreed_read_readme()
    main()
