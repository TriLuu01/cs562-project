import subprocess

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
  data = input("SELECT CONDITION-VECT([σ]): ").strip().replace(", ", ",")
  while data:
    Pred.extend([data.strip().replace(", ", ",").split(",")])
    data = input("SELECT CONDITION-VECT([σ]): ")
    
  # H like sum_1_quant > 2 * sum_2_quant
  H = input("HAVING_CONDITION(H): ").strip()
  return {"S": S, "n": n, "V": V, "F": F, "Pred": Pred, "H": H}
   
def main():
    """
    This is the generator code. It should take in the MF structure and generate the code
    needed to run the query. That generated code should be saved to a 
    file (e.g. _generated.py) and then run.
    """

    body = """
    for row in cur:
        if row['quant'] > 10:
            _global.append(row)
    """

    # Note: The f allows formatting with variables.
    #       Also, note the indentation is preserved.
    tmp = f"""
import os
import psycopg2
import psycopg2.extras
import tabulate
from dotenv import load_dotenv

# DO NOT EDIT THIS FILE, IT IS GENERATED BY generator.py

def query():
    load_dotenv()

    user = os.getenv('USER')
    password = os.getenv('PASSWORD')
    dbname = os.getenv('DBNAME')

    conn = psycopg2.connect("dbname="+dbname+" user="+user+" password="+password,
                            cursor_factory=psycopg2.extras.DictCursor)
    cur = conn.cursor()
    cur.execute("SELECT * FROM sales")
    
    _global = []
    {body}
    
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
    subprocess.run(["python", "_generated.py"])


if "__main__" == __name__:
    main()
