import streamlit as st
import pandas as pd

from database import active_orders, add_order, change_amount, change_status, all_orders
from agent import transcript_order
from google_funcs import upload_to_drive


def update_orders(old_data, new_data):
    """ This function updates the database with updated data """
    # Changes in amounts
    for row in new_data.itertuples(index=False):
        if row.amount != old_data.loc[old_data['id'] == row.id, 'amount'].values:
            change_amount('shopping.db', row.id, row.amount)
    # Changes in active
    for row in new_data.itertuples(index=False):
        if row.status != old_data.loc[old_data['id'] == row.id, 'status'].values:
            change_status('shopping.db', row.id)

    upload_to_drive('shopping.db')


def main():
    """ This is the main function for the home page """
    st.title(':blue[Family Shop App]')

    with st.form('Enter Order', clear_on_submit=True):
        st.subheader('Voice Order')
        message = st.audio_input('Record Your Order')

        st.subheader('Manual Order')
        manual_product = st.text_input('Enter Product', value=None)
        manual_amount = st.number_input('Enter Amount', min_value=0)

        st.divider()

        if st.form_submit_button('Submit'):
            try:
                # Voice input
                if message:
                    order = transcript_order(message)
                    if isinstance(order, list):
                        product = order[0]
                        amount = order[1]
                        if product != '':
                            add_order('shopping.db', product, amount)
                            upload_to_drive('shopping.db')
                        else:
                            st.error(order)
                    else:
                        st.error('You did not enter any order.')

                # Manual input
                elif manual_product:
                    product = manual_product
                    amount = manual_amount
                    add_order('shopping.db', product, amount)
                    upload_to_drive('shopping.db')

                # Feedback to user
                if amount is not None and amount != 0:
                    st.write(f'Added {product}, {amount}')
                else:
                    st.write(f'Added {product}')

            except:
                # Manual process if agent not available
                pass

    st.divider()

    st.subheader('Existing orders:')
    orders = active_orders('shopping.db')
    for order in orders:
        order['status'] = not order['active']
    orders_df = pd.DataFrame(orders)
    new_data = st.data_editor(orders_df,
                              hide_index=True,
                              column_config={
                                   'date': None,
                                   'ordered_by': None,
                                   'picture': None,
                                   'active': None
                                 },
                              )

    st.button('Update Orders', on_click=update_orders, args=(orders_df, new_data))


if __name__ == '__main__':
    main()