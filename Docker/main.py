import os 
import sys

def main(arg1): 
    with open("/app/UN.vi.translated.desubword", "w"):
        pass 
    os.system("bash run.sh {}".format(arg1))
    

if __name__ == "__main__":
    filename1 = sys.argv[1]
    print("Input Filename", filename1)

    main(filename1)