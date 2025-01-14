import re
import datetime
from pathlib import Path
import pandas as pd
import shutil
from openpyxl.styles import PatternFill

class File:
    def __init__(self, source_folder_path, destination_folder_path, event_named_df_prepared, event_named_df, standard_or_custom_folder, copy_files):
        self.source_folder_path = Path(source_folder_path.replace("\\", "\\\\"))
        self.destination_folder_path = Path(destination_folder_path.replace("\\", "\\\\"))
        self.event_named_df_prepared = event_named_df_prepared
        self.event_named_df = event_named_df
        self.standard_or_custom_folder = standard_or_custom_folder
        self.copy_files = copy_files
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

        print("Starting files analysis in order to find pictures and movies...")

        for extension in self.extensions_to_search:
            try:
                # Finds all files with specific extension
                for file in self.source_folder_path.rglob(extension):
                    # Count all files
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
                                'day':f"{self.day:02}",
                                'date': datetime.date(self.year, self.month, self.day)
                            })
                            self.counter_match += 1
                        except ValueError:
                            continue
                    else:
                        # If no match add file name to non_matches_list
                        self.non_matches_list.append(file.name)
            except Exception as e:
                print(f"Error processing files: {e}")

        # Generating DataFrame with matches list and saving as an Excel file
        self.photo_video_metadata_df  = pd.DataFrame(self.new_row_to_add, columns=["filename", "extension", "year", "month", "day", "date"])
        self.generateExcelFile(self.photo_video_metadata_df , self.destination_folder_path, "Image and Video Files.xlsx")

        # Generating DataFrame with non matches list and saving as an Excel
        self.files_non_matching = pd.DataFrame(self.non_matches_list, columns = ['filename'])
        self.generateExcelFile(self.files_non_matching, self.destination_folder_path, "Non Image and Video Files.xlsx")

        # Find unique year and month
        self.unique_dates = list(set(self.unique_dates))

        # Prepare matches list
        self.matches_list = self.photo_video_metadata_df.loc[:, 'filename'].drop_duplicates().to_list()

        # Write information about files matches and found
        if self.counter_total > 0:
            print("Found", self.counter_total, "files from which", round(100 * self.counter_match / self.counter_total, 2),
                  "% belong to pictures or movies.")
        else:
            print("No files found.")
        return True
    
    def search_for_copies(self):
        print("search")
        self.list_of_copies = []
        print("Ok")
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

    def create_custom_folders(self):
        print("Starting 'create_custom_folders' function...")
        self.folder_counter = [0, 0]
        for index, row in self.event_named_df.iterrows():
            print(type(row['date']))
            year_path = self.destination_folder_path / str(row['date'].year)
            # Creating year folder if not exist
            try:
                year_path.mkdir()
                self.folder_counter[0] += 1
            except FileExistsError:
                pass

            # Creating custom folder based on the file
            custom_path = year_path / row['custom_folder_name']
            print(custom_path)
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

        # Veryfing if the pictures or videos are to be copies
        self.photo_video_metadata_with_no_custom_folders = self.photo_video_metadata_df.loc[self.photo_video_metadata_df['filename'].isin(self.files_to_copy), :]

        # Create a column with date
        self.photo_video_metadata_with_no_custom_folders['date'] = pd.to_datetime(self.photo_video_metadata_with_no_custom_folders[['year', 'month', 'day']])

        # Convert columns to datetime format
        self.event_names_df['min_date'] = pd.to_datetime(self.event_names_df['min_date'])
        self.event_names_df['max_date'] = pd.to_datetime(self.event_names_df['max_date'])

        # Check if date is in range of custom folder and apply custom folder name if true
        self.photo_video_metadata_with_no_custom_folders['event_name'] = self.photo_video_metadata_with_no_custom_folders['date'].apply(
            lambda x: self.event_names_df.loc[(x >= self.event_names_df['min_date']) & (x <= self.event_names_df['max_date']), 'event_name'].values[0]
            if not self.event_names_df[(x >= self.event_names_df['min_date']) & (x <= self.event_names_df['max_date'])].empty else None
        )

        # After comparing the dates above I remove time part from datetime object
        self.photo_video_metadata_with_no_custom_folders['date'] = self.photo_video_metadata_with_no_custom_folders['date'].dt.date

        # Present only those files with no custom folder matching and unique
        self.photo_video_metadata_with_no_custom_folders = self.photo_video_metadata_with_no_custom_folders.loc[
            self.photo_video_metadata_with_no_custom_folders['event_name'].isna(), ['date']].\
            drop_duplicates().\
            sort_values(by='date')

        # Join together restricted DataFrame with its source to find random filename
        self.photo_video_metadata_with_no_custom_folders = pd.merge(
            self.photo_video_metadata_with_no_custom_folders,
            self.photo_video_metadata_df,
            on='date'
        )
        self.photo_video_metadata_with_no_custom_folders = self.photo_video_metadata_with_no_custom_folders.loc[:, ['date', 'filename']]

        self.photo_video_metadata_with_no_custom_folders  = self.photo_video_metadata_with_no_custom_folders.\
            groupby(by=['date']).first().\
            reset_index()

        # Adding a column to set custom folder name
        self.photo_video_metadata_with_no_custom_folders['custom_folder_name'] = ""

        # Renaming columns
        self.photo_video_metadata_with_no_custom_folders.columns = ['date', 'random_filename', 'custom_folder_name']

        # Generate a file with additional column containing matched custom folder
        self.generateExcelFile(self.photo_video_metadata_with_no_custom_folders,
                               self.destination_folder_path,
                               "Image and Video Files not matching to custom folders.xlsx"
                               )
        return True

    def verify_external_excel_custom_folder(self):

        # Default settings
        self.customs_ready = 1
        for index, event in self.photo_video_metadata_with_no_custom_folders.iterrows():
            if not self.event_named_df.empty:
                if event['random_filename'] not in self.event_named_df['random_filename']:
                    print(f"Custom folder missing for filename: {event['random_filename']}")
                    # If not all event has been declared change the flag
                    self.customs_ready = 0
            else:
                continue
        return True

    def build_custom_source(self):
        self.custom_folder_df = pd.concat(
            [self.event_names_df, self.event_named_df_prepared],
            axis=0
        )
        self.custom_folder_df.drop_duplicates()
        # Generate a file with additional column containing matched custom folder
        self.generateExcelFile(self.custom_folder_df,
                               self.destination_folder_path,
                               "Image and Video Files custom folders total.xlsx"
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

    def run(self):
        validation_flag = self.path_validation()
        # If paths are correct
        if validation_flag:

            # Find and count image and video files. Add these items to self.self.photo_video_metadata_df and self.matches_list
            # and self.files_non_matching. Create unique list of year-month combination based on the pictures.
            self.find_image_video_files()

            # Find all files from self.matches_list in destination location and create self.list_of_copies having all found copies
            self.search_for_copies()

            # Create self.files_to_copy having files to be copied based on self.matches_list and self.list_of_copies
            self.find_files_to_copy()

            if self.standard_or_custom_folder == 1:
                # Creating custom folders if external excel file has been declared
                self.create_custom_folders()

            if self.standard_or_custom_folder == 2:
                # Creating standard folders basen on combination of year and month
                self.create_standard_folders()

            # Create a DataFrame building a source of custom event to dates matches, based on the segregated pictures
            # and write it to self.event_names_df
            self.read_event_names_from_pictures("") # Set the path to date and filename source

            # Try to join together pictures and videos from source with custom folders from function above
            self.find_dates_with_no_custom_folder()

            # Verify if all missing files and have the custom folder names declared
            self.verify_external_excel_custom_folder()

            # Join together external Excel file Custom Folders source with specified folder source
            self.build_custom_source()

            # Check if pictures and videos were not customized in external Excel Folder
            # Copy files from list of self.files_to_copy to destination location (based on year-month so far)
            if self.copy_files == 1:
                if self.standard_or_custom_folder == 1:
                    if self.customs_ready == 1:
                        print("Copying will now be performed. Type: custom")
                        self.copy_files()
                    else:
                        print("You need to declare custom folder names in external file before continuing")
                elif self.standard_or_custom_folder == 2:
                    print("Copying will now be performed. Type mixed: both standard and custom")
                    self.copy_files()
            elif self.copy_files == 0:
                print("Files will not be copied as no copying disposition has been expected ")
            else:
                print("Copying operation not defined")
        return True

class ExcelFile:

    def __init__(self, excel_file_path):
        self.excel_file_path = Path(excel_file_path.replace("\\", "\\\\"))

    def path_validation(self):
        self.folder_paths = [self.excel_file_path]
        for index, self.path in enumerate(self.folder_paths):
            if self.path.exists():
                if self.path.is_file():
                    print(f"Nr {index + 1} path validation successful.")
                else:
                    print(f"Nr {index + 1} path validation unsuccessful - path indicates file.")
                    return False
            else:
                print(f"Nr {index + 1} path validation unsuccessful - path does not exist.")
                return False
        return True

    def read_from_excel_file(self):
        self.event_named_df = pd.read_excel(self.excel_file_path)
        self.event_named_df['date'] = pd.to_datetime(self.event_named_df['date'])
        return self.event_named_df

    def prepare_the_file(self):
        # Creating a view with events grouped and with minimum and maximum dates
        self.event_named_df['min_date'] = self.event_named_df.groupby(['custom_folder_name'])['date'].transform('min')
        self.event_named_df['max_date'] = self.event_named_df.groupby(['custom_folder_name'])['date'].transform('max')
        self.event_named_df['year'] = self.event_named_df['date'].dt.year.astype(str).str.zfill(2)
        self.event_named_df['month'] = self.event_named_df['date'].dt.month.astype(str).str.zfill(2)
        self.event_named_df_prepared = self.event_named_df.loc[:, ['custom_folder_name', 'year', 'month', 'min_date', 'max_date']]
        self.event_named_df_prepared.columns = ['event_name', 'year', 'month', 'min_date', 'max_date']
        self.event_named_df_prepared.drop_duplicates()

    def run(self):
        validation_flag = self.path_validation()
        # If paths are correct
        if validation_flag:
            self.event_named_df = self.read_from_excel_file()
            self.prepare_the_file()
            print(f"File prepared: {self.event_named_df.head()}")
        else:
            print("There was an error with path")
        return self.event_named_df, self.event_named_df_prepared

# Main part
if True:
    ######################################

    # Paths definitions to be defined
    source_folder_path = r''
    destination_folder_path = r''
    excel_file_path = r''

    # Flag for creating standard or custom folders
    # 1 - create only custom folders
    # 2 - create custom folders and standard folders if custom does not exist
    standard_or_custom_folder = 1

    # Copy Files
    # 1 - copy files
    # 0 - only analyze
    copy_files = 0

    #######################################

    # Read custom folders from excel File

    # If custom folders have been defined
    if excel_file_path != "":
        excel_file_obj = ExcelFile(excel_file_path)
        event_named_df, event_named_df_prepared = excel_file_obj.run()

    # In other cases
    else:
        # If no path has been defined set empty DataFrame
        event_named_df = pd.DataFrame()
        event_named_df_prepared = pd.DataFrame()

    # Anyway run main program starting with creating File Class object
    file = File(source_folder_path,
                destination_folder_path,
                event_named_df_prepared,
                event_named_df,
                standard_or_custom_folder,
                copy_files)

    # After creating File Class object start 'run' method on that File Class object
    file.run()
