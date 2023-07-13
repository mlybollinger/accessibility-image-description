import streamlit as st
import csv
import requests
from cs50 import SQL
from PIL import Image
import streamlit.components.v1 as components

import time
import concurrent.futures
import os
import pandas as pd
import glob
import numpy as np

def remove_images():
    files = glob.glob('images/*')
    for f in files:
        os.remove(f)

def save_image_from_url(url, img_no, output_folder):
    image = requests.get(url)
    output_path = os.path.join(
        output_folder, 'img_' + str(img_no) + ".png"
    )
    with open(output_path, "wb") as f:
        f.write(image.content)


def load(df, output_folder):    
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=5
    ) as executor:
        future_to_url = {
            executor.submit(save_image_from_url, row['src'], row['img_no'], output_folder): row['src']
            for _, row in df.iterrows()
        }
        for future in concurrent.futures.as_completed(
            future_to_url
        ):
            url = future_to_url[future]
            try:
                future.result()
            except Exception as exc:
                print(
                    "%r generated an exception: %s" % (url, exc)
                )

def create_column(df, left_or_right):

    if left_or_right == "left":
        start_row = 0
    elif left_or_right == "right":
        start_row = 5
    else:
        raise Exception("Column must be left or right")

    for i in range(start_row, start_row + 5):
        row = df.iloc[i]
        
        src = 'images/img_' + str(row['img_no']) + ".png"
        alt = row['model_alts'][1:][:-1]
        page_url = row['page_url']
        orig_alt = row['alt']
    

        st.subheader("Image: ")

            

        

        
        im = Image.open(src).resize((240, 240))
            
        st.image(im)
        st.markdown("<p style='font-size: 14px; color: #D3D3D3'><i>" + page_url + "</i></p>", unsafe_allow_html=True)


        if not st.session_state["checkbox_" + str(i)]:
            
            st.text_input("Alternative text to revise: ", value=alt, key = "text_" + str(i))
        else:
            st.markdown('<div class="css-16idsys"><p>Alternative text to revise: </p></div>', unsafe_allow_html=True)
            st.code(alt, language="markdown")

        st.checkbox("Leave this one for later", key="checkbox_" + str(i))

        st.markdown("#")

        with st.expander("See original alt text"):
            st.write(orig_alt)
        st.markdown("#")
        st.markdown("#")

def submit_button():
    for index, row in curr_df.iterrows():

        if not st.session_state["checkbox_" + str(index)]:
            db.execute('''UPDATE imgs SET approved_alt =
                ''' + str(st.session_state["text_" + str(index)]) + '''
                WHERE img_no = ''' + str(row['img_no']))
        else:
            db.execute('''UPDATE imgs
                SET approved_alt = 'TBD'
                WHERE img_no = ''' + str(row['img_no']))

    
    st.session_state.page +=1
    st.session_state.reset = 1

    placeholder.empty()

    

# read first ten rows of CSV file with image and alt-text
st.set_page_config(layout="wide")

if 'page' not in st.session_state:
    st.session_state.page = 0

col_names = ['index', 'site_url', 'page_url', 'src', 'alt', 'model_alt', 'img_address']

#establish SQL connection

db = SQL("sqlite:///nh_imgs.db")

curr_df = pd.DataFrame.from_records(db.execute('''SELECT * FROM imgs
    WHERE approved_alt IS NULL
    LIMIT 10'''))

for i in range(10):
    if "checkbox_" + str(i) not in st.session_state:
        st.session_state["checkbox_" + str(i)] = 0



if 'reset' not in st.session_state:
    st.session_state.reset = 0
    
    remove_images()
    load(curr_df, 'images/')
    time.sleep(3)
    





if st.session_state.reset:
    remove_images()

    load(curr_df, 'images/')
    st.session_state.reset = 0
    time.sleep(5)

js = '''
<script>
    var body = window.parent.document.querySelector(".main");
    console.log(body);
    body.scrollTo({top: 0, behavior: 'smooth'});
</script>
'''


placeholder = st.empty()

with placeholder.container():
    components.html(
        js,
    )



st.title("Model-Generated Alternative Text")

st.header("Approve, revise, or reject the following image descriptions generated by BLIP-2")

left, right = st.columns(2)

with left:
        
    create_column(curr_df, "left")

            
with right:

    create_column(curr_df, "right")





submit = st.button('Submit', on_click = submit_button)



 

    



            
          

             