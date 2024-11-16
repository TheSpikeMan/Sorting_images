import re
import os
import datetime
from pathlib import Path

class Folder:
    def __init__(self, source_folder_path, destination_folder_path):
        self.source_folder_path = Path(source_folder_path.replace("\\", "\\\\"))
        self.destination_folder_path = Path(destination_folder_path.replace("\\", "\\\\"))
    def path_validation(self):
        self.folder_paths = [self.source_folder_path, self.destination_folder_path]
        for index, self.path in enumerate(self.folder_paths):
            if self.path.exists():
                if self.path.is_dir():
                    print(f"Nr {index + 1} path validation successful.")
                else:
                    print(f"Nr {index + 1} path validation unsuccessful - path indicates file.")
                    return False
            else:
                print(f"Nr {index + 1} path validation unsuccessful - path does not exist.")
                return False
        return True
    def find_image_video_files(self):

        # Define all variables and objects
        self.matches_list = []
        self.non_matches_list = []
        self.unique_dates = []

        # Define counters to count found images and movies
        self.counter = 0
        self.counter_match = 0

        # Define pattern and extensions to search
        self.pattern = r'.*(?P<year>20[123]\d)(?P<month>[01]\d)(?P<day>[0123]\d).*'
        self.extensions_to_search = ['*.jpg', '*.jpeg', '*.mp4']

        for extension in self.extensions_to_search:
            try:
                for file in self.source_folder_path.rglob(extension):
                    self.counter += 1
                    # Check if match exists
                    self.match_obj = re.match(pattern=self.pattern, string=file.stem)
                    if self.match_obj:
                        self.year = int(self.match_obj.group('year'))
                        self.month = int(self.match_obj.group('month'))
                        self.day = int(self.match_obj.group('day'))
                        try:
                            # Try to create date object (additional date validation)
                            datetime.date(self.year, self.month, self.day)

                            # Add what's matched to unique_dates and the whole file to matches_list
                            self.unique_dates.append(f"{self.year}-{self.month:02}")
                            self.matches_list.append(file.name)
                            self.counter_match += 1
                        except ValueError:
                            continue
                    else:
                        # If no match add file name to non_matches_list
                        self.non_matches_list.append(file.name)
            except Exception as e:
                print(f"Error processing files: {e}")
        # Find unique year and month
        self.unique_dates = list(set(self.unique_dates))

        # Write information about files matches and found
        if self.counter > 0:
            print("Found", self.counter, "files from which", round(100 * self.counter_match / self.counter, 2),
                  "% belong to pictures or movies.")
        else:
            print("No files found.")
        # Return all filenames with match and unique year and month
        return self.matches_list, self.non_matches_list, self.unique_dates
    
    def search_for_copies(self, matches_list):
        self.list_of_copies = []
        for picture in matches_list:
            for file in self.destination_folder_path.rglob(picture):
                # If file has been found add it to the list
                self.list_of_copies.append(file.name)
        return self.list_of_copies

    def find_files_to_copy(self, list_of_copies, matches_list ):
        self.files_to_copy = list(set(matches_list) - set(list_of_copies))
        print(f"Among {self.counter_match} files {len(self.files_to_copy)} of them are to be copied.")

    def create_folders(self, unique_dates):
        self.folder_counter = [0, 0]

        for date in unique_dates:
            # Split date once to get year and month
            year, month = date.split("-")

            # Create main path for the year
            year_path = self.destination_folder_path / year
            try:
                year_path.mkdir()
                self.folder_counter[0] += 1
            except FileExistsError:
                pass

            # Create sub-folder path for the month
            month_path = year_path / month
            try:
                month_path.mkdir()
                self.folder_counter[1] += 1
            except FileExistsError:
                pass

        print(f"{self.folder_counter[0]} year folders have been created.")
        print(f"{self.folder_counter[1]} month folders have been created.")
        return True

    def run(self):
        validation_flag = self.path_validation()
        # if path is correct
        if validation_flag:
            matches_list, non_matches_list, unique_dates = self.find_image_video_files()
            list_of_copies = self.search_for_copies(matches_list)
            # self.find_files_to_copy(list_of_copies, matches_list)
            self.create_folders(unique_dates)

# Main part
if True:
    # Paths definitions
    source_folder_path = r'G:\Do segregacji 2024'
    destination_folder_path = r'G:\Folder testowy'

    object = Folder(source_folder_path, destination_folder_path)
    object.run()
