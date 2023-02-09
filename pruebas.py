import pandas as pd
import os

for i in range(0, 50):
    data = pd.DataFrame(columns=['time_instant', 'cosas'])

    data.to_csv(os.path.join('data', f'{i}.csv'), index=False)
