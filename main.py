import streamlit as st
from marketing_attribution_models import MAM
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import plotly.express as px

df = None
attributions = None
st.set_page_config(layout="wide")

with st.sidebar:
    st.title("Marketing Attribution Model")
    with st.expander('Dataset'):
        csv_file = st.file_uploader("Choose a file", type='csv')
        if csv_file is not None:
            df = pd.read_csv(csv_file)
            grp_channels = st.toggle('Group Channels',
                                     help="This indicates the input format of the dataframe. True  = Each row represents a user session that will be grouped into a userjourney; False = Each row represents a user journey and the columns")
            if grp_channels:
                path_sep = st.text_input("path_seperator",
                                         help="This should match the separator being used on the inputed dataframe in the channels_colname;")
            else:
                path_sep = ' > '
            channel_colname = st.selectbox("Channels Column-name", df.columns.insert(0, None),
                                           help="Column name in the dataframe containing the time in hours untill the moment of the conversion.")
            journey_with_conv_colname = st.selectbox("Journey With Conversion Column-name", df.columns.insert(0, None),
                                                     help="Column name in the dataframe indicating if the journey (row) was a successfully conversion (True), or not (False).")
            journey_id_on_conv = st.toggle("Create Journey ID based on Conversion")
            attributions = MAM(df=df,
                               group_channels=grp_channels,
                               path_separator=path_sep,
                               channels_colname=channel_colname,
                               journey_with_conv_colname=journey_with_conv_colname,
                               create_journey_id_based_on_conversion=journey_id_on_conv
                               )
        else:
            random_df = st.toggle('Random DF', help="Will create a random dataframe with testing purpose")
            if random_df:
                attributions = MAM(random_df=random_df)

    if attributions:
        with st.expander('Group Results'):
            grp_by_channel = st.toggle("Show Grouped By Channel")

        with st.expander('Last Click'):
            last_click = st.toggle("Show Last Click Heuristic")

        with st.expander('First Click'):
            first_click = st.toggle("Show First Click Heuristic")

        with st.expander('Last Click Non Direct Model'):
            last_click_non = st.toggle("Show Last Click Non Model")

        with st.expander('Position based Model'):
            pos_model = st.toggle("Show Position Based Model")
            if pos_model and csv_file:
                first_weight = st.slider("First Weight", 0, 100)/100
                middle_weight = st.slider("Middle Weight", 0, 100)/100
                last_weight = st.slider("Last Weight", 0, 100)/100

        with st.expander('Time Decay Model'):
            decay_model = st.toggle("Show Time Decay Model")
            if decay_model and csv_file:
                decay_ot = st.slider("Decay Over Time", 0, 100, 50)/100
                frq = st.slider("Frequency", 1, 10)

        with st.expander('Markov Chains'):
            markov = st.toggle("Show Attribution Using Markov")
            if markov:
                removal_effect = st.toggle("Show Removal Effect")

        with st.expander('Shapely Value'):
            shapely = st.toggle("Show Shapely Value")
            if shapely and csv_file:
                values_col = st.selectbox("Values Column", attributions.as_pd_dataframe().columns)

        with st.expander("Visualizations"):
            viz = st.toggle('Show Visualizations')
            if viz:
                model_type = st.selectbox("Model Type", ['all', 'heuristic', 'algorithmic'])

