# Importing necessary libraries for file parsing
from bs4 import BeautifulSoup
import pandas as pd

# Importing necessary library for file upload
import streamlit as st

"# Degirum Test Plan Parser"

# Uploading the HTML file
uploaded_files = st.file_uploader(
    "Choose a HTML file", type="html", accept_multiple_files=True
)

if uploaded_files is None or len(uploaded_files) == 0:
    st.stop()

title_headings = []
for uploaded_file in uploaded_files:
    soup = BeautifulSoup(uploaded_file.read().decode(), "html.parser")
    title_headings.append(soup.find(id="title-heading").text)
    uploaded_file.seek(0)

selection = st.selectbox(
    "Select Test Plan", title_headings, index=None, placeholder="Select a test plan"
)

if selection is None:
    st.stop()

uploaded_file = uploaded_files[title_headings.index(selection)]


html_content = uploaded_file.read().decode()
# Parsing the HTML content using BeautifulSoup
soup = BeautifulSoup(html_content, "html.parser")

ordered_content = []
for element in soup.find_all(["h1", "h2", "h3", "p", "table"]):
    if element.name == "table":
        table_df = pd.read_html(str(element))[0]
        ordered_content.append({"type": "table", "content": table_df})
    else:
        ordered_content.append(
            {"type": element.name, "content": element.get_text(strip=True)}
        )

category = None
test_id = None
test = None
test_name_type_author = None
feature = None
description = None

df = pd.DataFrame(
    columns=[
        "Category",
        "Test",
        "Feature",
        "Description",
        "Type",
        "Pass/Fail Criteria",
        "Required Blocks",
        "Behavioral Blocks",
        "Test Author",
        "TestID",
        "Test ID Description",
        "Quality",
        "Arguments",
    ]
)


for i, part in enumerate(ordered_content):
    content = part["content"]
    if isinstance(content, str):
        if content.strip().startswith("Category"):
            category = content.split(":")[1].strip()
        if content.strip().startswith("TestID"):
            test_id = content.split(":")[1].strip()
        if content.strip().startswith("Test:"):
            test = content.split(":")[1].strip()
            description = None
        if content.strip().startswith("Description") and description is None:
            description = ordered_content[i + 1]["content"].strip()
        if content.strip().startswith("Feature"):
            feature = ordered_content[i + 1]["content"].strip()
        if content.strip().startswith("Pass/Fail Criteria"):
            df.loc[df["Test"] == test, "Pass/Fail Criteria"] = ordered_content[i + 1][
                "content"
            ].strip()
        if content.strip().startswith("Required Blocks"):
            df.loc[df["Test"] == test, "Required Blocks"] = (
                ordered_content[i + 1]["content"].strip().replace(".", "")
            )
        if content.strip().startswith("Behavior"):
            df.loc[df["Test"] == test, "Behavioral Blocks"] = (
                ordered_content[i + 1]["content"].strip().replace(".", "")
            )
    if isinstance(content, pd.DataFrame) and "Test Author" in content.columns:
        test_name_type_author = content
    if isinstance(content, pd.DataFrame) and "Arguments" in content.columns:
        df.loc[len(df.index)] = [
            category,
            test,
            feature,
            description,
            test_name_type_author["Type"].values[0],
            "",
            "",
            "",
            test_name_type_author["Test Author"].values[0],
            test_id,
            content["Description"].values[0],
            content["Quality"].values[0],
            content["Arguments"].values[0].replace("+", " +").strip(),
        ]

    # df.to_csv("output.csv", index=False)

st.dataframe(df)

import base64
import codecs

csv = df.to_csv(index=False)
b64 = base64.b64encode(
    csv.encode()
).decode()  # some strings <-> bytes conversions necessary here
href = (
    f'<a href="data:file/csv;base64,{b64}" download="output.csv">Download CSV File</a>'
)
st.markdown(href, unsafe_allow_html=True)


df.to_excel("output.xlsx", index=False)
with open("output.xlsx", "rb") as f:
    data = f.read()
b64 = base64.b64encode(data).decode()
href = f'<a href="data:application/octet-stream;base64,{b64}" download="output.xlsx">Download Excel File</a>'
st.markdown(href, unsafe_allow_html=True)
