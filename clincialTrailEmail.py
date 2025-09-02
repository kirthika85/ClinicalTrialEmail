import streamlit as st
import pandas as pd

# Load the CSV file
df = pd.read_csv("Actual Data.csv")

# Get cohort columns for trials
trial_columns = [col for col in df.columns if col.startswith("COHORT_")]
def cohort_to_name(col):
    return col.replace("COHORT_", "").replace("_", " ").title()
trial_names = {cohort_to_name(col): col for col in trial_columns}

# 1. Clinical trial selection
selected_trial_name = st.selectbox("Select the Clinical Trial", list(trial_names.keys()))
selected_trial_col = trial_names[selected_trial_name]
st.write(f"You selected: {selected_trial_name}")

# 2. Provider count input
count_providers = st.number_input(
    "Count of Providers to be identified?", min_value=1, step=1, value=3
)

# 3. Find Providers button -- store found provider info in session state!
if st.button("Find Providers"):
    trial_df = df[df[selected_trial_col] == "Yes"]
    provider_counts = trial_df["PROVIDER_NAME"].value_counts()
    providers_info = trial_df.groupby("PROVIDER_NAME").agg({"PROVIDER_ID": "first"}).reset_index()
    providers_info["Email"] = providers_info["PROVIDER_NAME"].apply(
        lambda x: f"{x.split()[1].lower()}@doctors.com" if len(x.split())>1 else f"{x.lower()}@doctors.com"
    )
    providers_info["Patient Count"] = providers_info["PROVIDER_NAME"].map(provider_counts)
    providers_info = providers_info.sort_values(by="Patient Count", ascending=False).head(int(count_providers)
    )
    # Save providers_info to session state
    st.session_state.providers_info = providers_info

# 4. Always show provider list and checkboxes if in session state!
if hasattr(st.session_state, "providers_info"):
    st.write("Please find below Provider list. Select those to whom you want the welcome email to be triggered")
    providers_info = st.session_state.providers_info
    for _, row in providers_info.iterrows():
        key = f"provider_{row['PROVIDER_ID']}"
        label = f"{row['PROVIDER_NAME']} | {row['Email']} (Patient Count {row['Patient Count']})"
        st.checkbox(label, key=key)
    # Send Email button
    if st.button("Send Email to Selected Providers"):
        selected_providers = []
        for _, row in providers_info.iterrows():
            key = f"provider_{row['PROVIDER_ID']}"
            if st.session_state.get(key):
                # Generate welcome email snippet
                email_snippet = (
                    f"Subject: Welcome to the Clinical Trial\n"
                    f"Dear {row['PROVIDER_NAME']},\n\n"
                    f"Thank you for participating in the \"{selected_trial_name}\" clinical trial. "
                    f"We are excited to collaborate with you. Your patient count for this trial is {row['Patient Count']}.\n"
                    f"If you have any questions, contact us at your convenience.\n\n"
                    f"Best regards,\nClinical Trials Team"
                )
                selected_providers.append(f"{row['PROVIDER_NAME']} ({row['Email']})")
                st.info(email_snippet)
        if selected_providers:
            st.success(f"Welcome email triggered for: {', '.join(selected_providers)}")
        else:
            st.error("No providers selected!")
