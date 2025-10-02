
import streamlit as st
import pandas as pd
import datetime
import os
import openpyxl  # Required for working with existing Excel files

# Load Excel file (Reference Data sheet)
excel_file = "Requisition_Template.xlsx"
df_ref = pd.read_excel(excel_file, sheet_name="Reference Data")

# Clean up column names
df_ref.columns = df_ref.columns.str.strip()

# Create display labels (Item - Description)
df_ref['ItemDisplay'] = df_ref['Item'] + " - " + df_ref['Description']

# Create mapping from display to actual Item
item_map = dict(zip(df_ref['ItemDisplay'], df_ref['Item']))

st.title("📝 Requisition Request Form")
st.markdown("Fill out the item(s) you want to request below:")

# Select item using display names (searchable dropdown)
selected_display = st.selectbox("Select Item *", options=list(item_map.keys()), key="selected_item")

# Get actual item code from selected label
item = item_map[selected_display]

# Get the description from Reference Data
description = df_ref.loc[df_ref['Item'] == item, 'Description'].values[0]

# Company dropdown
company_options = {
    "445 - Services": "445",
    "446 - EPC": "446",
    "447 - OTS": "447",
    "549 - HV": "549",
    "550 - SEHV": "550"
}
selected_company_display = st.selectbox("Select Company *", options=list(company_options.keys()))
company_code = company_options[selected_company_display]

# Job/Dept/Eqp/WO dropdown
job_options = ["844607", "844608"]
selected_job = st.selectbox("Select Job/Dept/Eqp/WO *", options=job_options)

# Display the form
with st.form("requisition_form"):
    st.text_input("Description", value=description, disabled=True)
    comment = st.text_input("Comment (optional)")
    quantity = st.number_input("Quantity *", min_value=1, step=1)
    price = st.number_input("Price per unit ($) *", min_value=0.0, format="%.2f")
    need_by_date = st.date_input("Need-by Date *", min_value=datetime.date.today())
    submitted = st.form_submit_button("Submit Requisition")

# # Save submission
# if submitted:
#     new_entry = pd.DataFrame({
#         'Item': [item],
#         'Description': [description],
#         'Comment': [comment],
#         'Quantity': [quantity],
#         'Price': [price],
#         'Need-by Date': [need_by_date.strftime('%Y-%m-%d')],
#         'Company': [company_code],
#         'Job/Dept/Eqp/WO': [selected_job]
#     })
if submitted:
    # Validation checks
    errors = []
    
    # if not comment.strip():
    #     errors.append("Comment is required.")
    
    if not company_code:
        errors.append("Company must be selected.")

    if not selected_job:
        errors.append("Job/Dept/Eqp/WO must be selected.")

    if quantity <= 0:
        errors.append("Quantity must be greater than zero.")

    if price <= 0:
        errors.append("Price must be greater than zero.")

    if need_by_date <= datetime.date.today():
        errors.append("Need-by Date must be in the future.")

    if errors:
        for error in errors:
            st.error(error)
    else:
        # Proceed with saving if no errors
        new_entry = pd.DataFrame({
            'Item': [item],
            'Description': [description],
            'Comment': [comment],
            'Quantity': [quantity],
            'Price': [price],
            'Company': [company_code],
            'Job/Dept/Eqp/WO': [selected_job]
        })

        # Rest of the saving logic...


        # Rest of the saving logic...


    # Try to read existing submissions
    try:
        df_submissions = pd.read_excel(excel_file, sheet_name="Requisition Form")
        df_submissions = pd.concat([df_submissions, new_entry], ignore_index=True)
    except Exception:
        df_submissions = new_entry

    # Write back to the same Excel file
    with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df_ref.to_excel(writer, sheet_name="Reference Data", index=False)
        df_submissions.to_excel(writer, sheet_name="Requisition Form", index=False)

    st.success("Requisition submitted successfully!")
    st.dataframe(new_entry)

    # Update Buyer Import Template right after submission
    df_reference = df_ref.copy()  # Already cleaned
    df_merged = pd.merge(df_submissions, df_reference, on='Item', how='left')

    df_buyer_template = pd.DataFrame({
        "Item Type": df_merged["Item Type"],
        "Item": df_merged["Item"],
        "Description": df_merged["Description_x"],  # Use from Submissions
        "Comment": df_merged["Comment"],
        "WM": df_merged["WM"],
        "Quantity": df_merged["Quantity"],
        "Price": df_merged["Price"],
        "Expected": df_merged["Need-by Date"],
        "Rec Inv": "N",      # Default value
        "Dist": "J",         # Default value
        "Company": df_merged["Company"],
        "Job/Dept/Eqp/WO": df_merged["Job/Dept/Eqp/WO"],
        "Cost Code/Acc/Compon/WI": df_merged["Cost Code/Acc/Compon/WI"],
        "Cat/Tran Code/Exp": df_merged["Cat/Tran Code/Exp"]
    })

    with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df_buyer_template.to_excel(writer, sheet_name="Buyer Import Template", index=False)

