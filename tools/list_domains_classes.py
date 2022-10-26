import json
from config import DICTIONARY

def main():
    with open(DICTIONARY, "r") as file:
        dictionary = json.loads(file.read())
    
    domains = set()
    classes = set()

    for entry in dictionary.values():
        domains.update(entry["domains"])
        classes.update(entry["classes"])
    
    print("Num Domains", len(domains))
    print("Num Classes", len(classes))
    print()
    print("Domains")
    print("\n".join(sorted(list(domains))))
    print()
    print("Classes")
    print("\n".join(sorted(list(classes))))


if __name__ == "__main__":
    main()