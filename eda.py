import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


st.set_page_config(page_title='NBA Statistics Explorer', layout='wide')
st.image(
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRlXTzn3kr6AofzE1d78AQxWmitIP7ckNWQDg&s",
            width=400,
        )


st.title('NBA Player Statistics Explorer')


st.markdown("""
            
Welcome to the NBA Player Stats Explorer! This interactive app lets you dive deep into NBA player statistics from various seasons. Using data from  [Basketball-reference.com](https://www.basketball-reference.com/), you can explore detailed stats, filter by team and position, and view a range of visualizations including heatmaps, box plots, and scatter plots. Whether you're analyzing player performance trends, comparing teams, or identifying top players, this app provides an intuitive interface to help you uncover insights and trends in NBA data.

            
* **Python libraries:** base64, pandas, streamlit, matplotlib, seaborn
* **Data source:** [Basketball-reference.com](https://www.basketball-reference.com/)
""")

st.sidebar.header('User Input Features')
selected_year = st.sidebar.selectbox('Year', list(reversed(range(1950, 2024))))

@st.cache_data
def load_data(year):
    url = f"https://www.basketball-reference.com/leagues/NBA_{year}_per_game.html"
    html = pd.read_html(url, header=0)
    df = html[0]
    raw = df.drop(df[df.Age == 'Age'].index)
    raw = raw.fillna(0)
    playerstats = raw.drop(['Rk'], axis=1)
    return playerstats

playerstats = load_data(selected_year)

# Clean up column names
playerstats.columns = playerstats.columns.str.strip().str.lower().str.replace(' ', '_')
playerstats['team'] = playerstats['team'].astype(str)  # Ensure 'team' column is of type string

sorted_unique_team = sorted(playerstats['team'].unique())
selected_team = st.sidebar.multiselect('Team', sorted_unique_team, sorted_unique_team)
unique_pos = ['C', 'PF', 'SF', 'PG', 'SG']
selected_pos = st.sidebar.multiselect('Position', unique_pos, unique_pos)

df_selected_team = playerstats[(playerstats['team'].isin(selected_team)) & (playerstats['pos'].isin(selected_pos))]

st.header('Display Player Stats of Selected Team(s)')
st.write(f'Data Dimension: {df_selected_team.shape[0]} rows and {df_selected_team.shape[1]} columns.')
st.dataframe(df_selected_team)

def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="playerstats.csv">Download CSV File</a>'
    return href

st.markdown(filedownload(df_selected_team), unsafe_allow_html=True)

# Sidebar for visualizations
st.sidebar.header('Visualizations')
visualization = st.sidebar.radio(
    "Select a visualization:",
    ['Intercorrelation Heatmap', 'Box Plot by Team', 'Top 10 Players by Points', 'Points vs. Assists', 'Average Points by Age', 'Points by Team']
)

# Visualization selection
if visualization == 'Intercorrelation Heatmap':
    st.header('Intercorrelation Matrix Heatmap')
    numeric_df = df_selected_team.select_dtypes(include=[np.number])
    if not numeric_df.empty:
        corr = numeric_df.corr()
        mask = np.zeros_like(corr)
        mask[np.triu_indices_from(mask)] = True
        fig, ax = plt.subplots(figsize=(7, 5))
        sns.heatmap(corr, mask=mask, vmax=1, square=True, annot=True, cmap='coolwarm', ax=ax)
        ax.set_title('Correlation Heatmap of Numeric Metrics')
        st.pyplot(fig)
    else:
        st.write("No numeric data available for correlation.")

elif visualization == 'Box Plot by Team':
    st.header('Box Plot by Team')
    metrics = ['pts', 'reb', 'ast']  # Adjust these names based on actual column names
    for metric in metrics:
        if metric in df_selected_team.columns:
            df_selected_team[metric] = pd.to_numeric(df_selected_team[metric], errors='coerce')
            fig, ax = plt.subplots(figsize=(12, 6))
            sns.boxplot(x='team', y=metric, data=df_selected_team, ax=ax)
            ax.set_xlabel('Team')
            ax.set_ylabel(metric)
            ax.set_title(f'Box Plot of {metric} by Team')
            plt.xticks(rotation=90)
            st.pyplot(fig)
        else:
            st.write(f"Metric '{metric}' is not available in the dataset.")

elif visualization == 'Top 10 Players by Points':
    st.header('Top 10 Players by Points Scored')
    if 'pts' in df_selected_team.columns and 'player' in df_selected_team.columns:
        top_players = df_selected_team.nlargest(10, 'pts')[['player', 'pts']]
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.barplot(x='pts', y='player', data=top_players, ax=ax)
        ax.set_xlabel('Points')
        ax.set_ylabel('Player')
        ax.set_title('Top 10 Players by Points Scored')
        st.pyplot(fig)
    else:
        st.write("The 'pts' or 'player' column is missing in the dataset.")

elif visualization == 'Points vs. Assists':
    st.header('Points vs. Assists')
    if 'pts' in df_selected_team.columns and 'ast' in df_selected_team.columns:
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.scatterplot(x='pts', y='ast', data=df_selected_team, ax=ax)
        ax.set_xlabel('Points')
        ax.set_ylabel('Assists')
        ax.set_title('Points vs. Assists')
        st.pyplot(fig)
    else:
        st.write("The 'pts' or 'ast' columns are missing in the dataset.")

elif visualization == 'Average Points by Age':
    st.header('Average Points Scored by Age')
    if 'age' in df_selected_team.columns and 'pts' in df_selected_team.columns:
        age_points = df_selected_team.groupby('age')['pts'].mean().reset_index()
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.lineplot(x='age', y='pts', data=age_points, ax=ax)
        ax.set_xlabel('Age')
        ax.set_ylabel('Average Points')
        ax.set_title('Average Points Scored by Age')
        st.pyplot(fig)
    else:
        st.write("The 'age' or 'pts' columns are missing in the dataset.")

elif visualization == 'Points by Team':
    st.header('Points Scored by Team')
    if 'pts' in df_selected_team.columns and 'team' in df_selected_team.columns:
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.boxplot(x='team', y='pts', data=df_selected_team, ax=ax)
        ax.set_xlabel('Team')
        ax.set_ylabel('Points')
        ax.set_title('Points Scored by Team')
        plt.xticks(rotation=90)
        st.pyplot(fig)
    else:
        st.write("The 'pts' or 'team' columns are missing in the dataset.")
