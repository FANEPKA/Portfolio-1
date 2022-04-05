import json, typing


class JWORK:

    def __init__(self, file: typing.Optional[str] = None) -> None:
        if not file: self.file = 'config.json'
        else: self.file = file

    async def open_json(self, file: typing.Optional[str] = None) -> dict:
        if file: self.file = file
        with open(self.file, encoding='utf-8', mode='r') as file:
            return json.load(file)

    async def write_json(self, file: typing.Optional[str] = None, call = None):
        if file: self.file = file
        with open(self.file, encoding='utf-8', mode='w') as file:
            return json.dump(call, file, indent=4)

    def openj(self, file: typing.Optional[str] = None) -> dict:
        if file: self.file = file
        with open(self.file, encoding='utf-8', mode='r') as file:
            return json.load(file)

    def writej(self, file: typing.Optional[str] = None, call = None):
        if file: self.file = file
        with open(self.file, encoding='utf-8', mode='w') as file:
            return json.dump(call, file, indent=4)
        