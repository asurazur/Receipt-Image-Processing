from PIL import Image
from pytesseract import pytesseract
import mysql.connector
from getpass import getpass

def check_and_add_item(line,items):
    """
        This function checks if a line contains an item, then adds the item to the list
        line : string - a single line in the text
    """
    quantity = int()
    item_name = str()
    total = float()
    #Check if the first substring in the line is a number
    if(len(line.split()) < 3):
        return
    if(line.split()[0].isdigit()):
        quantity = line.split()[0]
    else:
         return
    #check if the last substring's last character is "F"
    if(line.split()[-1][-1] == "F"):
        total = line.split()[-1][:-1]
    else:
        return
    item_name = " ".join(line.split()[1:-1])
    items.append((quantity, item_name, total))

def find_and_store_items(elements):
    """
        elements : list of string - lines in the text 
        return : a list of attributes of items - contains the item's quantity, item_name, and total
    """
    items = []
    for line in elements:
        check_and_add_item(line,items)
    return items

def exportToCSV(fileCSV, db_cursor):
    print("The Receipt Contains the ff:")
    print("{0:<20}{1:<20}{2:<20}{3:>20}".format("ID","Quantity", "Item Name", "Total"), sep = "|")
    print("ID","Quantity", "Item Name", "Total", sep = ",", file = fileCSV)
    for record in db_cursor:
        print ("{0:<20}{1:<20}{2:<20}{3:>20}".format(record[0], record[1], record[2], record[3]), sep="|")
        print (record[0], record[1], record[2], record[3], sep=",", file=fileCSV)

#Item Export to MYSQL
fileCSV = open("receipt.csv","w")
#Open image with PIL
img = Image.open("./Images/711.jpg")
#Extract text from image
text = pytesseract.image_to_string(img, 'eng')
#parse the text then return the valid items
records_to_insert = find_and_store_items(text.split(sep="\n"))
#Save to Database

#Login to local Database
database = mysql.connector.connect(
    host = "localhost",
    user = input("Enter your MYSQL Username: "),
    password = getpass("Enter your MYSQL Password: ")
)

#Create DATABASE
db_cursor = database.cursor()
db_cursor.execute("CREATE DATABASE IF NOT EXISTS receipt")
db_cursor.execute("USE receipt")
db_cursor.execute(
    """CREATE TABLE IF NOT EXISTS items (
        id INT AUTO_INCREMENT PRIMARY KEY,
        quantity INT,
        item_name VARCHAR(255),
        total FLOAT)"""
)
print("Database Created")
#Insert items to Database
db_insert_query = "INSERT IGNORE INTO items (quantity, item_name, total) VALUES (%s, %s, %s)"
db_cursor.executemany(db_insert_query,records_to_insert)
database.commit()
db_cursor.execute("SELECT * FROM items")

#Export items table to receipt file and print to stdout
exportToCSV(fileCSV,db_cursor)
