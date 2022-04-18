import os, sys

# finds the parent directory automatically
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.utils import start_connection

print(start_connection(3))
print(start_connection("stats_1"))
