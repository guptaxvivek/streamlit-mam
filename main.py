import streamlit as st
from marketing_attribution_models import MAM
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

df = None
attributions = None
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

        with st.expander('Last Click Non Model'):
            last_click_non = st.toggle("Show Last Click Non Model")
            if last_click_non:
                col = st.selectbox("Select Channel Column", attributions.as_pd_dataframe().columns)
                but_not_this_channel = st.selectbox("But Not This Channel", attributions.as_pd_dataframe()[col].unique())

        with st.expander('Position based Model'):
            pos_model = st.toggle("Show Position Based Model")
            if pos_model:
                first_weight = st.slider("First Weight", 0, 100)/100
                middle_weight = st.slider("Middle Weight", 0, 100)/100
                last_weight = st.slider("Last Weight", 0, 100)/100

        with st.expander('Time Decay Model'):
            decay_model = st.toggle("Show Time Decay Model")
            if decay_model:
                decay_ot = st.slider("Decay Over Time", 0, 100)/100
                frq = st.slider("Frequency", 1, 10)

        with st.expander('Markov Chains'):
            markov = st.toggle("Show Attribution Using Markov")
            if markov:
                removal_effect = st.toggle("Show Removal Effect")

        with st.expander('Shapely Value'):
            shapely = st.toggle("Show Shapely Value")
            if shapely:
                values_col = st.selectbox("Values Column", attributions.as_pd_dataframe().columns)

        with st.expander("Visualizations"):
            viz = st.toggle('Show Visualizations')
            if viz:
                model_type = st.selectbox("Model Type", ['all', 'heuristic', 'algorithmic'])

start = st.checkbox('Start Model')
if start:
    if attributions:
        i = 1
        st.title(f"{i}. Dataframe")
        st.dataframe(attributions.as_pd_dataframe())

        if grp_by_channel:
            i += 1
            st.title(f"{i}. Group By Channel")
            attributions.attribution_shapley()
            st.dataframe(attributions.group_by_channels_models)

        if last_click:
            i += 1
            st.title(f"{i}. last Click")
            attribution_last_click = attributions.attribution_last_click()
            st.dataframe(attribution_last_click[1])

        if first_click:
            i += 1
            st.title(f"{i}. First Click")
            attribution_first_click = attributions.attribution_first_click()
            st.dataframe(attribution_first_click[1])

        if last_click_non:
            i += 1
            st.title(f"{i}. Last Click Non Model")
            st.dataframe(attributions.attribution_last_click_non(but_not_this_channel=but_not_this_channel)[1])

        if pos_model:
            i += 1
            st.title(f"{i}. Position Based Model")
            st.dataframe(attributions.attribution_position_based(list_positions_first_middle_last=[first_weight, middle_weight, last_weight])[1])

        if decay_model:
            i += 1
            st.title(f"{i}. Time Decay Model")
            st.dataframe(attributions.attribution_time_decay(decay_over_time=decay_ot, frequency=frq)[1])

        if markov:
            i += 1
            st.title(f"{i}. Attribution Using Markov")
            attribution_markov = attributions.attribution_markov(transition_to_same_state=False)
            st.dataframe(attribution_markov[1])
            ax, fig = plt.subplots(figsize=(15, 10))
            sns.heatmap(attribution_markov[2].round(3), cmap="YlGnBu", annot=True, linewidths=.5)
            st.pyplot(ax)
            if removal_effect:
                i += 1
                st.title(f"{i}. Removal Effect")
                ax1, fig1 = plt.subplots(figsize=(2, 5))
                sns.heatmap(attribution_markov[3].round(3), cmap="YlGnBu", annot=True, linewidths=.5)
                st.pyplot(ax1)

        if shapely:
            i += 1
            st.title(f"{i}. Shapely Value")
            st.dataframe(attributions.attribution_shapley(size=4, order=True, values_col=values_col)[0])

        if viz:
            i += 1
            st.title(f"{i}. Visualization")
            try:
                st.pyplot(attributions.plot(model_type=model_type))
            except UnboundLocalError:
                st.warning("Please Select a Model For Visualization")

    else:
        st.warning("Please Select a Dataframe")