# Optional: show existing submissions
try:
    with st.expander("📄 View Past Submissions"):
        st.dataframe(pd.read_excel(excel_file, sheet_name="Requisition Form"))
except Exception:
    pass


# import streamlit as st
# import pandas as pd
# import datetime
# import os
# import openpyxl  # Required for working with existing Excel files

# # Load Excel file (Reference Data sheet)
# excel_file = "Requisition_Template.xlsx"
# df_ref = pd.read_excel(excel_file, sheet_name="Reference Data")

# # Clean up column names
# df_ref.columns = df_ref.columns.str.strip()

# # Create display labels (Item - Description)
# df_ref['ItemDisplay'] = df_ref['Item'] + " - " + df_ref['Description']

# # Create mapping from display to actual Item
# item_map = dict(zip(df_ref['ItemDisplay'], df_ref['Item']))

# st.title("📝 Requisition Request Form")
# st.markdown("Fill out the item(s) you want to request below:")

# # Select item using display names (searchable dropdown)
# selected_display = st.selectbox("Select Item", options=list(item_map.keys()), key="selected_item")

# # Get actual item code from selected label
# item = item_map[selected_display]

# # Get the description from Reference Data
# description = df_ref.loc[df_ref['Item'] == item, 'Description'].values[0]

# # Display the form
# with st.form("requisition_form"):
#     st.text_input("Description", value=description, disabled=True)
#     comment = st.text_input("Comment (optional)")
#     quantity = st.number_input("Quantity", min_value=1, step=1)
#     price = st.number_input("Price per unit ($)", min_value=0.0, format="%.2f")
#     need_by_date = st.date_input("Need-by Date", min_value=datetime.date.today())
#     submitted = st.form_submit_button("Submit Requisition")


# if submitted:
#     new_entry = pd.DataFrame({
#         'Item': [item],
#         'Description': [description],
#         'Comment': [comment],
#         'Quantity': [quantity],
#         'Price': [price],
#         'Need-by Date': [need_by_date.strftime('%Y-%m-%d')]
#     })

#     # Try to read existing submissions
#     try:
#         df_submissions = pd.read_excel(excel_file, sheet_name="Requisition Form")
#         df_submissions = pd.concat([df_submissions, new_entry], ignore_index=True)
#     except Exception:
#         df_submissions = new_entry

#     # Write back to the same Excel file
#     with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
#         df_ref.to_excel(writer, sheet_name="Reference Data", index=False)
#         df_submissions.to_excel(writer, sheet_name="Requisition Form", index=False)

#     st.success("Requisition submitted successfully!")
#     st.dataframe(new_entry)

# # Optional: show existing submissions
# try:
#     with st.expander("📄 View Past Submissions"):
#         st.dataframe(pd.read_excel(excel_file, sheet_name="Requisition Form"))
# except Exception:
#     pass

# #Buyer Import Template---------------------------------------------------------------------------------------
# # Load the required sheets
# df_submissions = pd.read_excel(excel_file, sheet_name="Requisition Form")
# df_reference = pd.read_excel(excel_file, sheet_name="Reference Data")

# # Clean columns
# df_reference.columns = df_reference.columns.str.strip()
# df_submissions.columns = df_submissions.columns.str.strip()

# # Merge Submissions with Reference Data on 'Item'
# df_merged = pd.merge(df_submissions, df_reference, on='Item', how='left')

# # Construct Buyer Import Template DataFrame
# df_buyer_template = pd.DataFrame({
#     "Item Type": df_merged["Item Type"],
#     "Item": df_merged["Item"],
#     "Description": df_merged["Description_x"],  # Use from Submissions
#     "Comment": df_merged["Comment"],
#     "WM": df_merged["WM"],
#     "Quantity": df_merged["Quantity"],
#     "Price": df_merged["Price"],
#     "Expected": df_merged["Need-by Date"],
#     "Rec Inv": "N",      # Default value
#     "Dist": "J",         # Default value
#     "Company": "445",    # Default value
#     "Job/Dept/Eqp/WO": "844607",  # Fill if you track jobs
#     "Cost Code/Acc/Compon/WI": df_merged["Cost Code/Acc/Compon/WI"],
#     "Cat/Tran Code/Exp": df_merged["Cat/Tran Code/Exp"]
# })

# # Save or export to Excel (append as new sheet)
# with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
#     df_buyer_template.to_excel(writer, sheet_name="Buyer Import Template", index=False)

# print("Buyer Import Template updated!")



