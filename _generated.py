import sys
import os
import psycopg2
import psycopg2.extras
import tabulate
from dotenv import load_dotenv
import json
# DO NOT EDIT THIS FILE, IT IS GENERATED BY generator.py

def load_extended_sql_data(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
        return data
def exist(row, V, table):
    for entry in table:
        match = len(V)
        for j in V:
            if row[j] == entry[j]:
                match -=1
                if match == 0:
                    return True
    return False
def createEntry(row, V, F):
    mf_struct = {}
    for i in V:
        mf_struct[i] = None
    for j in F:
        agg = j.split('_')[0]
        match agg:
            case "min":
                mf_struct[j] = sys.float_info.min
            case "max":
                mf_struct[j] = sys.float_info.max
            case "avg":
                mf_struct[j] = [0,0] #sum, count
            case _:
                mf_struct[j] = 0
    for i in V:
        mf_struct[i] = row[i]
    return mf_struct

def query():
    load_dotenv()
    print("Current Working Directory:", os.getcwd())
    #Load the esql data, this would be generated directly from generate
    data = load_extended_sql_data('./cs562-project/data.json')
    # print("Projected Attributes (S):", data['S'])
    S = data['S']
    # print("Number of Grouping Variables (n):", data['n'])
    n = data['n']
    # print("Group By Attributes (V):", data['V'])
    V = data['V']
    # print("Aggregate Functions (F vector):", data['F'])
    F = data['F']
    # print("Predicate Vector:", data['Pred'])
    Pred = data['Pred']
    # print("Having Conditions:", data['H'])
    H = data['H']

    #Connect our environment to PostGresql
    user = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')
    dbname = os.getenv('DBNAME')
    print(user + password + dbname)
    
    conn = psycopg2.connect(host = 'localhost', dbname = dbname, user= user, password= password, port = 5432, cursor_factory=psycopg2.extras.DictCursor)
    cur = conn.cursor()
    cur.execute("SELECT * FROM sales")
    #define variables needed 
    aggregate = {'sum', 'max', 'min', 'count', 'avg'}
    #Populate the mf structure by group by and grouping variables
    '''
    while {
	//read from table sales, then compute all sum

	//doing a table scan for grouping variable 1
}

while{
	//table scan for grouping variable 2
	
}
while{
	//table scan for grouping variable 3
}
ex: 
    while (1)
{
read(a_row)
if (end of table ) break;
if a_row[cust] is in H_table
  	H_table[i].sum_x_q += a_row_quant;
else 
	H_table[i].cust = a_row.cust
	H_table[i].sum_x_q = a_row.quant;
}
if a_row.state = ‘NY’
    '''
    H_table = []
    #Start scanning for group by
    for row in cur:
        if (len(H_table) == 0):
            H_table.append(createEntry(row, V, F))
        #check if it already exist
        if exist(row, V, H_table) == False:
            H_table.append(createEntry(row,V,F))
    #Start scanning for n grouping variables (look at the F table) -> fill the group by variables by scanning 



    
    
    return H_table

def main():
    # Assuming the filename is 'data.json'
    
    print(query())
    
if "__main__" == __name__:
    main()
    
