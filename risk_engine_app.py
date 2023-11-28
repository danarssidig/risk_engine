import streamlit as st
import pandas as pd
import locale
import folium
from streamlit_folium import st_folium

# Read the CSV file into a DataFrame
df_risk_engine = pd.read_csv('df_risk_engine.csv')

# Calculate the maximum threshold dynamically
max_threshold = round(df_risk_engine['% Std Dev'].max())

# Section 1: Title and Introduction
st.title("Appraiser Risk Engine (Beta)")
st.markdown("### Derived from Tangerang City valuation reports.")

# Adding two line spaces
st.text("")  # One line space
st.text("")  # Another line space

# Section 2: Instructions for Setting Threshold
st.write("### Step 1: Setting Deviation Threshold")
st.write("###### Please set the thresold for value opinion deviation")
#st.write(f"Input value between 100 to {max_threshold}")

# Input box for the threshold value
threshold_input = st.slider(" ", 100, max_threshold)


# Initialize lists to store results
num_report_anomalies = 0
num_appraiser_anomalies = 0

# Filter the DataFrame for rows where '% Std Dev' is higher than the threshold
filtered_anomaly_df = df_risk_engine[df_risk_engine['% Std Dev'] > threshold_input]

# Calculate the number of anomalies
num_report_anomalies = len(filtered_anomaly_df)
num_appraiser_anomalies = filtered_anomaly_df['Penanda Tangan'].nunique()

# Display the results
st.write(f"###### Analysis results for a {threshold_input} threshold:")
st.write(f"{num_report_anomalies} anomalies found in property reports.")
st.write(f"{num_appraiser_anomalies}  anomaly appraisers are identified.")

st.text("")  # Another line space

# Section 3: Instructions for Summarizing Anomaly Appraisers
st.write("### Step 2: Summarizing Anomaly Appraisers")
st.write("###### Detail information on anomaly appraisers")

# Create a DataFrame for anomaly appraisers
detail_appraiser_df = pd.DataFrame()

# Column 1: Appraiser Names
detail_appraiser_df['Appraiser Names'] = filtered_anomaly_df['Penanda Tangan'].unique()

# Insert a "No." column with numbering starting from 1
detail_appraiser_df.insert(0, 'No.', range(1, len(detail_appraiser_df) + 1))

# Column 2: Appraisers' Valuation Firms
detail_appraiser_df['Valuation Firms'] = detail_appraiser_df['Appraiser Names'].map(filtered_anomaly_df.groupby('Penanda Tangan')['KJPP'].unique().apply(lambda x: ', '.join(map(str, x))))

# Column 3: Add a 'Total Reports' column based on counts in df_risk_engine
detail_appraiser_df['Total Reports'] = detail_appraiser_df['Appraiser Names'].map(df_risk_engine['Penanda Tangan'].value_counts())

# Column 4: Add a 'Anomaly Reports' column based on counts in filtered_anomaly_df
detail_appraiser_df['Anomaly Reports'] = detail_appraiser_df['Appraiser Names'].map(filtered_anomaly_df['Penanda Tangan'].value_counts())

# Column 5: Percent Anomaly
detail_appraiser_df['Percent Anomaly'] = round((detail_appraiser_df['Anomaly Reports'] / detail_appraiser_df['Total Reports']) * 100)

# Column 6: Clusters
detail_appraiser_df['Clusters'] = detail_appraiser_df['Appraiser Names'].map(filtered_anomaly_df.groupby('Penanda Tangan')['Cluster No.'].unique().apply(lambda x: ', '.join(map(str, x))))

# Set the index to start from 1
detail_appraiser_df.set_index('No.', inplace=True)

# Display the DataFrame
st.dataframe(detail_appraiser_df, use_container_width=True)
#st.table(detail_appraiser_df)

# Section 4: Instructions for Displaying and Verifying Anomaly Appraisers
st.write("### Step 3: Displaying Anomaly Appraisers")

# User input for Cluster Numbers using text input
selected_clusters_input = st.text_input("###### Enter Cluster Numbers (comma-separated) here", "")

st.write("###### Comparison between anomaly and normal values")

# Initialize map outside the if-else block
#cluster_map = folium.Map(location=[df_risk_engine['Latitude'].mean(), df_risk_engine['Longitude'].mean()], zoom_start=115)

# Check if any clusters are entered
if selected_clusters_input:
    try:
        # Extract cluster numbers as a list of integers
        selected_clusters = [int(cluster.strip()) for cluster in selected_clusters_input.split(',')]
    except ValueError:
        st.error("Please enter valid integer values for cluster numbers.")
        st.stop()  # Stop further execution

    # Filter the DataFrame based on entered clusters
    df_selected_clusters = df_risk_engine[df_risk_engine['Cluster No.'].isin(selected_clusters)]

    # Update the map center
    #map_center = [df_selected_clusters['Latitude'].mean(), df_selected_clusters['Longitude'].mean()]
    map_center = folium.Map(location=[df_selected_clusters['Latitude'].mean(), df_selected_clusters['Longitude'].mean()], zoom_start=15)

    # Set the locale to Indonesian
    locale.setlocale(locale.LC_NUMERIC, 'id_ID')

    # Loop over filtered data and add markers to map
    for index, row in df_selected_clusters.iterrows():
        # Determine the color based on the condition
        color = 'red' if row['% Std Dev'] > threshold_input else 'blue'
    
        lat = row['Latitude']
        lon = row['Longitude']
        nilai_tanah = row['Indikasi Nilai Tanah']
        nama_penilai = row['Penanda Tangan']
        nama_kjpp = row['KJPP']

        # Format the land value
        formatted_nilai_tanah = locale.format_string("%.2f", nilai_tanah, grouping=True)

        # Construct html string based on selected values
        html = ""
        html += f"Penilai: {nama_penilai}<br>"
        html += f"KJPP: {nama_kjpp}<br>"
        html += f"Nilai Tanah: Rp{formatted_nilai_tanah}"

        # Add marker to map with hover information and use the determined color
        folium.Marker(
            [lat, lon],
            tooltip=html,
            icon=folium.Icon(color=color)
        ).add_to(map_center)
    
else:
    map_center = folium.Map(location=[df_risk_engine['Latitude'].mean(), df_risk_engine['Longitude'].mean()], zoom_start=13)

# Display the map
cluster_data = st_folium(map_center, width=725, height=450)