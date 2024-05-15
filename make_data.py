import numpy as np
import json
from pathlib import Path
import imageio
import pandas as pd
import xarray as xr
import intake

def write_mp4(video_array, file_name, fps=30):
    with imageio.get_writer(file_name, fps=fps) as writer:
        for i in range(video_array.shape[0]):
            writer.append_data(video_array[i])


def main():
    shots = [
        30390,
        30391,
        30392,
        30393,
        30394,
        30395,
        30396,
        30397,
        30398,
        30420
    ]

    cat = intake.open_catalog("catalog.yml")

    for shot in shots:
        try:
            current_dataset: xr.Dataset = cat.tiny(shot=shot, name='amc/plasma_current').read()
            current_dataset: pd.DataFrame = current_dataset.to_dataframe()
            current_file = f"local_data/{shot}.csv"
            current_dataset.to_csv(current_file)

            image_dataset = cat.tiny(shot=shot, name='rba').read()
            video = image_dataset.data.values
            video_file = f'local_data/{shot}.mp4'
            write_mp4(video, video_file)

            datasets = []
            for channel in range(1, 19):
                ds = cat.tiny(shot=shot, name=f'xsx/hcam_l_{channel}').read()
                datasets.append(ds)
            for channel in range(1, 19):
                ds = cat.tiny(shot=shot, name=f'xsx/hcam_u_{channel}').read()
                datasets.append(ds)
            dataset = xr.combine_nested(datasets, concat_dim='n')

            ds = dataset
            ds = ds.isel(time=ds.time > .299)
            ds = ds.isel(time=ds.time < .2995)
            ds['data'].values[ds['data'] > 0.03] = 0

            img = ds['data'].values
            img = (img - img.min()) / (img.max() - img.min())
            img *= 255
            img = img.astype(np.uint8)
            imageio.imwrite(f'local_data/{shot}.png', img)

            task = {
                'data': {
                    'current': f'https://s3.echo.stfc.ac.uk/mast/test/viz/{shot}.csv',
                    'video': f'https://s3.echo.stfc.ac.uk/mast/test/viz/{shot}.mp4',
                    'image': f'https://s3.echo.stfc.ac.uk/mast/test/viz/{shot}.png',
                }
            }

            with Path(f'local_data/{shot}.json').open('w') as f:
                json.dump(task, f)

        except Exception as e:
            print(f"{shot}: {e}")

if __name__ == "__main__":
    main()