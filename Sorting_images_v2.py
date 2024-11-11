
from pathlib import Path
import re
def find_image_video_files(path):
    """
    Function searches for .jpg and .mp4 files in specific path folder.
    For now it considers only files, not subdirectories.

    Parameters
    ----------
    path : type STRING, path to look for image and video files

    Returns
    -------
    files_list: type LIST, list of .jpg/.jpeg and .mp4 files in 'path' folder
    date_part: type LIST, list of all year-months combinations
    """

    files_list = []
    non_matches_list = []
    date_part = []
    path = Path(path)
    for index, file in enumerate(path.iterdir()):
        print(index, ", ", file)
        pattern = r'.*(?P<year>20[12]\d)(?P<month>[01]\d)(?P<day>[0123]\d).*'
        if file.suffix in {'.jpg', '.mp4', '.jpeg'}:
            # Check if match exists
            matchObj = re.match(pattern=pattern, string=file.stem)
            if matchObj:
                # If match exists add what's matched to date_part and the whole file to files_list
                date_part.append(matchObj.group('year') + '-' + \
                                 matchObj.group('month'))
                files_list.append(file.name)
            else:
                # If no match add file name to non_matches_lsit
                non_matches_list.append(file.name)
                continue
    # Find unique year and month
    date_part = list(set(date_part))
    # Return all filenames with match and unique year and month
    return files_list, date_part

result = find_image_video_files("G:\\NTFS-Zdjęcia\\2024\\slub")