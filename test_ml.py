import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ml_model import check_word

print(check_word("spainish"))  
print(check_word("Ukranian")) 