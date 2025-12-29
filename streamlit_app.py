import streamlit as st
from snowflake.snowpark.functions import col
import requests

st.title(f":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your smoothie will be:', name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()

# Get fruit options with FRUIT_NAME and SEARCH_ON columns
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert Snowpark dataframe to pandas
pd_df = my_dataframe.to_pandas()

# Commented out to prevent showing the table
# st.dataframe(pd_df)

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.subheader(fruit_chosen + ' Nutrition Information')

        # Fix string interpolation in URL
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        if smoothiefroot_response.ok:
            sf_json = smoothiefroot_response.json()
            st.dataframe(data=sf_json, use_container_width=True)
        else:
            st.write(f"Could not get nutrition info for {fruit_chosen}.")

    my_insert_stmt = f""" insert into smoothies.public.orders(ingredients,name_on_order) values ('{ingredients_string.strip()}', '{name_on_order}') """

    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!' , icon="✅")