with(st.expander("🌟 Welcome to the Marketing Attribution Models Interface! 🌟")):
    st.write("""**🔍 Overview:**\n
This user-friendly interface is designed to help marketers, analysts, and businesses visualize and understand how different marketing channels contribute to conversions. Whether you're new to marketing analytics or a seasoned professional, this tool makes it easy to see which channels are driving results and where to optimize your marketing spend.
\n**🛠 Features:**\n
\n**Multiple Attribution Models:**\n
Explore various attribution models like First Click, Last Click, Linear, and Time Decay to see how they allocate conversion value to different marketing channels.
User-Friendly Visualization:
View your attribution data in intuitive charts and graphs, allowing you to quickly comprehend the impact of each channel on conversions.
\n**Customizable Insights:**\n
Tailor the analysis to your needs, adjust settings, and explore different scenarios to see how changes in attribution can impact your marketing strategy.
\n**🌐 How to Use:**\n
\n**Input Your Data:**\n
Start by uploading your marketing data as a csv file, including interactions across different channels and conversions.
\n**Select Attribution Model:**\n
Choose the attribution model you want to apply. You can switch between models to compare results.
\n**Analyze & Optimize:**\n
Review the visualized results to understand which channels are most effective, and optimize your marketing efforts accordingly.
\n**📘 Benefits of Using This Tool:**\n
\n**Informed Decision-Making:**\n
Gain insights into the effectiveness of your marketing channels, helping you make data-driven decisions to optimize your marketing ROI.
\n**Efficient Resource Allocation:**\n
Understand which channels are contributing most to conversions and allocate your marketing resources more effectively.
\n**Enhanced Marketing Strategy:**\n
Leverage the insights gained from different attribution models to refine your marketing strategies and campaigns for better outcomes.
\n**🌟 Start Your Analysis!**\n
Dive in and explore how different marketing channels are influencing your conversions. If you’re ready to uncover insights and optimize your marketing strategies, this is the tool for you!
""")


start = st.checkbox('Start Model')


