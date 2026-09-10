import json

class Config():
    def __init__(self):
        try:
            with open("src/koske_galary/files/config.json") as file:
                self.config = json.load(file)
        except Exception as e:
            print(f"Failed loading the file, {e}")
            quit()
    
    def update(self, new, key:str) -> bool:
        try:
            self.config[key] = new
        except KeyError:
            print("No sutch config exists.")
            return False
        with open("src/koske_galary/files/config.json") as file:
            json.dump(file, self.config, indent=4)
            return True

