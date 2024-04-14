import pandas as pd

# Set display options to prevent truncation
pd.set_option('display.max_rows', None)  # Display all rows
pd.set_option('display.max_columns', None)  # Display all columns
pd.set_option('display.width', None)  # Auto-detect terminal width

try:
    expenses_df = pd.read_csv('expenses_data.csv')
except FileNotFoundError:
    print("CSV file not found.")
    exit()
except Exception as e:
    print("Error:", e)
    exit()

# Read data from CSV file, specifying date format
expenses_df = pd.read_csv('expenses_data.csv', parse_dates=['Date'], dayfirst=True)

# Clean up leading and trailing spaces in 'Category' column
expenses_df['Category'] = expenses_df['Category'].str.strip()

# Define essential and discretionary categories
essential_categories = ['Supermarket', 'Gas', 'Electricity', 'Mobile phone', 'Household', 'Council tax', 'Car insurance', 'Fuel',
    'Home insurance', 'Home maintenance', 'Water', 'Car maintenance', 'Broadband', 'Medical', 'TV license']
discretionary_categories = ['Counsellor', 'Pets', 'Holidays', 'Investment', 'Eating Out', 'Clothes', 'Pocket money', 'Breakdown', 
    'Travel', 'Fitness', 'Recreation', 'Concerts/Shows', 'Streaming subs', 'Car park', 'Gifts', 'Video games', 'Caravan', 'Reimbursement',
    'Post', 'Hive']

# Define one-off annual expenditure categories
one_off_annual_categories = ['Car insurance']

# Add column indicating whether each category is essential, discretionary, or one-off annual expenditure
expenses_df['Category Type'] = 'Other'
expenses_df.loc[expenses_df['Category'].isin(essential_categories), 'Category Type'] = 'Essential'
expenses_df.loc[expenses_df['Category'].isin(discretionary_categories), 'Category Type'] = 'Discretionary'
expenses_df.loc[expenses_df['Category'].isin(one_off_annual_categories), 'Category Type'] = 'One-off Annual'

# Extract month and year from 'Date'
expenses_df['Month'] = expenses_df['Date'].dt.strftime('%Y-%m')

# Group by month and category, summing up expenses
summary = expenses_df.groupby(['Month', 'Category'])['Amount'].sum().reset_index()

# Group by category and category type, summing up expenses
category_totals = expenses_df.groupby(['Category', 'Category Type'])['Amount'].sum().reset_index()
category_totals = category_totals[category_totals['Amount'] < 0]

# Calculate the number of unique months
num_months = len(expenses_df['Month'].unique())

# Calculate the average per month for each category
category_totals['Average per Month'] = category_totals['Amount'] / num_months
category_totals['Average per Month'] = category_totals['Average per Month'].round(2)

# Extrapolate the total for the year
category_totals['Total for Year'] = category_totals['Average per Month'] * 12
category_totals['Total for Year'] = category_totals['Total for Year'].round(2)

# Sort the DataFrame based on category type
category_totals_sorted = category_totals.sort_values(by=['Amount'], ascending=[True])

# Print Category Totals without the One-off column
print("Category Totals:")
print(category_totals_sorted[['Category', 'Category Type', 'Amount', 'Average per Month', 'Total for Year']].to_string(index=False))

# Group by category type, summing up expenses
category_type_totals = expenses_df.groupby(['Category Type', 'Month'])['Amount'].sum().unstack(fill_value=0)
category_type_totals['Total'] = category_type_totals.sum(axis=1)
category_type_totals = category_type_totals[category_type_totals['Total'] < 0]

# Check if 'One-off Annual' column exists before dropping it
if 'One-off Annual' in category_type_totals.columns:
    category_type_totals = category_type_totals.drop(columns=['One-off Annual'])

# Calculate the average amount per month for each category type
category_type_totals['Average per Month'] = category_type_totals.iloc[:, :-1].mean(axis=1).round(2)

# Extrapolate the category totals for the year
category_type_totals['Total for Year'] = category_type_totals['Average per Month'] * 12

# Calculate the sum of discretionary and essential values for monthly average and yearly total
discretionary_sum = category_type_totals.loc['Discretionary', 'Average per Month'] + category_type_totals.loc['Essential', 'Average per Month']
total_for_year = category_type_totals.loc['Discretionary', 'Total for Year'] + category_type_totals.loc['Essential', 'Total for Year']

# Add the one-off annual expenditure to the totals
discretionary_sum += category_type_totals.loc['One-off Annual', 'Average per Month']
total_for_year += category_type_totals.loc['One-off Annual', 'Total for Year']

# Create a new row for the sum of discretionary and essential values
total_row = pd.DataFrame([[' ', discretionary_sum, total_for_year]], columns=['Total', 'Average per Month', 'Total for Year'], index=['Total (Discretionary + Essential)'])

# Concatenate the new row with the existing DataFrame
category_type_totals = pd.concat([category_type_totals, total_row])

# Specify the columns to fill NaN values for (excluding 'Average per Month' and 'Total for Year')
columns_to_fill = category_type_totals.columns.difference(['Average per Month', 'Total for Year'])

# Fill NaN values in specified columns with 0
category_type_totals[columns_to_fill] = category_type_totals[columns_to_fill].fillna('')

print("\nTotal spending by category type:")
print(category_type_totals)
