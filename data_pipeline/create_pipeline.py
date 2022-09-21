from datetime import datetime
# define data file name
file_name = "funding_amount.csv"
# use generator expression to read each line of data file
lines = (line for line in open(file_name))
# Split each line into a list of values
list_line = (s.rstrip().split(",") for s in lines)
# Use simple next commend to generate column names list which is split forst row
cols = next(list_line)
# creates dictionaries and unites them with a zip() call:
# The keys are the column names cols, the values are the 
# rows in list form, created in line 6.
company_dicts = (dict(zip(cols, data)) for data in list_line)
# filter out company’s series A funding amounts when its round is series A
funding = (
            [int(company_dict["raisedAmt"]), int(company_dict["numEmps"] or 0)]
            for company_dict in company_dicts
            if company_dict["round"] == "b"
          )
# iteration process by calling sum() to get the total amount of series A funding found in the CSV
total_series_a = sum([fund[0] for fund in funding])
total_num_emp = sum([fund[1] for fund in funding]) 
# generate final results
print(f"Total series A fundraising: ${total_series_a} Total employees: {total_num_emp}")