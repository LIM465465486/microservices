# Importing the required libaries
import pypyodbc
import csv
import win32com.client as win32
import time

# Setting up the Connection to the SQL Server
cnxn = pypyodbc.connect("Driver= {SQL Server Native Client 11.0};"
                    "Server=sql2012;"
                    "Database=Client;"
                    "Trusted_Connection=yes;")

cursor = cnxn.cursor()
data = cursor.execute("EXEC usp_rpt_QuestionFile") #Running the SP and housing the data
headers = [tuple[0] for tuple in data.description] # Getting the field names out of the SP
timestr = time.strftime("%Y%m%d") # Storing the current date
path = "Y:\Client Files\Client\Perpetual\Questions\Client QuestionsTest"+timestr+".csv" # Where the file will be saved
f = csv.writer(open(path, "wb"), delimiter=",")
f.writerow(headers) #Writing the field names as the first row to the CSV
for row in data: #Appending the data to the file
    f.writerow(row)


with open(path, "wb") as f:
    wtr = csv.writer(f, delimiter=",")
    wtr.writerow(headers) #Writing the field names as the first row to the CSV
    wtr.writerows(data)