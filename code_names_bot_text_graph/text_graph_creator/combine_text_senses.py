import os
import json

from config import TEXT_SENSES, TEXT_SENSE_BATCHES

def main():
    text_senses = dict()
    for filename in os.listdir(TEXT_SENSE_BATCHES):
        if filename.endswith(".json"):
            path = os.path.join(TEXT_SENSE_BATCHES, filename)
            with open(path, "r") as file:
                text_senses.update(json.loads(file.read()))

    with open(TEXT_SENSES, "w+") as file:
        file.write(json.dumps(text_senses, sort_keys=True, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    main()