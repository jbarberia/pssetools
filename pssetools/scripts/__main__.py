if __name__ == "__main__":
    import os
    path = os.path.dirname(__file__)
    files = os.listdir(path)

    print("")
    print("Scripts disponibles:")
    print("--------------------")

    for file in files:
        if file.startswith("__"): continue
        base, ext = os.path.splitext(file)
        print(" - " + base)
