from datetime import datetime
import random, string

def new_id() -> str:
    return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]) 
    
def current_time() -> str:
    return datetime.now().strftime("%B %d, %Y at %H:%M:%S")
