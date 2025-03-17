# Import libraries
import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

st.set_page_config(page_title="Data Sweeper Pro", page_icon="📊")

# Custom CSS styling
st.markdown("""
<style>
.main {background-color: #f5f5f5;}
h1 {color: #2e86c1;}
.stButton>button {background-color: #28b463; color: white;}
.stFileUploader>div>div>div>button {background-color: #2e86c1;}
</style>
""", unsafe_allow_html=True)

# Set up app
st.title("📊 Data Sweeper Pro")
st.write("Advanced data cleaning and visualization tool with multi-file support")

# File upload section
uploaded_files = st.file_uploader("Upload CSV/Excel files", 
                                 type=['csv', 'xlsx'], 
                                 accept_multiple_files=True)

if uploaded_files:
    # Initialize progress bar and dataframe list
    progress_bar = st.progress(0)
    dfs = []
    
    # Process each file
    for i, uploaded_file in enumerate(uploaded_files):
        st.subheader(f"Processing: {uploaded_file.name}")
        
        # Read file
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            continue

        # File info
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**File Size:** {uploaded_file.size/1024:.2f} KB")
        with col2:
            st.write(f"**Initial Shape:** {df.shape}")

        # Data preview
        with st.expander("Preview Data"):
            st.dataframe(df.head())

        # Data cleaning options
        st.subheader("🧹 Data Cleaning Tools")
        cleaning_col1, cleaning_col2 = st.columns(2)
        
        with cleaning_col1:
            if st.checkbox("Remove Duplicates", key=f"dup_{i}"):
                initial_rows = df.shape[0]
                df.drop_duplicates(inplace=True)
                st.success(f"Removed {initial_rows - df.shape[0]} duplicates")

            if st.checkbox("Drop Columns", key=f"drop_{i}"):
                cols_to_drop = st.multiselect("Select columns to drop", 
                                            df.columns, 
                                            key=f"dropcols_{i}")
                df = df.drop(columns=cols_to_drop)

        with cleaning_col2:
            if st.checkbox("Handle Missing Values", key=f"missing_{i}"):
                fill_method = st.radio("Fill method:",
                                    ["Mean", "Median", "Mode", "Custom Value"],
                                    key=f"fill_{i}")
                if fill_method == "Custom Value":
                    custom_val = st.text_input("Enter custom value", 
                                             key=f"custom_{i}")
                    df = df.fillna(custom_val)
                else:
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    if fill_method == "Mean":
                        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
                    elif fill_method == "Median":
                        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
                    elif fill_method == "Mode":
                        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mode().iloc[0])

        # Data visualization
        st.subheader("📈 Visualization")
        viz_col1, viz_col2 = st.columns(2)
        
        with viz_col1:
            chart_type = st.selectbox("Chart type", 
                                    ["Bar", "Line", "Scatter", "Pie"],
                                    key=f"chart_{i}")
        with viz_col2:
            x_axis = st.selectbox("X-axis", df.columns, key=f"x_{i}")
            y_axis = st.selectbox("Y-axis", df.columns, key=f"y_{i}")

        if chart_type == "Bar":
            st.bar_chart(df[[x_axis, y_axis]])
        elif chart_type == "Line":
            st.line_chart(df[[x_axis, y_axis]])
        elif chart_type == "Scatter":
            st.plotly_chart(px.scatter(df, x=x_axis, y=y_axis))
        elif chart_type == "Pie":
            st.plotly_chart(px.pie(df, names=x_axis, values=y_axis))

        # Data conversion
        st.subheader("🔄 Format Conversion")
        convert_col1, convert_col2 = st.columns(2)
        
        with convert_col1:
            export_format = st.radio("Export format",
                                   ["CSV", "Excel"],
                                   key=f"format_{i}")
        with convert_col2:
            if st.button("Convert File", key=f"convert_{i}"):
                buffer = BytesIO()
                if export_format == "CSV":
                    df.to_csv(buffer, index=False)
                    mime_type = "text/csv"
                else:
                    df.to_excel(buffer, index=False)
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                
                buffer.seek(0)
                st.download_button(
                    label="Download Converted File",
                    data=buffer,
                    file_name=f"converted_{uploaded_file.name.split('.')[0]}.{export_format.lower()}",
                    mime=mime_type
                )
        dfs.append(df)
        # Update progress bar
        progress_bar.progress((i+1)/len(uploaded_files))
        progress_bar.progress((i+1)/len(uploaded_files))
    
    # File comparison feature
    if len(uploaded_files) >= 2:
        st.subheader("🔍 File Comparison")
        if st.checkbox("Compare first 2 files"):
            df1 = pd.read_csv(uploaded_files[0])
            df2 = pd.read_csv(uploaded_files[1])
            
            comp_col1, comp_col2 = st.columns(2)
            with comp_col1:
                st.write("**File 1 Summary**")
                st.dataframe(df1.describe())
            with comp_col2:
                st.write("**File 2 Summary**")
                st.dataframe(df2.describe())
            
            differences = df1.compare(df2)
            with st.expander("Show Differences"):
                st.dataframe(differences)

    # Auto-clean report
    if st.button("📄 Generate Clean Report"):
        report = f"""
        ## Data Cleaning Report
        **Total files processed:** {len(uploaded_files)}
        **Total rows processed:** {sum([df.shape[0] for df in dfs])}
        **Total columns processed:** {sum([df.shape[1] for df in dfs])}
        """
        st.markdown(report)

    st.success("✅ All files processed successfully!")

# Footer
st.markdown("""
---
*Created by **Syed Uns Haider Zaidi***
""")