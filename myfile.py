import math_utils 
print("top-level in two.py") 
math_utils.func() 
if __name__ == "__main__": 
    print("two.py is being run directly") 
else: 
    print("two.py is being imported into another module")