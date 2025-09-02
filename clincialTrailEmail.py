import streamlit as st
import pandas as pd

# Load local CSV file
df = pd.read_csv("Actual-Data-1.csv")

# List available clinical trial columns
trial_columns = [col for col in df.columns if col.startswith("COHORT_")]

# Generate readable cohort names for dropdown
def cohort_to_name(col):
    # Remove prefix, replace underscores, capitalize
    name = col.replace("COHORT_", "").replace("_", " ").title()
    return name

trial_names = {cohort_to_name(col): col for col in trial_columns}

# Step 1: Trial selection
selected_trial_name = st.selectbox("Select the Clinical Trial", list(trial_names.keys()))
selected_trial_col = trial_names[selected_trial_name]

st.write(f"You selected: {selected_trial_name}")

# Step 2: How many providers to identify
count_providers = st.number_input("Count of Providers to be identified?", min_value=1, step=1, value=3)
find = st.button("Find Providers")

if find:
    # Filter providers involved in selected cohort
    trial_df = df[df[selected_trial_col] == "Yes"]
    provider_counts = trial_df["PROVIDER_NAME"].value_counts()
    
    # Get provider emails from original data
    providers_info = trial_df.groupby("PROVIDER_NAME").agg({
        "PROVIDER_ID": "first"
    }).reset_index()
    providers_info["Email"] = providers_info["PROVIDER_NAME"].apply(lambda x: f"{x.split()[1].lower()}@doctors.com" if len(x.split())>1 else f"{x.lower()}@doctors.com")
    
    # Combine counts and emails
    providers_info["Patient Count"] = providers_info["PROVIDER_NAME"].map(provider_counts)
    providers_info = providers_info.sort_values(by="Patient Count", ascending=False).head(int(count_providers))

    # Provider selection checkboxes
    selected = []
    st.write("Please find below Provider list. Select those to whom you want the welcome email to be triggered")
    for idx, row in providers_info.iterrows():
        label = f"{row['PROVIDER_NAME']} | {row['Email']} (Patient Count {row['Patient Count']})"
        if st.checkbox(label):
            selected.append(row["PROVIDER_NAME"])

    # Send Email Button
    if st.button("Send Email to Selected Providers"):
        st.success(f"Welcome email triggered for: {', '.join(selected)}")
