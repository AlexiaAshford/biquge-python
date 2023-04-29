import json
import os
from rich import print


class Config:
    def __init__(self, file_path: str, dir_path: str):
        self.file_path = file_path
        self.dir_path = dir_path
        self.data = {}

    def load(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.data = json.load(f) or {}
        except FileNotFoundError:
            os.makedirs(self.dir_path, exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8"):
                pass
        except Exception as e:
            print(f"error: {e}\nerror: while reading config file: {self.file_path}")

    def save(self):
        try:
            os.makedirs(self.dir_path, exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"error: {e}\nerror: while saving config file: {self.file_path}")
