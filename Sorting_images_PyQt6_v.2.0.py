import re
import datetime
from pathlib import Path
import pandas as pd
import shutil
from openpyxl.styles import PatternFill

class File:
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
        self.new_row_to_add = []

        # Define counters to count found images and movies and total counts
        self.counter_total = 0
        self.counter_match = 0

        # Define pattern and extensions to search
        self.pattern = r'.*(?P<year>20[123]\d)(?P<month>[01]\d)(?P<day>[0123]\d).*'
        self.extensions_to_search = ['*.jpg', '*.jpeg', '*.mp4']

        print("Starting files analysis...")

        for extension in self.extensions_to_search:
            try:
                # Finds all files with specific extension
                for file in self.source_folder_path.rglob(extension):
                    self.counter_total += 1
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

                            # Join together file attributes with future copy destination folder
                            self.new_row_to_add.append({
                                'filename':str(file.name),
                                'extension':extension,
                                'year':f"{self.year}",
                                'month':f"{self.month:02}",
                                'day':f"{self.day:02}"}
                            )

                            self.counter_match += 1
                        except ValueError:
                            continue
                    else:
                        # If no match add file name to non_matches_list
                        self.non_matches_list.append(file.name)
            except Exception as e:
                print(f"Error processing files: {e}")

        # Generating DataFrame with matches list and saving as an Excel file
        self.photo_video_metadata_df  = pd.DataFrame(self.new_row_to_add, columns=["filename", "extension", "year", "month", "day"])
        self.generateExcelFile(self.photo_video_metadata_df , self.destination_folder_path, "Image and Video Files.xlsx")

        # Generating DataFrame with non matches list and saving as an Excel
        self.files_non_matching = pd.DataFrame(self.non_matches_list, columns = ['filename'])
        self.generateExcelFile(self.files_non_matching, self.destination_folder_path, "Non Image and Video Files.xlsx")

        # Find unique year and month
        self.unique_dates = list(set(self.unique_dates))

        # Prepare matches list
        self.matches_list = self.photo_video_metadata_df .loc[:, 'filename'].drop_duplicates().to_list()

        # Write information about files matches and found
        if self.counter_total > 0:
            print("Found", self.counter_total, "files from which", round(100 * self.counter_match / self.counter_total, 2),
                  "% belong to pictures or movies.")
        else:
            print("No files found.")
        return True
    
    def search_for_copies(self):
        self.list_of_copies = []
        for picture in self.matches_list:
            for file in self.destination_folder_path.rglob(picture):
                # If file has been found add it to the list
                self.list_of_copies.append(file.name)
        return True

    def find_files_to_copy(self):
        self.files_to_copy = list(set(self.matches_list) - set(self.list_of_copies))
        print(f"Among {self.counter_match} files {len(self.files_to_copy)} of them are to be copied.")

    def create_standard_folders(self):
        self.folder_counter = [0, 0]

        for date in self.unique_dates:
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

        if self.folder_counter[0] and self.folder_counter[1] != 0:
            print(f"{self.folder_counter[0]} year folders have been created.")
            print(f"{self.folder_counter[1]} month folders have been created.")
        else:
            print("No standard date folders have been created.")
        return True

    def create_custom_folders(self, event_named_df):
        print("Starting 'create_custom_folders' function...")
        self.folder_counter = [0, 0]
        self.event_named_df = event_named_df
        for row in self.event_named_df.iterrows():
            year_path = self.destination_folder_path / str(row[1]['Year'])
            try:
                year_path.mkdir()
                self.folder_counter[0] += 1
            except FileExistsError:
                pass

            # Reading name from third position and setting a custom path
            custom_path = year_path / str(row[1].iloc[2])
            try:
                custom_path.mkdir()
                self.folder_counter[1] += 1
            except FileExistsError:
                pass
        if self.folder_counter[0] and self.folder_counter[1] != 0:
            print(f"{self.folder_counter[0]} year folders have been created.")
            print(f"{self.folder_counter[1]} custom folders have been created.")
        else:
            print("No custom folders have been created.")
        return True

    def copy_files(self):
        if len(self.files_to_copy) > 0:
            print("Starting copying...")
            for file in self.matches_list:
                if file in self.files_to_copy:
                    # Finding the year and month to copy the file
                    year = self.photo_video_metadata_df .loc[self.photo_video_metadata_df ['filename'] == file, 'year'].iloc[0]
                    month = self.photo_video_metadata_df .loc[self.photo_video_metadata_df ['filename'] == file, 'month'].iloc[0]
                    try:
                        shutil.copy2(self.source_folder_path/file, self.destination_folder_path/year/month)
                    except:
                        print("Errors have been encountered while copying.")
                else:
                    continue
            print("Copying finished")
        else:
            print("Copying will not be performed as there is no files to copy.")
        return True

    def read_event_names_from_pictures(self, reading_range):
        """

        Parameters
        ----------
        reading_range: STRING, Path to folder being a source of folder names according to dates

        Returns
        -------

        """
        self.reading_range = Path(reading_range.replace("\\", "\\\\"))
        self.pattern = r'.*(?P<year>20[123]\d)(?P<month>[01]\d)(?P<day>[0123]\d).*'
        self.extensions_to_search = ['*.jpg', '*.jpeg', '*.mp4']
        self.range_to_add = []

        print("Starting event analysis...")

        # For all extensions defined above do...
        for extension in self.extensions_to_search:
            try:
                # Finds all files with specific extension
                for file in self.reading_range.rglob(extension):
                    self.match_obj = re.match(pattern=self.pattern, string=file.stem)
                    # If match
                    if self.match_obj:
                        # Calculate values
                        self.year = int(self.match_obj.group('year'))
                        self.month = int(self.match_obj.group('month'))
                        self.day = int(self.match_obj.group('day'))
                        self.event_name = file.parent.name
                        self.date = datetime.date(self.year, self.month, self.day)
                        # Every iteration add a next list element as a set
                        self.range_to_add.append({
                            'event_name': self.event_name,
                            'extension': extension,
                            'year': f"{self.year}",
                            'month': f"{self.month:02}",
                            'day': f"{self.day:02}",
                            'date': self.date})
            except Exception as e:
                print(f"There was an error while analyzing the events: {e}")

        # Create a DataFrame with list of sets
        self.event_names_df = pd.DataFrame(self.range_to_add,
                                           columns=["event_name", "extension", "year", "month", "day", "date"])
        # Calculate a maximum and minimum value in the 'window' of grouped values
        self.event_names_df['min_date'] = self.event_names_df.groupby(['event_name', 'year', 'month'])['date'].transform('min')
        self.event_names_df['max_date'] = self.event_names_df.groupby(['event_name', 'year', 'month'])['date'].transform('max')
        # Drop not used columns
        self.event_names_df.drop(columns = ['extension', 'day', 'date'], inplace=True)
        # Drop duplicates
        self.event_names_df.drop_duplicates(inplace=True)
        # Save to Excel file
        self.generateExcelFile(self.event_names_df, self.destination_folder_path, "Event names.xlsx")

    def find_dates_with_no_custom_folder(self):
        print("Starting function checking matching pictures to folders")

        # Convert columns to datetime format
        self.event_names_df['min_date'] = pd.to_datetime(self.event_names_df['min_date'])
        self.event_names_df['max_date'] = pd.to_datetime(self.event_names_df['max_date'])

        # Create w column with date
        self.photo_video_metadata_df['date'] = pd.to_datetime(self.photo_video_metadata_df[['year', 'month', 'day']])

        # Check if date is in range of custom folder and apply custom folder name if true
        self.photo_video_metadata_df['event_name'] = self.photo_video_metadata_df['date'].apply(
            lambda x: self.event_names_df.loc[(x >= self.event_names_df['min_date']) & (x <= self.event_names_df['max_date']), 'event_name'].values[0]
            if not self.event_names_df[(x >= self.event_names_df['min_date']) & (x <= self.event_names_df['max_date'])].empty else None
        )

        # Generate a file with additional column containing matched custom folder
        self.generateExcelFile(self.photo_video_metadata_df,
                               self.destination_folder_path,
                               "Image and Video Files with matched folders.xlsx"
                               )
        return True

    def generateExcelFile(self,
                          dataframe,
                          destination,
                          filename):
        """

        Parameters
        ----------
        dataframe: export DataFrame
        destination: export destination, pathlib.Path Object
        filename: name of the file

        Returns
        -----
        None

        """
        self.destination_path = destination/filename
        try:
            print("Preparing excel file to export.")
            with pd.ExcelWriter(path=self.destination_path,
                                engine='openpyxl',
                                mode='w') as writer:
                dataframe.to_excel(writer, index=False, sheet_name='Arkusz1')

                # Pobierz arkusz
                sheet = writer.sheets['Arkusz1']

                # Dopasowanie szerokości kolumn
                for col in sheet.columns:
                    max_length = max(len(str(cell.value)) for cell in col if cell.value)
                    column = col[0].column_letter  # Pobierz literę kolumny
                    sheet.column_dimensions[column].width = max_length + 2

                # Kolorowanie nagłówków
                header_fill = PatternFill(start_color="DCE6F1", end_color="DCE6F1", fill_type="solid")
                for cell in sheet[1]:
                    cell.fill = header_fill

                print(f"File successfully exported to location {self.destination_path}.")
        except Exception as e:
            print(f"There was an error while exporting the file to excel: {e}")

        return True

    def run(self, event_named_df):
        validation_flag = self.path_validation()
        # if paths are correct
        if validation_flag:
            self.find_image_video_files()
            self.search_for_copies()
            self.find_files_to_copy()
            self.create_standard_folders()
            self.create_custom_folders(event_named_df)
            self.read_event_names_from_pictures("") # Set the path to date and filename source
            self.find_dates_with_no_custom_folder()
            #self.copy_files()
        return True

class ExcelFile:
    def read_from_excel_file(self, path):
        self.path = Path(path.replace("\\", "\\\\"))
        self.event_named_df = pd.read_excel(self.path)

        # Read year from first column, which should contain a date and write it to 'Year' column
        self.event_named_df['Year'] = self.event_named_df.iloc[:, 0].dt.year
        return self.event_named_df

# Main part
if True:
    # Paths definitions
    source_folder_path = r''
    destination_folder_path = r''
    excel_file_path = r''

    # Read custom folders from excel File
    if excel_file_path != "":
        excel_file_obj = ExcelFile()
        event_named_df = excel_file_obj.read_from_excel_file(excel_file_path)
    else:
        # If no path has been defined set empty DataFrame
        event_named_df = pd.DataFrame()

    # Run main program
    file = File(source_folder_path, destination_folder_path)
    file.run(event_named_df)
