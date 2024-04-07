import streamlit as st
from utils import create_docs
import pandas as pd
from tqdm import tqdm
import time

def main():
    st.set_page_config(page_title="Invoice Extraction Bot")
    st.title("Invoice Extraction Bot...💁")
    st.subheader("I can help you in extracting invoice data")

    # Upload the Invoices (PDF and docx files)
    files = st.file_uploader("Upload invoices here, PDF and DOCX files allowed",
                             type=["pdf", "docx"], accept_multiple_files=True)

    submit = st.button("Extract Data")

    if submit:
        with st.spinner('Wait for it...'):
            # Create a progress bar
            progress_bar = st.progress(0)
            num_files = len(files)
            df = pd.DataFrame({'Invoice no': pd.Series(dtype='str'),
                                'Date': pd.Series(dtype='str'),
                                'Client': pd.Series(dtype='str'),
                                'Description': pd.Series(dtype='str'),
                                'Hours': pd.Series(dtype='str'),
                                'Rate': pd.Series(dtype='str'),
                                'Amount': pd.Series(dtype='str')
                                })

            start_time = time.time()
            total_retries = 0
            for idx, file in enumerate(files):
                retries, data_dict = create_docs([file], df)
                total_retries += retries
                df = pd.concat([df, pd.DataFrame([data_dict])], ignore_index=True)
                progress = (idx + 1) / num_files
                progress_bar.progress(int(progress * 100))  # Update the progress bar in the UI

            end_time = time.time()
            total_time = end_time - start_time
            average_time_per_file = total_time / num_files

            with pd.option_context('display.max_rows', None):
                st.write(df)

            file_name = st.download_button(
                label="Save CSV",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="invoices.csv",
                mime="text/csv",
                key="download-csv"
            )

            if file_name:
                st.success(f"CSV saved as {file_name}. Processing complete! Average time per file: {average_time_per_file:.2f} seconds. Total retries: {total_retries}. Hope I was able to save your time❤️")
            else:
                st.warning("No file was saved.")

if __name__ == '__main__':
    main()
