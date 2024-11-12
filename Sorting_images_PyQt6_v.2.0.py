import re
import datetime
from pathlib import Path
class Folder:
    def __init__(self, folder_path):
        self.folder_path = Path(folder_path)
    def path_validation(self):

        if self.folder_path.exists():
            if self.folder_path.is_dir():
                print("Walidacja ścieżki zakończona pomyślnie.")
                return True
            else:
                print("Walidacja ścieżki zakończona niepomyślnie - ścieżka wskazuje na plik.")
                return False
        else:
            print("Walidacja ścieżki zakończona niepomyślnie - ścieżka nie istnieje.")
            return False

    def find_image_video_files(self):
        """
        Function searches for .jpg/.jpeg and .mp4 files in specific path folder.
        It searches for files in path folder and all subdirectories.

        Parameters
        Returns
        -------
        matches_list: type LIST, list of .jpg/.jpeg and .mp4 files in 'path' folder
        non_matches_list: type LIST, list of files not matching
        date_part: type LIST, list of all year-months combinations

        """
        # Define all variables and objects
        matches_list = []
        non_matches_list = []
        date_part = []

        # Define counters to count found images and movies
        counter = 0
        counter_match = 0

        # Define pattern and extensions to search
        pattern = r'.*(?P<year>20[123]\d)(?P<month>[01]\d)(?P<day>[0123]\d).*'
        extensions_to_search = ['*.jpg', '*.jpeg', '*.mp4']

        for extension in extensions_to_search:
            for file in self.folder_path.rglob(extension):
                counter = counter + 1
                # Check if match exists
                matchObj = re.match(pattern=pattern, string=file.stem)
                if matchObj:
                    year = int(matchObj.group('year'))
                    month = int(matchObj.group('month'))
                    day = int(matchObj.group('day'))
                    try:
                        # Try to create date object (additional date validation)
                        datetime.date(year, month, day)
                        # Add what's matched to date_part and the whole file to matches_list
                        date_part.append(str(year) + '-' + str(month))
                        matches_list.append(file.name)
                        counter_match = counter_match + 1
                    except ValueError:
                        continue
                else:
                    # If no match add file name to non_matches_list
                    non_matches_list.append(file.name)
        # Find unique year and month
        date_part = list(set(date_part))
        print("Found", counter, "files from which", round(100 * counter_match / counter, 2),
              "% belong to pictures or movies.")
        # Return all filenames with match and unique year and month
        return matches_list, non_matches_list, date_part

    def run(self):
        validation_flag = self.path_validation()
        # if path is correct
        if validation_flag:
            self.find_image_video_files()


folder_object = Folder("G:\\NTFS-Zdjęcia")
folder_object.run()