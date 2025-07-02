import csv

# List of keywords related to Computer Science branches
cs_keywords = [
    'computer', 'cs', 'data sc', 'data science', 'ai', 'artificial intelligence',
    'cyber security', 'info', 'information science', 'machine learning', 'data engineering'
]

def is_cs_branch(branch_name):
    name = branch_name.lower()
    return any(kw in name for kw in cs_keywords)

def append_cs_label(branch_name):
    if 'computer science' in branch_name.lower():
        return branch_name
    return f"{branch_name} (Computer Science)"

input_file = 'cleaned_cutoff_data_latest.csv'
output_file = 'cleaned_cutoff_data_latest_cs.csv'

with open(input_file, 'r', encoding='utf-8', newline='') as infile, \
     open(output_file, 'w', encoding='utf-8', newline='') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)
    header = next(reader)
    writer.writerow(header)
    branch_idx = header.index('Branch Name')
    for row in reader:
        branch_name = row[branch_idx]
        if is_cs_branch(branch_name):
            row[branch_idx] = append_cs_label(branch_name)
        writer.writerow(row)

print(f"Updated file written to {output_file}")
