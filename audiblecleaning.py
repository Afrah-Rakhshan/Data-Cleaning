import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# %matplotlib inline

"""importing file from google drive"""

from google.colab import drive
drive.mount('/content/drive')

"""Reading the CSV file and printing the head and description"""

# Replace this with the path to your CSV file
csv_file_path = '/content/drive/MyDrive/ColabNotebooks/DataCleaning/audible_uncleaned.csv'

# Read the CSV file
df = pd.read_csv(csv_file_path)

# Show the first few rows of the dataframe
print(df.head())
df.describe()

#checking if there are any duplicates
df.duplicated().sum()

#removing string writtenby from column author
df['author'] = df['author'].str.replace('Writtenby:','')
df.author.sample(5)

#adding space between first name and last name in author column
df['author'] = df['author'].str.replace(pat = r"(\w)([A-Z])", repl = r"\1 \2", regex=True)
df.author.sample(5)

#creating a new data frame which has the authors column seperated if there are multiple authors to a book
df2 = pd.concat([df['name'],
                df['author'].str.split(',', expand=True).add_prefix('author'),
                df.loc[:,['narrator', 'time', 'releasedate', 'language', 'stars', 'price']]],
                axis=1
)

print(df2.head())

#missing values in all author columns of df2
df2.loc[:,['author0','author1','author2','author3']].isnull().sum()

# removing narratedby from narrtor column and spacing between fname and lname
df2['narrator'] = df2['narrator'].str.replace(pat='Narratedby:', repl='')

df2['narrator'] = df2['narrator'].str.replace(pat = r'(\w)([A-Z])', repl= r'\1 \2', regex=True)

df2.narrator.sample(5)

#operations on time column

#replace all numbers with blanks
time_column = df['time'].str.replace(pat = r'[0-9]', repl = '', regex = True)
#keep only unique patterns
time_column.drop_duplicates()

#finding rows with 'less than x duration' , case = False is for case insensitive
less_than_duration = df2[df2.time.str.contains(pat = 'less than', case = False)].index
#check all unique values with 'less than' pattern
df2.time[less_than_duration].drop_duplicates()

#we understand after executing that there is only kind of value in this pattern - 'less than 1 minute'

#creating columns to seperate hours and minutes
df2['hour_component'] = 0
df2['min_component'] = 0

#extracting hours and mins separately
df2['hour_component'] = df2.time.str.extract(pat = r'^(\d+) hr')
df2['min_component'] = df2.time.str.extract(pat = r'(\d+) min')

df2.loc[:,['time', 'hour_component', 'min_component']].sample(5)

#rremoving NaN values
df2['hour_component'] = df2['hour_component'].fillna(0)
df2['min_component'] = df2['min_component'].fillna(0)

df2.loc[[328,5532,1583], ['time', 'hour_component', 'min_component']]

#convert the hour and min column to int type
df2 = df2.astype({'hour_component':'int','min_component':'int'})

df2.info()

df2.releasedate.sample(5)

#day component- dd
#check if any value in day part > 31.
any(df2.releasedate.str.extract(pat = r'^(\d+)-').drop_duplicates().astype(int) > 31)

#check for inconsistencies in month of release date
#Check to see whether middle values (months) contain any number > 12
#all unique months.
any((df2.releasedate.str.extract(pat = r'-(\d+)-').drop_duplicates()).astype(int) > 12)

#check inconsistencies in year value of release date
#future release date is also present, hence values 25 for year 2025, 24 for year 2024...
df2.releasedate.str.extract(pat = r'-(\d+)$').drop_duplicates()

#convert release-date from string to date type
df2.releasedate = pd.to_datetime(df2.releasedate, format = '%d-%m-%y')
#checking data types again
df2.info()

#language column
print(df2.language.drop_duplicates().tolist())

#make language names uniform by capitalizing the first letter.
df2.language = df2.language.str.title()

df2.language.sample(5)

#split stars column into 2
df2[['stars_out_of_5', 'total_ratings']] = df2.stars.str.split('stars', expand = True)

#glimpse of the separated values
df2.loc[:,['stars','stars_out_of_5', 'total_ratings']].head(4)

#replace 'Not rated yet' rows with NA

#rows with not yet rated value
not_rated_rows = df2[df2.stars_out_of_5.str.contains(pat = 'Not rated yet', case = False)].index
#replace 'Not yet rated' and 'None' with NA
df2.loc[not_rated_rows,['stars_out_of_5', 'total_ratings']] = np.nan

#replace 'out of 5' with ''
df2.stars_out_of_5 = df2.stars_out_of_5.str.replace(pat = ' out of 5', repl = '')
#replace 'ratings' with ''
df2.total_ratings = df2.total_ratings.str.replace(pat = r' ratings| rating', repl = '', regex = True)
#remove ',' from ratings. e.g. 1,200 becomes 1200
df2.total_ratings = df2.total_ratings.str.replace(pat = ',', repl = '')

#convert both columns to float type as NaN cannot be converted to int
df2 = df2.astype({'stars_out_of_5':'float', 'total_ratings':'float'})

#convert price to float type

#replace 'free' with 0
df2.price = df2.price.str.replace(pat = 'free', repl = '0', case = False)
#remove ',' from the values
df2.price = df2.price.str.replace(pat = ',', repl = '')
#convert to float
df2.price = df2.price.astype(float)

#renaming columns author0 to author1, author1 to author2 etc.
df2.rename(columns = {'author0':'author_1', 'author1':'author_2', 'author2':'author_3', 'author3':'author_4',
                               'releasedate': 'release_date'}, inplace = True)

#final dataframe with relevant columns
cleaned_df = df2.loc[:,['name', 'author_1', 'author_2', 'author_3', 'author_4', 'narrator', 'release_date',
                                 'hour_component', 'min_component', 'language', 'stars_out_of_5', 'total_ratings', 'price']]

cleaned_df.head(3)