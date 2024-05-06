import subprocess


def main():
    """
    This is the generator code. It should take in the MF structure and generate the code
    needed to run the query. That generated code should be saved to a 
    file (e.g. _generated.py) and then run.
    """

    helpers = """
def load_extended_sql_data(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
        return data

def exist(row, V, table):
    for index, entry in enumerate(table):
        match = len(V)
        for j in V:
            if row[j] == entry[j]:
                match -=1
                if match == 0:
                    return index
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

def meet_conditions(row, conditions, initial ): #missing checking for aggregate
    for i in conditions:
        parts = i.split()
        if (len(parts) == 3 and initial):
            try:
                e = eval(f"{row[parts[0]]} {parts[1]} {parts[2]}")
            except:
                e = eval(f"'{row[parts[0]]}' {parts[1]} {parts[2]}")
            if not e:
                return False
        elif (len(parts) == 3):
            try:
                e = eval(f"{row[parts[0].split('_')[1]]} {parts[1]} {parts[2]}")
            except:
                e = eval(f"'{row[parts[0].split('_')[1]]}' {parts[1]} {parts[2]}")
            if not e:
                return False
    return True

def read_input():
  # S like cust, sum_1_quant, sum_2_quant, sum_3_quant
  S = input("SELECT ATTRIBUTE(S): ").replace(" ", "").split(",")

  # n is an integer
  n = int(input("NUMBER OF GROUPING VARIABLES(n): ").replace(" ", "").strip())

  # V like cust, prod
  V = input("GROUPING ATTRIBUTES(V): ").replace(" ", "").split(",")

  # F like sum_1_quant, avg_1_quant, sum_2_quant, sum_3_quant, avg_3_quant
  F = input("F-VECT([F]): ").replace(" ", "").split(",")

  # Pred is all the predicates, so enter comma separated conditions
  # Press enter when you are done with predicates
  # Note: 1st condition can be the where clause (0th grouping variable)
  Pred = []
  data = input("SELECT CONDITION-VECT([sigma]): ").strip().replace(", ", ",")
  while data:
    Pred.extend([data.strip().replace(", ", ",").split(",")])
    data = input("SELECT CONDITION-VECT([sigma]): ")
    
  # H like sum_1_quant > 2 * sum_2_quant
  H = input("HAVING_CONDITION(H): ").strip()
  return {"S": S, "n": n, "V": V, "F": F, "Pred": Pred, "H": H}
    """

    # Note: The f allows formatting with variables.
    #       Also, note the indentation is preserved.
    tmp = f"""
import sys
import os
import psycopg2
import psycopg2.extras
import tabulate
from dotenv import load_dotenv
import json

{helpers}

# DO NOT EDIT THIS FILE, IT IS GENERATED BY generator.py
# Dict interpolation needs double curly brackets for f-string
aggregate = {{'sum' : 0, 'max': 0, 'min': 0 , 'count': 0, 'avg':[0,0]}}

#Load the esql data, this would be generated directly from generate
data = load_extended_sql_data('data.json')
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

def query():
    load_dotenv()

    user = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')
    dbname = os.getenv('DBNAME')

    conn = psycopg2.connect(dbname=dbname, user=user, password=password,
                            cursor_factory=psycopg2.extras.DictCursor)
    cur = conn.cursor()
    cur.execute("SELECT * FROM sales")

    #define variables needed 
    
    #Populate the mf structure by group by and grouping variables
    # TODO: ~~~~


    H_table = []
    #Check if we have the 0th grouping variables (original table)
    initial = False if Pred[0][0][0].isdigit() else True
        
    #Start scanning for group by attributes
    for row in cur:
        if initial and not meet_conditions(row, Pred[0], initial):
            continue
        if (len(H_table) == 0):
            H_table.append(createEntry(row, V, F))
        #check if it already exist
        if isinstance(exist(row, V, H_table),bool):
            H_table.append(createEntry(row,V,F))
        aggregate['sum'] += row['quant']
        aggregate['count'] += 1
        aggregate['max'] = max(aggregate['max'],row['quant'])
        aggregate['min'] = min(aggregate['min'],row['quant'])
        aggregate['avg'] = [aggregate['avg'][0] + row['quant'], aggregate['avg'][1]+1]
    #Start scanning for n grouping variables (look at the F table) -> fill the group by variables by scanning 
    
    
    for i in F:
        #reset cursor
        cur.scroll(0,'absolute')
        predicate = i.split('_')
        
        for row in cur:
            #extract index of aggregate in pred
            idx = int(predicate[1]) if initial else int(predicate[1])-1
            #if row matches with an entry in H_table, check predicate and compute
            index = exist(row,V,H_table)
            if isinstance(index,int) and meet_conditions(row, Pred[idx], False):
                if initial and not meet_conditions(row, Pred[0], initial):
                    continue
                match predicate[0]:
                    case 'sum':
                        H_table[index][i] += row['quant']
                    case 'count':
                        H_table[index][i] += 1
                    case 'avg':
                        temp = H_table[index][i]
                        H_table[index][i] =  [temp[0] + row['quant'], temp[1] + 1]
                    case 'min':
                        H_table[index][i] = min(H_table[index][i], row['quant'])
                    case 'max':
                        H_table[index][i] = max(H_table[index][i], row['quant'])
        if predicate[0] == 'avg':
            for r in H_table:
                r[i] = r[i][0] / r[i][1]
    _global = []
    for index, entry in enumerate(H_table):
        _global.append(entry)
    
    return tabulate.tabulate(_global,
                        headers="keys", tablefmt="psql")

def main():
    print(query())
    
if "__main__" == __name__:
    main()
    """

    # Write the generated code to a file
    open("_generated.py", "w").write(tmp)
    # Execute the generated code


if "__main__" == __name__:
    main()
