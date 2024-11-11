
from pathlib import Path
import re
def find_image_video_files(path):
    """
    Function searches for .jpg/.jpeg and .mp4 files in specific path folder.
    It searches for files in path folder and all subdirectories.

    Parameters
    ----------
    path : type STRING, path to look for image and video files

    Returns
    -------
    matches_list: type LIST, list of .jpg/.jpeg and .mp4 files in 'path' folder
    non_matches_list: type LIST, list of files not matching
    date_part: type LIST, list of all year-months combinations
    """

    # Define all variables and objects
    files_list = []
    non_matches_list = []
    date_part = []
    path = Path(path)

    # Define counters to count found images and movies
    counter = 0
    counter_match = 0

    # Define pattern and extensions to search
    pattern = r'.*(?P<year>20[12]\d)(?P<month>[01]\d)(?P<day>[0123]\d).*'
    extensions_to_search = ['*.jpg', '*.jpeg', '*.mp4']

    for extension in extensions_to_search:
        for file in path.rglob(extension):
            counter = counter + 1
            # Check if match exists
            matchObj = re.match(pattern=pattern, string=file.stem)
            if matchObj:
                # If match exists add what's matched to date_part and the whole file to files_list
                date_part.append(matchObj.group('year') + '-' + \
                                 matchObj.group('month'))
                files_list.append(file.name)
                counter_match = counter_match + 1
            else:
                # If no match add file name to non_matches_list
                non_matches_list.append(file.name)
                continue
    # Find unique year and month
    date_part = list(set(date_part))
    print("Found",counter,"files from which", round(100 * counter_match/counter, 2), "% belong to pictures or movies.")
    # Return all filenames with match and unique year and month
    return matches_list, non_matches_list, date_part