if start:
    c = []
    c[0:2] = st.columns(2,gap="medium")
    c[2:4] = st.columns(2,gap="medium")
    c[4:6] = st.columns(2,gap="medium")
    c[6:8] = st.columns(2,gap="medium")
    c[8:10] = st.columns(2,gap="medium")

    st.markdown("""
        <style type="text/css">
            div[data-testid="column"] {
                border: 1px solid black;
                padding: 10px;
                border-radius: 5px;
                box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.2);
            }
        </style>
    """, unsafe_allow_html=True)

    if attributions:
        i = 1
        with c[i-1]:
            st.title(f"{i}. Dataframe")
            st.dataframe(attributions.as_pd_dataframe(), use_container_width=True)

        if grp_by_channel:
            i += 1
            with c[i-1]:
                st.title(f"{i}. Group By Channel")
                attributions.attribution_shapley()
                df = attributions.group_by_channels_models
                fig = px.pie(df, values=df.columns[1], names=df.columns[0])
                st.plotly_chart(fig, use_container_width=True)
                st.write("You can see all results grouped by channel.")

        if last_click:
            i += 1
            with c[i-1]:
                st.title(f"{i}. last Click")
                attribution_last_click = attributions.attribution_last_click()
                df = attribution_last_click[1]
                try:
                    fig = px.pie(df, values=df.columns[1], names=df.columns[0])
                except AttributeError:
                    fig = px.pie(values=df.values, names=df.index)
                st.plotly_chart(fig, use_container_width=True)
                st.write("The Last Click heuristic, also known as the Last Touch attribution model, is one of the simplest and most widely used methods in marketing attribution models. This model attributes 100% of the conversion value to the last touchpoint or interaction that the customer had before converting, like making a purchase or filling out a form.")

        if first_click:
            i += 1
            with c[i-1]:
                st.title(f"{i}. First Click")
                attribution_first_click = attributions.attribution_first_click()
                df = attribution_first_click[1]
                try:
                    fig = px.pie(df, values=df.columns[1], names=df.columns[0])
                except AttributeError:
                    fig = px.pie(values=df.values, names=df.index)
                st.plotly_chart(fig, use_container_width=True)
                st.write("The First Click model, sometimes also known as the First Touch model, is a heuristic (or rule of thumb) that attributes 100% of the conversion value to the first interaction or touchpoint a customer has with a brand or campaign. This means that if a conversion occurs, the entire credit for that conversion is given to the first channel through which the user engaged with the brand.")

        if last_click_non:
            i += 1
            with c[i-1]:
                st.title(f"{i}. Last Click Non Direct Model")
                data = attributions.attribution_last_click_non(but_not_this_channel='Direct')[1]
                try:
                    fig = px.bar(data, x='channels', y=data.columns[1])
                except AttributeError:
                    fig = px.bar(x=data.index, y=data.values)
                st.plotly_chart(fig, use_container_width=True)
                st.write("In this, Direct traffic is overwritten in case previous interations have a specific traffic source other than Direct itself in a given timespan (6 months by default).")
        if pos_model:
            i += 1
            with c[i-1]:
                st.title(f"{i}. Position Based Model")
                if csv_file:
                    df = attributions.attribution_position_based(
                        list_positions_first_middle_last=[first_weight, middle_weight, last_weight])[1]
                else:
                    df = attributions.attribution_position_based(
                        list_positions_first_middle_last=[0.3, 0.3, 0.4])[1]
                try:
                    fig = px.bar(x=df.channels, y=df[df.columns[1]])
                except AttributeError:
                    fig = px.bar(x=df.index, y=df.values)
                st.plotly_chart(fig, use_container_width=True)
                # st.write("This model inputs the weights respective to the positions of channels in each journey can me specified according to business related decisions")


        if decay_model:
            i += 1
            with c[i-1]:
                st.title(f"{i}. Time Decay Model")
                if csv_file:
                    df = attributions.attribution_time_decay(decay_over_time=decay_ot, frequency=frq)[1]
                else:
                    df = attributions.attribution_time_decay(
                        decay_over_time=0.6,
                        frequency=7)[1]
                try:
                    fig = px.pie(df, values=df.columns[1], names=df.channels)
                except AttributeError:
                    fig = px.pie(values=df.values, names=df.index)
                st.plotly_chart(fig, use_container_width=True)
                st.write("The Time Decay model in marketing attribution is a way to assign credit to the different interactions, or touchpoints, a customer has with your marketing channels before they make a purchase or conversion. In this model, the interactions that occur closer to the time of conversion receive more credit than those that occur further away in time. Essentially, the credit decays as you go back in time from the conversion.")

        if markov:
            i += 1
            with c[i-1]:
                st.title(f"{i}. Attribution Using Markov")
                attribution_markov = attributions.attribution_markov(transition_to_same_state=False)
                fig = px.imshow(attribution_markov[2].round(3), text_auto=True)
                st.plotly_chart(fig, use_container_width=True)
                if removal_effect:
                    st.header("Removal Effect")
                    fig1 = px.imshow(attribution_markov[3].round(3), text_auto=True)
                    st.plotly_chart(fig1, use_container_width=True)
                st.write("Markov Chains in marketing attribution models provide a sophisticated approach to understanding and allocating credit to different marketing channels involved in customer conversion paths. A Markov Chain is a statistical model that calculates the probability of transitioning from one state to another within a system.")

        if shapely:
            i += 1
            with c[i-1]:
                st.title(f"{i}. Shapely Value")
                if csv_file:
                    st.dataframe(attributions.attribution_shapley(size=4, order=True, values_col=values_col)[0])
                else:
                    st.dataframe(attributions.attribution_shapley(size=4, order=True, values_col="conversions")[0])
                st.write("The Shapley Value is a concept from cooperative game theory that has been applied to marketing attribution models to distribute the credit for a conversion among different marketing channels. It allows for a fair allocation of the conversion value to each touchpoint in the customer journey, based on their contribution to the conversion.")

        if viz:
            i += 1
            with c[i - 1]:
                st.title(f"{i}. Visualization")
                try:
                    st.pyplot(attributions.plot(model_type=model_type).figure)
                except UnboundLocalError:
                    st.warning("Please Select a Model For Visualization")

    else:
        st.warning("Please Select a Dataframe")
