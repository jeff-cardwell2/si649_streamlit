import altair as alt
import pandas as pd
import streamlit as st

st.title("Interactive CommVis by Jeff Cardwell")

all_recipes_df = pd.read_csv('allrecipes.csv')
all_recipes_df = all_recipes_df.drop(columns=['Unnamed: 0', 'footnotes', 'error', 'url', 'photo_url', 'instructions'])

ingredient_dist_df = pd.read_csv('ingredient_dist.csv')
ingredient_dist_df = ingredient_dist_df.drop(columns='Unnamed: 0')

adaptations_df = pd.read_csv('adaptations.csv')
adaptations_df= adaptations_df.drop(columns='Unnamed: 0')

def make_vis1():
    ingredient = []
    count = []
    trad = []
    top_non_trad_ingredients = []

    non_trad_df = ingredient_dist_df.loc[ingredient_dist_df['Traditional']==0]
    for i in non_trad_df.sort_values('Count', ascending=False)['Ingredient'][:41]:
        top_non_trad_ingredients.append(i)

    top_non_trad_ingredients.remove('saffron thread')
    top_non_trad_ingredients.remove('onion')
    top_non_trad_ingredients.remove('lemon wedges')
    top_non_trad_ingredients.remove('kosher salt')
    top_non_trad_ingredients.remove('black pepper')
    top_non_trad_ingredients.remove('green peas')

    for i, r in ingredient_dist_df.iterrows():
        if r['Traditional'] == 1:
            ingredient.append(r['Ingredient'])
            count.append(r['Count'])
            trad.append('Yes')
        else:
            if r['Ingredient'] in top_non_trad_ingredients:
                ingredient.append(r['Ingredient'])
                count.append(r['Count'])
                trad.append('No')

    limited_ing_dist_df = pd.DataFrame()
    limited_ing_dist_df['Ingredient'] = ingredient
    limited_ing_dist_df['Count'] = count
    limited_ing_dist_df['Traditional'] = trad

    trad = list(limited_ing_dist_df['Traditional'].unique())

    radio_sel = alt.selection_multi(
        fields = ['Traditional'],
        bind = 'legend')

    int_sel = alt.selection_interval(empty = 'all')

    display_cond = alt.condition(
        int_sel,
        alt.SizeValue(30),
        alt.SizeValue(0)
    )

    bar = alt.Chart(limited_ing_dist_df, title = {'text':"Traditional Paella Is About What's NOT There", 'subtitle':"Select a Value in the Legend to Filter Chart"}, width = 400).mark_bar().encode(
        x=alt.X('Count',
            title= 'Number of Recipes with Ingredient'),
        y=alt.Y('Ingredient',
            sort = alt.SortField(field='Count', order='descending')),
        color=alt.Color(
            'Traditional:N',
            scale=alt.Scale(
                domain=['Yes', 'No'],
                range=["red", "gold"]
            ))
    ).add_selection(
        radio_sel
    ).transform_filter(radio_sel)

    return bar

def make_vis2():
    pts = alt.selection(type="single", encodings=['x'])

    point = alt.Chart(all_recipes_df).mark_point().transform_filter(
        alt.datum['review_count'] > 0
    ).encode(
        alt.X('rating_stars:Q', bin=False, title='Rating'),
        alt.Y('review_count:Q', bin=False, title='Number of Reviews'),
        color = alt.value('red'),
        tooltip = ['title', 'Paella type', 'rating_stars', 'review_count']
    ).properties(
        width=600,
        height=300
    ).transform_filter(pts)


    bar = alt.Chart(all_recipes_df,  title = {'text':"Which Types of Paella are the Most Popular?", 'subtitle':"Select a Paella Type to Filter Chart"}).mark_bar().encode(
        x=alt.X('Paella type:N',
            title=None,
            axis=alt.Axis(labelAngle=0, labelFontStyle='Bold')),
        y=alt.Y('mean_rating:Q',
            title='Average Rating'),
        color=alt.condition(pts, alt.ColorValue("red"), alt.ColorValue("gold"))
    ).transform_aggregate(
        mean_rating = 'mean(rating_stars)',
        groupby=['Paella type']
    ).properties(
        width=600,
        height=300
    ).add_selection(pts)

    concat = alt.vconcat(
        bar,
        point
    ).resolve_legend(
        color="independent",
        size="independent"
    ).configure_point(size=100)

    return concat

def make_vis3():
    brush = alt.selection(type='interval', encodings = ['x'])

    points = alt.Chart(all_recipes_df, title={'text':"Does Quality Require More Patience?", 'subtitle':"How does average cook time change for different rating groups?"}, width=600, height = 400).mark_point(filled = True).transform_filter(
        (alt.datum['rating_stars'] > 0) & (alt.datum['total_time_minutes']>0)
    ).encode(
        x=alt.X('rating_stars:Q',
            title='Rating'),
        y=alt.Y('total_time_minutes:Q',
            title='Total Cook Time'),
        color = alt.condition(brush, alt.value('gold'), alt.value('grey')),
        tooltip = ['title', 'Paella type', 'rating_stars', 'review_count'],
        opacity=alt.condition(brush, alt.OpacityValue(1), alt.OpacityValue(0.7)),
    ).add_selection(
        brush
    )

    line = alt.Chart(all_recipes_df).mark_rule(color='red').transform_filter(
        (alt.datum['rating_stars'] > 0) & (alt.datum['total_time_minutes']>0)
    ).encode(
        y='mean(total_time_minutes):Q',
        tooltip = 'mean(total_time_minutes):Q',
        size=alt.SizeValue(3)
    ).transform_filter(
        brush
    )

    layer = alt.layer(points, line).configure_point(size=70)
    return layer

viz1 = make_vis1()
viz2 = make_vis2()
viz3 = make_vis3()

selectbox_options = ['vis1', 'vis2', 'vis3']
selectbox = st.sidebar.selectbox(
    label='Select Visualization',
    options = selectbox_options
)
if selectbox == 'vis1':
    viz1
elif selectbox == 'vis2':
    viz2
elif selectbox == 'vis3':
    viz3
